import os 
from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()

pool = pooling.MySQLConnectionPool(
    pool_name="job_tracker_pool",
    pool_size=5,
    host=os.getenv("host", "localhost"),
    port=int(os.getenv("port", "3306")),
    user=os.getenv("user", "root"),
    password=os.getenv("password"),
    database=os.getenv("name", "job_tracker")
)

def get_db():
    return pool.get_connection()