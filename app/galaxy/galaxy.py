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

    def _get_user_preference(self, cur, user):
        print(f"Getting user preference for {user.email}")
        cur.execute("""
            SELECT * 
            FROM user_preference 
            WHERE user_id = (SELECT id FROM galaxy_user WHERE email = %s)
        """, [user.email])
        return cur.fetchone()
    
    def _update_user_preference(self, cur, user, pulsar):
        print(f"Updating user preference for {user.email}")
        value = json.dumps({
            "accp|pulsar_host": pulsar.url, 
            "accp|pulsar_api_key": pulsar.api_key})
        cur.execute("""
            UPDATE user_preference 
            SET value = %s 
            WHERE user_id = (SELECT id FROM galaxy_user WHERE email = %s)
        """, (
            value,
            user.email
        ))

    def _insert_user_preference(self, cur, user, pulsar):
        print(f"Inserting user preference for {user.email}")
        value = json.dumps({
            "accp|pulsar_host": pulsar.url, 
            "accp|pulsar_api_key": pulsar.api_key})
        cur.execute("""
            INSERT INTO user_preference (user_id, name, value) 
            VALUES (
                (SELECT id FROM galaxy_user WHERE email = %s), 
                %s, 
                %s
            )
        """, (
            user.email, 
            "extra_user_preferences",
            value
        ))

    def _upsert_user_preference(self, cur, user, pulsar):
        existing_preference = self._get_user_preference(cur, user)
        if existing_preference is None:
            self._insert_user_preference(cur, user, pulsar)
        else:
            self._update_user_preference(cur, user, pulsar)

    def _remove_user_preference(self, cur, user):
        print(f"Removing user preference for {user.email}")
        cur.execute("""
            DELETE FROM user_preference WHERE user_id = (
                SELECT id FROM galaxy_user WHERE email = %s
            )
        """, (user.email))
    
    def update_pulsar(self, user, pulsar):
        try:
            cur = self.conn.cursor()
            self._upsert_user_preference(cur, user, pulsar)
            self.conn.commit()
        except Exception as e:
            print(f"Failed to update pulsar for {user.email}: {e}")
    
    def remove_pulsar(self, user):
        try:
            cur = self.conn.cursor()
            self._remove_user_preference(cur, user)
            self.conn.commit()
        except Exception as e:
            print(f"Failed to remove pulsar for {user.email}: {e}")
