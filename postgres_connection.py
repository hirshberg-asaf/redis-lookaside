import psycopg2
import logging
from fastapi import HTTPException

# PostgreSQL connection parameters
dbname = 'movies'
user = 'admin'
password = 'admin'
host = 'localhost'
port = '5432'

# Set up logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

def db_connection():
    """Function to establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        logger.debug("Connected to PostgreSQL.")
        return conn
    except Exception as error:
        logger.error(f"Database connection error: {error}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {error}")
