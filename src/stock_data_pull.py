import yfinance as yf
import argparse as ap
import logging
import awswrangler as wr


def get_yahoo_historical(stock_symbol, file_dest, period='1d', file_type='csv'):
    """
    Pull specified history for symbol and save to dest_path

    :param stock_symbol:
    :param file_dest:
    :param period:

    :return:
    """
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period=period)
    
    logger.debug(f'hist : {hist}')
    logger.info(f'writing stock data for {stock_symbol} to {file_dest}')

    if file_type == 'csv':
        hist.to_csv(file_dest, index=True)
    else:
        hist.to_parquet(file_dest, index=True)


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--stock_symbol", type=str, required=True)
    parser.add_argument("--dest_path", type=str, required=True)
    parser.add_argument("--period", type=str, default='1d')
    parser.add_argument("--file_type", type=str, choices=['csv', 'parquet'], default='parquet')

    params = vars(parser.parse_args())

    return params

if __name__ == '__main__':
    """
    command line args:
        --stock_symbol : symbol of stock whose data to pull from yfinance
        --dest_path : base path to write output file
        [--period] : yfinance arg defining the time period of data to pull
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    args = parse_arg()

    dest_path_arg = args['dest_path']
    period_arg = args.get('period', '1d')
    stock_symbol_arg = args['stock_symbol']
    file_type_arg = args['file_type']

    full_dest_path = f"{dest_path_arg}/{stock_symbol_arg}_{period_arg}_historical.{file_type_arg}"

    get_yahoo_historical(stock_symbol_arg,
                         full_dest_path,
                         period_arg,
                         args['file_type'])
