# Python libraries
import os
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
from joblib import Memory
import datetime as dt

# Local imports
from wofofiles.conn import username, password, host, port, database


# Set up a directory for the cache
cache_dir = './cache'
memory = Memory(cache_dir, verbose=0)

# Define the caching function with expiration
def cache_with_expiry(func, expiry_minutes=10):
    def wrapper(*args, **kwargs):
        current_time = datetime.now()
        cache_file = os.path.join(cache_dir, func.__name__)
        if os.path.exists(cache_file):
            cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if (current_time - cache_time) < timedelta(minutes=expiry_minutes):
                return memory.cache(func)(*args, **kwargs)
            else:
                # Clear the old cache if expired
                memory.clear()
        return memory.cache(func)(*args, **kwargs)
    return wrapper

# Use your existing function but with caching
@cache_with_expiry
def dataset():
    query = """
    SELECT * FROM ownership

    """

    # Create the connection string and engine
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    
    # Execute the query and return the DataFrame
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df

# Now calling the function will use the cache if available and not expired
df = dataset()




def daily_transactions():

    # Import the data
    df = pd.read_excel('draft/data_sample.xlsx')
    df.drop(['TRNS_TYPE_CODE', 'TRNS_SERIAL', 'ITEM_NAME'], axis=1, inplace=True)
    df['CUSTOMER_NAME'].fillna('Walk-in', inplace=True)
    df['LIST_RATE'].fillna(0, inplace=True) 

    # rename columns
    df.rename(columns={
        'INVOICE_NO': 'TransactionNumber',
        'INVOICE_DATE': 'TransactionDate',
        'INVOICE_TIME': 'TransactionTime',
        'INSERT_USER': 'UserCode',
        'USER_NAME': 'UserName',
        'STORE_CODE': 'StoreCode',
        'STORE_NAME': 'StoreName',
        'CUSTOMER_CODE': 'CustomerCode',
        'CUSTOMER_NAME': 'CustomerName',
        'ITEM_GROUP_CODE': 'GroupCode',
        'GROUP_NAME': 'GroupName',
        'ITEM_CODE': 'ItemCode',
        'ITEM_NAME_E': 'ItemNameEn',
        'SALES_PRICE': 'SalesPrice',
        'DISC1_VALUE': 'DiscountValue',
        'SALES_QTY': 'SalesQuantity',
        'RETURN_QTY': 'ReturnQuantity',
        'LIST_RATE': 'ListRate',
        'EXPIRY_DATE': 'ExpiryDate',
        'THEMAR_CUST_MOBILE': 'CustomerMobile',
        'UNIT_COST': 'UnitCost'
    }, inplace=True)

    return df


def returns_report():
    # copy of daily transactions dataframe
    df = daily_transactions()
    # convert TransactionDate to datetime
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], format='%d-%m-%Y', dayfirst=True)
    # drop unnecessary columns
    df.drop(['UserCode', 'StoreCode', 'CustomerCode', 'GroupCode', 'ItemCode', 'CustomerMobile', 'UnitCost'], axis=1, inplace=True)

    return df

