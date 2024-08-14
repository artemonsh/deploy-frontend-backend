from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


DB_HOST='localhost'
DB_PORT='5432'
DB_NAME='mydb'
DB_USER='postgres'
DB_PASS='0078927necid89'

print("None" if DB_PORT is None else str(DB_PORT))