from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import  sessionmaker


engine = create_engine('sqlite:///example.db')
session_factory = sessionmaker(engine)
Base = declarative_base()
