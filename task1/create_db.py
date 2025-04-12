import psycopg2
import os

def create_db():
    conn = None  # Initialize conn to None
    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            database="task_1",
            port='5433',
            user="postgres",
            password="postgres",
        )
        conn.autocommit = True

        with conn.cursor() as cur:
            # Read the SQL script from the file
            with open("task_1/task_1.sql", "r") as f:
                sql = f.read()

            # Execute the SQL script to create the tables
            cur.execute(sql)

        print("Database and tables created successfully!")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while creating database: {error}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_db()
    
