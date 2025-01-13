import time
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from redis_connection import get_redis_connection
from postgres_connection import db_connection

# Set up logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Redis connection
r = get_redis_connection()

@app.get("/")
def read_root():
    """Root endpoint for the API."""
    return {"message": "Movie API"}

@app.get("/top_movies", response_model=List[dict])
def top_ten_movies():
    # Fetch the top 10 movies either from Redis cache or PostgreSQL.
    cache_key = "movies:top10"

    start_time_redis = time.time()
    cached_data = r.zrangebyscore(cache_key, "-inf", "+inf")
    if cached_data:
        redis_query_time = time.time() - start_time_redis
        logger.debug(f"Cache hit, time: {redis_query_time}")
        return [json.loads(item) for item in cached_data]

    # Fetch from the DB on cache miss
    start_time_psql = time.time()
    conn = db_connection()
    try:
        cur = conn.cursor()
        query = """
            SELECT title, popularity
            FROM movies
            ORDER BY popularity DESC
            LIMIT 10;
        """
        cur.execute(query)
        result = cur.fetchall()
        top10movies = [{"title": row[0], "score": row[1]} for row in result]

        # Cache the result in Redis with TTL of 10 minutes (600)
        redisPipeline = r.pipeline()
        for movie in top10movies:
            redisPipeline.zadd(cache_key, {json.dumps(movie): movie["score"]})

        redisPipeline.execute()
        r.expire(cache_key, 600)

        psql_query_time = time.time() - start_time_psql
        logger.debug(f"Cache miss, time: {psql_query_time}")

        return top10movies

    except Exception as error:
        logger.error(f"Database query failed: {error}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {error}")
    finally:
        conn.close() 
