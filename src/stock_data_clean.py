import pandas as pd
import numpy as np


def clean_hist_data(df: pd.DataFrame):
    return_df = df.copy()
    drop_cols = ["Open", "High", "Low", "Close"]
    return_df.drop(columns=set.intersection(set(drop_cols), set(return_df.columns)), inplace=True)
    return_df.index = pd.to_datetime(return_df.index.strftime('%Y-%m-%d'))

    # fill dividends to be the most recent distribution
    return_df.loc[df['Dividends'] == 0, ['Dividends']] = np.nan
    return_df['dividends_filled'] = return_df['Dividends'].bfill(inplace=False)
    return_df['dividends_filled'] = return_df['dividends_filled'].ffill(inplace=False)
    return_df.drop(columns=['Dividends'], inplace=True)  
    
    return return_df


def clean_price_data(df: pd.DataFrame):
    """
    Price and Div data from yahoo.
    Convert dates, rename cols, fill divs
    type: 'price' or 'nav'

    :return: None
    """
    return_df = df.copy()
    # only price from this dataset
    drop_cols = ['High', 'Low', 'Open', 'Adj Close', 'Volume']
    
    return_df.drop(columns=set.intersection(set(drop_cols), 
                                            set(df.columns)), 
                                            inplace=True)

    # Converting the original datetime to just a date.
    # For now there is no need for a timestamp, just a date
    return_df.index = pd.to_datetime(return_df.index.strftime('%Y-%m-%d'))
    return_df.rename(columns={"Close": "closing_price"}, inplace=True)      

    return return_df


def clean_cef_data(cef_price_df: pd.DataFrame, cef_nav_df: pd.DataFrame):
    cef_price_df_cleaned = clean_price_data(cef_price_df)
    
    # Path for CEF's with XnnnX format tickers (XDSLX, XAWFX, etc)
    # There will be a corresponding price dataset for each CEF, only nav for this dataset
    cef_nav_df_cleaned = clean_price_data(cef_nav_df)
    cef_nav_df_cleaned.rename(columns={"closing_price": "closing_nav"}, inplace=True)

    joined_df = cef_nav_df_cleaned.join(cef_price_df_cleaned, how='inner')
    joined_df.dropna(inplace=True)

    return joined_df