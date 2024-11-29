import yfinance as yf
import argparse as ap
import logging


def get_yahoo_historical(stock_symbol, file_dest, period='1d'):
    """
    Pull specified history for symbol and save to dest_path
    Uses history function which adjusts closing price for splits and dividends.
    This dataset will be used for dividends, volume, splits, and volume data.

    :param stock_symbol:
    :param file_dest:
    :param period:

    :return:
    """
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=period)
    logger.info(f'Writing historical stock data for {stock_symbol} to {file_dest}')
    hist.to_parquet(file_dest, index=True)


def get_yahoo_price_data(stock_symbol, file_dest, period='1d'):
    """
    Pull closing price history using the download() method which does not
    adjust for dividends and splits, thus giving the actual price 
    for symbol and save to dest_path.

    When passing in a stock equity (VOO, AAPL, etc) or CEF stock symbol (ex. DSL or AWF), 
        this will return the unadjusted stock price in the Close field.
    When passing in a CEF alt symbol (ex. XDSLX or XAWFX), 
        this will return the NAV price in the Close field.

    :param stock_symbol:
    :param file_dest:
    :param period:

    :return:
    """
    price_df = yf.download(stock_symbol, period=period)
    logger.info(f'writing stock price data for {stock_symbol} to {file_dest}')
    price_df.to_parquet(file_dest, index=True)

def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--stock_symbol", type=str, required=True)
    parser.add_argument("--dest_path", type=str, required=True)
    parser.add_argument("--type", type=str, choices=['nav', 'price', 'hist'], required=True)
    parser.add_argument("--period", type=str, default='1d')

    params = vars(parser.parse_args())

    return params


if __name__ == '__main__':
    """
    command line args:
        --stock_symbol : symbol of stock whose data to pull from yfinance
        --dest_path : base path to write output file
        --period : (optional) yfinance arg defining the time period of data to pull
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    args = parse_arg()

    dest_path_arg = args['dest_path']
    period_arg = args.get('period')
    stock_symbol_arg = args['stock_symbol']
    type_arg = args['type']

    full_dest_path = f"{dest_path_arg}/{type_arg}/{stock_symbol_arg.replace("X","")}_{period_arg}.parquet"

    if type_arg == 'price' or type_arg == 'nav':
        get_yahoo_price_data(stock_symbol_arg,full_dest_path,period_arg)
    elif type_arg == 'hist':
        get_yahoo_historical(stock_symbol_arg,full_dest_path,period_arg)
    else:
        raise ValueError(f"Invalid type argument: {type_arg}")