import pandas as pd
import numpy as np


def clean_price_data(df: pd.DataFrame, type: str):
    """
    Price and Div data from yahoo.
    Convert dates, rename cols, fill divs
    type: 'price' or 'nav'

    :return: None
    """
    drop_cols = ['Capital Gains', 'High', 'Low', 'Open', 'Stock Splits']
    
    df.drop(columns=set.intersection(set(drop_cols), set(df.columns)), inplace=True)

    # Converting the original datetime to just a date.
    # For now there is no need for a timestamp, just a date
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d'))

    if type == 'price':
        df.rename(columns={"Close": "closing_price"}, inplace=True)
        # fill dividends to be the most recent distribution
        df.loc[df['Dividends'] == 0, ['Dividends']] = np.nan
        df['dividends_filled'] = df['Dividends'].bfill(inplace=False)
        df['dividends_filled'] = df['dividends_filled'].ffill(inplace=False)
        df.drop(columns=['Dividends'], inplace=True)
        
        df.rename(columns={"Volume": "volume"}, inplace=True)
    else:
        # there will be a corresponding price dataset for each CEF, 
        # so only nav for nav dataset
        df.drop(columns=['Volume', 'Dividends'], inplace=True)
        df.rename(columns={"Close": "nav"}, inplace=True)

    return df
