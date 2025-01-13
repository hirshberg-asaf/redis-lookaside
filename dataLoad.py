import psycopg2
import csv

# Define the connection parameters
dbname = 'movies'
user = 'admin'
password = 'admin'
host = 'localhost'
port = '5432'

# Establish a connection to Postgres
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("Connection successful")
except Exception as error:
    print(f"Error: {error}")

# Create movies table (if not exists)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title varchar(255),
        genre varchar(100),
        description TEXT,
        popularity  FLOAT
    );
""")

# Create movie_cast table (if not exists)
cur.execute("""
    CREATE TABLE IF NOT EXISTS movie_cast (
        movie_id INT REFERENCES movies(id) ON DELETE CASCADE,
        cast_members TEXT,  -- Renamed 'cast' to 'cast_members'
        PRIMARY KEY (movie_id)
    );
""")

# Open movies CSV and insert to tables
with open('data/movies.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row['original_title']
        genre = row['genres']
        popularity = float(row['popularity'])
        description = row['overview']
        cast = row['cast']  # Assuming the CSV has a column 'cast' with the list of actors

        # round popularity to 2 decimal
        popularity = round(popularity, 2)

        # Insert movie into the movies table
        query = """
                INSERT INTO movies (title, genre, description, popularity)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """
        values = (title, genre, description, popularity)
        cur.execute(query, values)
        movie_id = cur.fetchone()[0]  # Get the id of the inserted movie

        # Insert cast data into the movie_cast table
        query_cast = """
                INSERT INTO movie_cast (movie_id, cast_members)
                VALUES (%s, %s)
                """
        values_cast = (movie_id, cast)
        cur.execute(query_cast, values_cast)

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data inserted successfully.")
