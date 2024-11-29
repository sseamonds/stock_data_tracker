import rds_functions as rf
import logging

# Configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}

logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def get_nav_metrics_from_df(calc_df):
    nav_discount_avg_1y = calc_df.tail(1)['nav_discount_premium_moving_avg_1yr'][0]
    nav_discount_avg_alltime = round(calc_df['nav_discount_premium'].mean(), 4)
    
    return nav_discount_avg_1y,nav_discount_avg_alltime


def check_current_cef_discount(stock:str, curr_prem_disc:float, 
                               user_name:str, password:str, rds_host:str, db_name:str):
    '''
    Validate current premium/discount for a stock against its 1 year and all time averages
    '''
    stock_info = rf.get_metrics_by_stock(stock, user_name, password, rds_host, db_name)
    logger.debug(f'{stock_info=}')

    if curr_prem_disc:
        if stock_info:
            if curr_prem_disc < 0 and stock_info['nav_discount_avg_1y'] > curr_prem_disc:
                logger.info(f'Discount for {stock} of {curr_prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_avg_1y']}')
            if curr_prem_disc < 0 and stock_info['nav_discount_avg_alltime'] > curr_prem_disc:
                logger.info(f'Discount for {stock} of {curr_prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_avg_alltime']}')
        else:
            logger.error(f'Error getting stock info for {stock}')
    else:
        logger.error(f'Error getting premium/discount for {stock}')