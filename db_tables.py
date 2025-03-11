from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table, Date, Boolean, ForeignKey
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

# Konten table (Main account table)
konten = Table(
    "konten",
    metadata,
    Column("konto_id", Integer, primary_key=True, autoincrement=True),
    Column("erstellungsdatum", Date),
    Column("name", String),
    Column("bank", String),
    Column("typ", String),
    Column("kontostand", Float),
    Column("waehrung", String),
    Column("iban", String),
    Column("eigenes_konto", Boolean)  
)

# Kontostände table (Balances)
kontostaende = Table(
    "kontostaende",
    metadata,
    Column("kontostand_id", Integer, primary_key=True, autoincrement=True),
    Column("konto_id", Integer, ForeignKey("konten.konto_id", ondelete="CASCADE"), nullable=False),
    Column("datum", Date),
    Column("kontostand", Float),
    Column("waehrung", String)
)

# Transaktionen table (Transactions)
transaktionen = Table(
    "transaktionen",
    metadata,
    Column("transaktion_id", Integer, primary_key=True, autoincrement=True),
    Column("konto_id_incoming", Integer, ForeignKey("konten.konto_id", ondelete="CASCADE"), nullable=True),
    Column("konto_id_outgoing", Integer, ForeignKey("konten.konto_id", ondelete="CASCADE"), nullable=True),
    Column("art", String),
    Column("datum", Date),
    Column("betrag", Float),
    Column("beschreibung", String),
    Column("kategorie", String),
    Column("dauerauftrag", Boolean),
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

