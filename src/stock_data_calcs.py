import numpy as np
import pandas as pd


def calculate_hist_metrics(df: pd.DataFrame):
    """
    Calculate and persist metrics from history dataset (dividends, splits, volume, etc).

    :return: DataFrame with calculated metrics
    """
    return_df = df.copy()

    # div yield
    div_multiplier = 4  # in the future, this will be calculated based on distribution schedule or provided as an arg
    return_df['div_yield'] = np.round(return_df['dividends_filled'].div(return_df['closing_price']) * div_multiplier, 4)
    return_df['div_yield_mvg_avg_1yr'] = np.round(return_df['div_yield'].rolling(260, min_periods=1).mean(), 4)
    return_df['div_yield_mvg_avg_max'] = np.round(return_df['div_yield'].mean(), 4)

    return return_df

def calculate_stock_metrics(df: pd.DataFrame):
    """
    Calculate and persist metrics.

    :return: DataFrame with calculated metrics
    """
    return_df = df.copy()
    # 20, 60, 200 day moving averages
    return_df['price_moving_avg_20'] = np.round(return_df['closing_price'].rolling(20, min_periods=1).mean(), 2)
    return_df['price_moving_avg_60'] = np.round(return_df['closing_price'].rolling(60, min_periods=1).mean(), 2)
    return_df['price_moving_avg_1yr'] = np.round(return_df['closing_price'].rolling(260, min_periods=1).mean(), 2)

    return return_df


def calculate_cef_metrics(df: pd.DataFrame):
    """
    Calculate and persist metrics.

    :return: DataFrame with calculated metrics
    """
    return_df = df.copy()
    
    # price metrics
    return_df['price_moving_avg_20'] = np.round(return_df['closing_price'].rolling(20, min_periods=1).mean(), 2)
    return_df['price_moving_avg_60'] = np.round(return_df['closing_price'].rolling(60, min_periods=1).mean(), 2)
    return_df['price_moving_avg_1yr'] = np.round(return_df['closing_price'].rolling(260, min_periods=1).mean(), 2)

    # nav metrics
    return_df['nav_discount_premium'] = return_df.apply(lambda r: round((r.closing_price-r.nav)/r.nav, 4), axis=1)
    return_df['nav_discount_premium_moving_avg_1yr'] = np.round(return_df['nav_discount_premium'].rolling(260, min_periods=1).mean(), 4)

    return_df['nav_moving_avg_20'] = np.round(return_df['nav'].rolling(20, min_periods=1).mean(), 2)
    return_df['nav_moving_avg_60'] = np.round(return_df['nav'].rolling(60, min_periods=1).mean(), 2)
    return_df['nav_moving_avg_1yr'] = np.round(return_df['nav'].rolling(260, min_periods=1).mean(), 2)
    return_df['nav_avg_alltime'] = np.round(return_df['nav'].mean(), 2)

    return return_df



