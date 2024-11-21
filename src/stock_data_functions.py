import yfinance as yf
import logging
import stock_functions as sf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def stock_cef(stock_symbol):
    return yf.Ticker('X' + stock_symbol + 'X')


def get_current_cef_discount(stock_symbol):
    """
    Pull current stock data for symbol and return the date of the most recent data point
    """
    try:
        stock = yf.Ticker(stock_symbol)
        cef_stock = stock_cef(stock_symbol)
        
        previous_close = stock.fast_info['previousClose']
        previous_nav = cef_stock.fast_info['regularMarketPreviousClose']
        logger.info(f'{previous_close=}')
        logger.info(f'{previous_nav=}')

        return round(sf.get_premium_discount(previous_close, previous_nav),4)
    except Exception as e:
        logger.error(f'Error getting premium/discount for {stock_symbol}.\n{previous_close=}, {previous_nav=}\n{e}')
        return None