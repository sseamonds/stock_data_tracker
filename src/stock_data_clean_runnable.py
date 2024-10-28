import argparse as ap
import logging
from stock_data_clean import clean_stock_data


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--source_path", type=str, required=True)
    parser.add_argument("--dest_path", type=str, required=True)

    params = vars(parser.parse_args())

    return params

"""
Local script to run clean stock data
"""
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    args = parse_arg()
    source_path = args['source_path']
    dest_path = args['dest_path']

    clean_stock_data(source_path, dest_path, logger, platform='local')