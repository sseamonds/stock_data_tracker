import yfinance as yf
import logging

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def stock_cef(stock_symbol):
    return yf.Ticker('X' + stock_symbol + 'X')


def get_premium_discount(price, nav):
    if nav and nav != 0:
        return (price - nav) / nav
    else:
        raise Exception('Error getting premium/discount')


def get_current_cef_discount(stock_symbol:str) -> float:
    """
    Pull current stock data for symbol and return the date of the most recent data point
    """

    try:
        stock = yf.Ticker(stock_symbol)
        cef_stock = stock_cef(stock_symbol)
        previous_close = stock.fast_info['previousClose']
        previous_nav = cef_stock.fast_info['regularMarketPreviousClose']
        
        logger.debug(f'{stock_symbol=}, {previous_close=}, {previous_nav=}')

        return round(get_premium_discount(previous_close, previous_nav), 4)
    except Exception as e:
        logger.error(f'Error getting premium/discount for {stock_symbol}.\n{e}')
        return None