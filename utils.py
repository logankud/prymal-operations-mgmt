
import psycopg2
import os


def get_db_connection():
  """
  Returns a new psycopg2 connection to the Replit-hosted Postgres database.
  """
  conn = psycopg2.connect(
      host=os.environ.get("PGHOST", "localhost"),
      database=os.environ.get("PGDATABASE", "replitdb"),
      user=os.environ.get("PGUSER", "user"),
      password=os.environ.get("PGPASSWORD", "password")
  )
  return conn


def load_sql_file(filename: str) -> str:
  """
  Loads a SQL file from the specified filename.
  """
  base_path = os.path.dirname(os.path.abspath(__file__))
  sql_path = os.path.join(base_path, filename)
  with open(sql_path, "r", encoding="utf-8") as f:
      return f.read()