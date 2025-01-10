'''Functions for interacting with RDS tables.'''
import logging
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, MetaData

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def save_stock_history(df: pd.DataFrame, symbol: str, db_params: dict) -> bool:
    # Use SQLAlchemy's insert with on_conflict_do_update to upsert historical stock data
    try:
        logger.debug(f"Upserting data for symbol: {symbol}")
        engine = create_engine(f'postgresql://{db_params["user_name"]}:{db_params["password"]}@{db_params["rds_host"]}/{db_params["db_name"]}')

        df['symbol'] = symbol
        df.reset_index(inplace=True)
        df.rename(columns={'Date': 'record_date'}, inplace=True)

        metadata = MetaData()
        table = Table('stock_history', metadata, autoload_with=engine)
        insert_stmt = insert(table).values(df.to_dict(orient='records'))
        update_dict = {col: insert_stmt.excluded[col] for col in df.columns if col not in ['record_date', 'symbol']}

        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['record_date', 'symbol'],
            set_=update_dict
        )

        with engine.connect() as conn:
            conn.execute(upsert_stmt)
            conn.commit()
        
        logger.info(f"Upsert completed for symbol: {symbol}")
        return True
    except Exception as error:
        logger.error(f"An error occurred upserting stock history: {error}")
        return False


def get_stock_history(symbol: str, db_params: dict) -> pd.DataFrame:
    # Get stock price/nav/etc history from stock_history table, return a dataframe 
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=db_params["rds_host"],
            user=db_params["user_name"],
            password=db_params["password"],
            database=db_params["db_name"])

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM stock_history WHERE symbol = %s", (symbol,))
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=colnames)
        df.set_index('record_date', inplace=True)

        return df
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return None
    except Exception as error:
        logger.error(f"An error occurred querying : {error}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_stock_metrics_history(symbol: str, db_params: dict) -> pd.DataFrame:
    # Get stock metrics history from stock_metrics_history table, return a dataframe 
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=db_params["rds_host"],
            user=db_params["user_name"],
            password=db_params["password"],
            database=db_params["db_name"])

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM stock_metrics_history WHERE symbol = %s", (symbol,))
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=colnames)
        df.set_index('record_date', inplace=True)

        return df
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return None
    except Exception as error:
        logger.error(f"An error occurred querying : {error}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def save_stock_metrics_history(df: pd.DataFrame, db_params: dict) -> bool:
    # Upsert stock_metrics_history for a single stock
    try:
        engine = create_engine(f'postgresql://{db_params["user_name"]}:{db_params["password"]}@{db_params["rds_host"]}/{db_params["db_name"]}')

        # feels hacky, but don't see how to match a nameless DF index to a table index.  
        # to_sql allows this with index_label, but we want to allow for upserts
        df.reset_index(inplace=True)
        df.rename(columns={'Date': 'record_date'}, inplace=True)

        metadata = MetaData()
        table = Table('stock_metrics_history', metadata, autoload_with=engine)
        insert_stmt = insert(table).values(df.to_dict(orient='records'))
        update_dict = {col: insert_stmt.excluded[col] for col in df.columns if col not in ['record_date', 'symbol']}

        logger.info(f"update_dict: {update_dict}")
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['record_date', 'symbol'],
            set_=update_dict
        )

        with engine.connect() as conn:
            conn.execute(upsert_stmt)
            conn.commit()
        
        logger.info(f"Upsert completed for metrics history of symbol")
        return True
    except Exception as error:
        logger.error(f"An error occurred upserting stock metrics history: {error}")
        return False
 

def get_current_metrics_by_stock(symbol: str, db_params: dict) -> dict:
    col1 = "nav_discount_premium_avg_1yr"
    col2 = "nav_discount_premium_avg_max"
    table_name = "current_stock_metrics"

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=db_params["rds_host"],
            user=db_params["user_name"],
            password=db_params["password"],
            database=db_params["db_name"]
        )
        
        cur = conn.cursor()
        cur.execute(f"SELECT {col1}, {col2} FROM {table_name} WHERE symbol = %s", (symbol,))
        rows = cur.fetchall()

        return {col1: rows[0][0], col2: rows[0][1]}
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return None
    except Exception as error:
        logger.error(f"An error occurred querying : {error}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def save_current_stock_metrics(symbol: str, 
                               nav_discount_premium_avg_1yr: float, 
                               nav_discount_premium_avg_max: float, 
                               db_params: dict) -> bool:
    """Upsert latest stock metrics to current_stock_metrics table"""
    conn = None
    cur = None

    try:
        existing_metrics = get_current_metrics_by_stock(symbol, db_params)
        if existing_metrics:
            conn = psycopg2.connect(
                host=db_params["rds_host"],
                user=db_params["user_name"],
                password=db_params["password"],
                database=db_params["db_name"]
            )

            cur = conn.cursor()
            sql_update = """
                UPDATE current_stock_metrics
                SET nav_discount_premium_avg_1yr = %s, nav_discount_premium_avg_max = %s
                WHERE symbol = %s
            """
            cur.execute(sql_update, (nav_discount_premium_avg_1yr, nav_discount_premium_avg_max, symbol))
            conn.commit()
            logger.info(f"Record updated for symbol: {symbol}")
        else:
            conn = psycopg2.connect(
                host=db_params["rds_host"],
                user=db_params["user_name"],
                password=db_params["password"],
                database=db_params["db_name"]
            )

            cur = conn.cursor()
            current_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            sql_insert = """
                INSERT INTO current_stock_metrics (symbol, nav_discount_premium_avg_1yr, nav_discount_premium_avg_max, last_updated)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql_insert, (symbol, nav_discount_premium_avg_1yr, nav_discount_premium_avg_max, current_time))
            conn.commit()
            logger.info(f"Record inserted for symbol: {symbol}")
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return False
    except Exception as error:
        logger.error(f"An error occurred inserting/updating: {error}")
        return False
    finally:
        if conn:
            conn.close()
        if cur:
            cur.close()

    return True
