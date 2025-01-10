import logging
from stock_alerts import alert
from rds_functions import get_current_metrics_by_stock

# configure logging
default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s : %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
logger = logging.getLogger(__name__)


def get_current_nav_metrics_from_df(calc_df) -> tuple:
    """Get latest metrics from calc_df"""
    nav_discount_premium_avg_1yr = calc_df.tail(1)['nav_discount_premium_avg_1yr'].iloc[0]
    nav_discount_premium_avg_max = round(calc_df['nav_discount_premium'].mean(), 4)
    
    return nav_discount_premium_avg_1yr, nav_discount_premium_avg_max


def check_current_cef_discount(stock:str, 
                               curr_prem_disc:float, 
                               db_params:dict,
                               alert_mode:str='LOG'):
    '''
    Validate current premium/discount for a stock against its 1 year and all time averages
    '''
    stock_info = get_current_metrics_by_stock(stock, db_params=db_params)
    logger.debug(f'{stock_info=}')

    messages = []

    if curr_prem_disc:
        if stock_info:
            if curr_prem_disc < 0 and stock_info['nav_discount_premium_avg_1yr'] > curr_prem_disc:
                messages.append(f'Discount for {stock} of {curr_prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_premium_avg_1yr']}')
            if curr_prem_disc < 0 and stock_info['nav_discount_premium_avg_max'] > curr_prem_disc:
                messages.append(f'Discount for {stock} of {curr_prem_disc} has exceeded its 1 year average of {stock_info['nav_discount_premium_avg_max']}')
        else:
            raise Exception(f'Error getting stock info for {stock}')
    else:
        raise Exception(f'Received empty premium/discount for {stock}')
    
    if len(messages) > 0:
        alert(alert_mode, messages)
