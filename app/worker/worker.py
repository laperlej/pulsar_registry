import threading
from sqlalchemy import select
import time
import datetime
from models.model import Outbox, Pulsar, User

class EmptyOutboxException(Exception):
    pass

class Worker(threading.Thread):
    def __init__(self, app, galaxy):
        super().__init__(daemon=True)  # Daemon thread will exit when the main thread does
        self.app = app
        self.galaxy = galaxy
        self.stop_event = threading.Event()  # Event to signal when to stop
        self.sleep_time = 1  # Time to sleep between tasks

    def run(self):
        while not self.stop_event.is_set():  # Keep running until stop_event is set
            time.sleep(60)  # Sleep for a bit
            try:
                with self.app.state.db.get_session() as session:
                    tasks = self._get_tasks(session)
                    for task in tasks:
                        try:
                            self._process_task(session, task)
                            self._mark_task_complete(task)
                        except:
                            print(f"Failed to process task: {task}")
                    session.commit()
            except EmptyOutboxException:
                continue  # No task available, loop again

    def _get_tasks(self, session):
        # Implement your task retrieval logic here
        result = session.execute(select(Outbox).where(Outbox.deleted_at == None).order_by(Outbox.id))
        tasks = result.scalars().all()
        if len(tasks) == 0:
            raise EmptyOutboxException("No tasks available")
        return tasks


    def _process_task(self, session, task):
        print(f"Processing task: {task}")
        result = session.query(Pulsar).filter().order_by(Pulsar.id).limit(1)
        pulsar = result.scalar_one_or_none()
        user = session.query(User).filter(User.id == task.user_id).one()
        if pulsar is None:
            self.galaxy.remove_pulsar(user)
        else:
            self.galaxy.update_pulsar(user, pulsar)

    def _mark_task_complete(self, task):
        # Soft delete the task from the database
        task.deleted_at = datetime.datetime.now()

    def stop(self):
        self.stop_event.set()  # Signal to stop
