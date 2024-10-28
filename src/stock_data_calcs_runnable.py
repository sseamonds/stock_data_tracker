import argparse as ap
from stock_data_calcs import calculate_stock_metrics
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)


def parse_arg():
    """
    This function parses command line arguments to this script
    """
    parser = ap.ArgumentParser()

    parser.add_argument("--source_path", type=str, required=True)
    parser.add_argument("--dest_path", type=str, required=True)

    params = vars(parser.parse_args())

    return params


if __name__ == "__main__":
    args = parse_arg()
    source_path = args['source_path']
    dest_path = args['dest_path']

    calculate_stock_metrics(source_path, dest_path, logger, platform='local')
