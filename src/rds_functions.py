'''Functions for interacting with RDS tables.'''
import logging
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def get_current_metrics_by_stock(stock: str, db_params: dict) -> dict:
    col1 = "nav_discount_avg_1y"
    col2 = "nav_discount_avg_alltime"
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
        cur.execute(f"SELECT {col1}, {col2} FROM {table_name} WHERE stock = %s", (stock,))
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


def upsert_stock_metrics(stock: str, nav_discount_avg_1y: float, nav_discount_avg_alltime: float, db_params: dict) -> bool:
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
        sql_string = """
            INSERT INTO stock_metrics (stock, nav_discount_avg_1y, nav_discount_avg_alltime)
            VALUES (%s, %s, %s)
        """
        logger.debug(f"sql_string: {sql_string}")

        cur.execute(sql_string, (stock, nav_discount_avg_1y, nav_discount_avg_alltime))
        conn.commit()
        logger.info(f"Record inserted for stock: {stock}")
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return False
    except Exception as error:
        logger.error(f"An error occurred inserting : {error}")
        return False
    finally:
        if conn:
            conn.close()
        if cur:
            cur.close()

    return True


def upsert_stock_metrics(stock: str, nav_discount_avg_1y: float, nav_discount_avg_alltime: float, db_params: dict) -> bool:
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
        sql_string = """
            INSERT INTO stock_metrics (stock, nav_discount_avg_1y, nav_discount_avg_alltime)
            VALUES (%s, %s, %s)
        """
        logger.debug(f"sql_string: {sql_string}")

        cur.execute(sql_string, (stock, nav_discount_avg_1y, nav_discount_avg_alltime))
        conn.commit()
        logger.info(f"Record inserted for stock: {stock}")
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return False
    except Exception as error:
        logger.error(f"An error occurred inserting : {error}")
        return False
    finally:
        if conn:
            conn.close()
        if cur:
            cur.close()

    return True


def insert_stock_history(df: pd.DataFrame, symbol: str, db_params: dict) -> bool:
    try:
        logger.debug(f"Inserting data for symbol: {symbol}")
        engine = create_engine(f'postgresql://{db_params["user_name"]}:{db_params["password"]}@{db_params["rds_host"]}/{db_params["db_name"]}')
        logger.info(f"engine: {engine}")
        df['symbol'] = symbol
        
        num_rows = df.to_sql('stock_history', engine, if_exists='append', 
                  index_label='record_date')
        logger.info(f"{num_rows} rows inserted for symbol: {symbol}")
        
        return True
    except Exception as error:
        logger.error(f"An error occurred inserting stock history: {error}")
        return False
