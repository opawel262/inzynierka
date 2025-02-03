from app.core.config import settings
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

connection_engine = None

while connection_engine is None:
    try:
        connection_engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL, connect_args={}
        )
    except Exception as e:
        print(f"Error occured when trying to connect to database:\n\n{e}")

        print(f"Retrying in 3s...")
        sleep(3)

engine = connection_engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
