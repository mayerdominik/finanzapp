from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table, Date
import dotenv
import os

# load credentials from .env file
dotenv.load_dotenv()

# get credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create a connection to the database
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Create metadata object
metadata = MetaData()

# # Define tables (sample tables here, ids should be strings)
# table1 = Table(
#     "stock_data",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("stock_code", String),
#     Column("date", String),
#     Column("open", Float),
#     Column("high", Float),
#     Column("low", Float),
#     Column("close", Float),
#     Column("volume", Float)
# )

# table2 = Table(
#     "stock_info",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("stock_code", String),
#     Column("name", String),
#     Column("sector", String),
#     Column("industry", String)
# )
konten = Table(
    "konten",
    metadata,
    Column("konto_id", Integer, primary_key=True, autoincrement=True),
    Column("erstellungsdatum", Date),
    Column("name", String),
    Column("bank", String),
    Column("typ", String),
    Column("kontostand", Float),
    Column("waehrung", String)
)

def create_all_tables():
    '''Creates all tables listed above, if not existent yet use with caution'''
    try:
        metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
                        
def delete_all_tables():
    '''Deletes all tables listed above, use with caution'''
    try:
        metadata.drop_all(engine)
    except Exception as e:
        print(f"Error deleting tables: {e}")

if __name__ == "__main__":

    # Create tables in the database
    create_all_tables()

