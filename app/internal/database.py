from .config import AppConfig
from sqlalchemy import create_engine
from models.model import Base
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

class Database:
    def __init__(self, config: AppConfig):
        self.in_memory = config.database.in_memory
        self.path = config.database.path
        self.debug = config.database.debug
        self.engine = None

    def _get_connection_string(self):
        if self.in_memory:
            return f"sqlite://"
        else:
            return f"sqlite:///{self.path}"

    def connect(self):
        self.engine =  create_engine(
            self._get_connection_string(),
            echo=self.debug,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine)
        return self

    def get_session(self) -> Session:
        if self.engine is None:
            raise Exception("Database not connected")
        return Session(self.engine)
