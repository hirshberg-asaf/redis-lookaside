import redis
import logging

# Redis connection parameters
redisHost: str = 'localhost'
redisPort: int = 6379
redisDB: int = 0

# Set up logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

def get_redis_connection() -> redis.Redis:
    """Function to get a Redis connection."""
    try:
        r = redis.Redis(host=redisHost, port=redisPort, db=redisDB)
        # Verify connection (optional)
        if r.ping():
            logger.debug("Connected to Redis.")
        return r
    except Exception as error:
        logger.error(f"Error connecting to Redis: {error}")
        raise error
