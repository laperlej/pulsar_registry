import psycopg2
import json

"""
SELECT id FROM galaxy_user where email = $1
INSERT INTO user_preference (user_id, name, value) VALUES ($1, $2, $3)

 id | user_id |          name          |                            value
----+---------+------------------------+-------------------------------------------------------------
  1 |       2 | extra_user_preferences | {"accp|pulsar_host": "test", "accp|pulsar_api_key": "test"}
"""
class Galaxy:
    def __init__(self, config):
        self.conn = psycopg2.connect(config.galaxy_database)

    def _upsert_user_preference(self, user, pulsar):
        value = json.dumps({
            "accp|pulsar_host": pulsar.url, 
            "accp|pulsar_api_key": pulsar.api_key})
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO user_preference (user_id, name, value) 
            VALUES (
                (SELECT id FROM galaxy_user WHERE email = %s), 
                %s, 
                %s
            )
            ON CONFLICT (user_id, name) DO UPDATE SET value = %s
        """, (
            user.email, 
            "extra_user_preferences",
            value
        ))
        self.conn.commit()

    def _remove_user_preference(self, user):
        cur = self.conn.cursor()
        cur.execute("""
            DELETE FROM user_preference WHERE user_id = (
                SELECT id FROM galaxy_user WHERE email = %s
            )
        """, (user.email))
        self.conn.commit()
    
    def update_pulsar(self, user, pulsar):
        try:
            self._upsert_user_preference(user, pulsar)
        except Exception as e:
            print(f"Failed to update pulsar for {user.email}: {e}")
    
    def remove_pulsar(self, user):
        try:
            self._remove_user_preference(user)
        except Exception as e:
            print(f"Failed to remove pulsar for {user.email}: {e}")
