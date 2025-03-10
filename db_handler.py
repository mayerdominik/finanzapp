import psycopg2
import os
import dotenv
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import Session
import pandas as pd

# load DB credentials from .env file
dotenv.load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# for sqlalchemy create an engine
engine_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(engine_url)

def get_connection():
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        return conn
    except:
        print(f"Error connecting to database {database}")

def execute_statement(conn, statement):
    try:
        cur = conn.cursor()
        cur.execute(statement)
        conn.commit()
    except:
        print(f"Error executing statement {statement}")

def truncate_table(table_name):
    '''Truncates a table in the database'''
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"TRUNCATE TABLE {table_name};")
        conn.commit()
        conn.close()
        print(f"Table {table_name} successfully truncated")
    except Exception as e:
        print(f"Error truncating table {table_name}; {e}")


def df_to_db(df, table_name, safe_write=False, overwrite_db_in_conflict=False):
    '''Adds rows from a pandas DataFrame to a database table,
    optionally checking for primary key conflicts and overwriting rows in conflict, if specified'''
    try:
        # Dynamically create metadata and table object
        metadata = MetaData()  # Use the engine to bind metadata
        table = Table(table_name, metadata, autoload_with=engine)  # Dynamically load the table schema from the DB

        if not engine.dialect.has_table(engine.connect(), table_name):
            print(f"Table {table_name} does not exist")
            return
         
        with Session(engine) as session:
            
            # Conflict handling
            if safe_write:
                # Get the primary key columns 
                primary_key_columns = [col.name for col in table.primary_key.columns]
                # Get the primary key values in the DataFrame
                df_primary_key = set(tuple(row[col] for col in primary_key_columns) for index, row in df.iterrows())
                select_query = session.query(*[table.c[pk] for pk in primary_key_columns])
                # Fetch the existing primary key values from the table
                existing_keys = set(tuple(row) for row in select_query.all())
                conflicts = df_primary_key.intersection(existing_keys)

                if conflicts:
                    print(f"Found conflicts in the primary key columns: {primary_key_columns}: {conflicts}")
                    if overwrite_db_in_conflict:
                        # Delete rows from the table if overwrite_in_conflict is True
                        for pk in conflicts:
                            # Create a delete statement for each conflicting primary key
                            # session.execute(table.delete().where(tuple(table.c[pk] == value for pk, value in zip(table.primary_key.columns, pk))))
                            # Build the where clause for composite primary keys
                            where_clause = []
                            for idx, pk_value in enumerate(pk):
                                where_clause.append(table.c[table.primary_key.columns[idx].name] == pk_value)
                            
                            # Combine the conditions in the where clause using AND
                            where_condition = where_clause[0]
                            for condition in where_clause[1:]:
                                where_condition = where_condition & condition
                            
                            # Execute delete statement
                            session.execute(table.delete().where(where_condition))
                        session.commit()
                        print("Conflicting rows deleted from the table.")
                    else:
                        # Remove conflicts from the DataFrame if overwrite_in_conflict is False
                        df = df[~df.apply(lambda row: tuple(row[primary_key_columns]) in conflicts, axis=1)]
                        print("Conflicting rows removed from the DataFrame.")
            if df.empty:
                print("No data to write to the table.")
                return
            # convert DataFrame to list of dictionaries
            data_dicts = df.to_dict('records')
            # Add rows to the table
            session.execute(table.insert(), data_dicts)

            
            # Commit the transaction
            session.commit()
            print(f"DataFrame successfully written to database table {table_name}")

    except Exception as e:
        print(f"Error writing DataFrame to database table {table_name}; {e}")

def df_to_db_and_replace(df, table_name):
    '''Adds rows from a pandas DataFrame to a database table and replaces existing rows'''

    try:
        # first, check if the table exists
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        if not engine.dialect.has_table(engine.connect(), table_name):
            print(f"Table {table_name} does not exist")
            return

        with Session(engine) as session:
            # Clear all rows from the table before inserting new data
            session.execute(table.delete())  # Delete all rows
            session.commit()  # Commit the delete operation
            # convert DataFrame to list of dictionaries
            data_dicts = df.to_dict('records')
            # Add rows to the table
            session.execute(table.insert(), data_dicts)
            # Commit the transaction
            session.commit()
            print(f"DataFrame successfully written to database table {table_name} and replaced existing rows")

    except Exception as e:
        print(f"Error writing DataFrame to database table {table_name}; {e}")


def df_from_db(table_name):
    '''Fetches a table from the database and returns it as a pandas DataFrame'''
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)  # Automatically load the table schema from the DB
    
    # Query the table and fetch the results into a DataFrame
    query = table.select()  # Select all columns from the table
    df = pd.read_sql(query, engine)  # Use pandas to read the SQL result directly into a DataFrame
    return df

# if __name__ == "__main__":
#     # Test the connection
#     # conn = get_connection()
#     # print(conn)

#     # Test the truncate_table function
#     # truncate_table("stock_data")
#     # Test the df_to_db function

#     # example use
#     data = {
#         "erstellungsdatum": ["AAPL", "GOOGL", "MSFT"],
#         "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
#         "open": [100, 200, 300],
#         "high": [110, 210, 310],
#         "low": [90, 190, 290],
#         "close": [105, 205, 305],
#         "volume": [1000000, 2000000, 3000000]
#     }
#     df = pd.DataFrame(data)
#     df_to_db(df, "konten", safe_write=True, overwrite_db_in_conflict=True)
