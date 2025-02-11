from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
import time
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@db:3306/patient_db"

# Add retry logic for database connection
max_retries = 5
retry_delay = 5

for retry in range(max_retries):
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        # Test the connection
        with engine.connect() as connection:
            print("Database connection successful!")
        break
    except OperationalError as e:
        if retry < max_retries - 1:
            print(f"Database connection attempt {retry + 1} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Could not connect to the database after several attempts.")
            raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()