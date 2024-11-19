import numpy as np

def get_nav_metrics_from_df(calc_df):
    nav_discount_avg_1y = calc_df.tail(1)['nav_discount_premium_moving_avg_1yr'][0]
    nav_discount_avg_alltime = np.round(calc_df['nav_discount_premium'].mean(), 4)
    return nav_discount_avg_1y,nav_discount_avg_alltime