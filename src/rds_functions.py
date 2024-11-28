'''Functions for interacting with RDS tables.'''
import logging
import psycopg2

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def get_metrics_by_stock(stock, user_name, password, rds_host, db_name) -> dict:
    col1 = "nav_discount_avg_1y"
    col2 = "nav_discount_avg_alltime"
    table_name = "stock_metrics"

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=rds_host,
            user=user_name,
            password=password,
            database=db_name
        )
        
        cur = conn.cursor()
        cur.execute(f"SELECT {col1}, {col2} FROM {table_name} WHERE stock = '{stock}'")
        rows = cur.fetchall()

        return {col1: rows[0][0], col2: rows[0][1]}
    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {db_error}")
        return None
    except Exception as error:
        logger.error(f"An error occurred querying : {error}")
        if cur:
            cur.close()
        if conn:
            conn.close()
        if cur:
            cur.close()
        

def insert_stock_metrics(stock:str, nav_discount_avg_1y:float, nav_discount_avg_alltime:float, 
                         user_name:str, password:str, rds_host:str, db_name:str):
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            host=rds_host,
            user=user_name,
            password=password,
            database=db_name
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
    except Exception as error:
        logger.error(f"An error occurred inserting : {error}")
    finally:
        if conn:
            conn.close()
        if cur:
            cur.close()
