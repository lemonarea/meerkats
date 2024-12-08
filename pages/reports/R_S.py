import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# local imports
from wofofiles.df_src import returns_report
from wofofiles.globfuncs import format_value


# Returns Report
def R_S00001():

    df_1 = returns_report()
    
    # Mock function to simulate data retrieval
    def fetch_data():
        time.sleep(2)  # Simulate a delay
        return df_1

    # Caching function with TTL (time-to-live)
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_data():
        return fetch_data()

    if st.sidebar.button("Fetch New Data"):
        with st.spinner("Fetching new data..."):
            data = fetch_data()  # Fetch directly without cache
        st.success("New data fetched!")
    else:
        with st.spinner("Retrieving cached data..."):
            data = get_data()  # Retrieve cached data

    # Filters

    col1, col2, col3 = st.columns([6, 2, 2])
    # col1 select box filter for StoreName

    with col1:
        # Report title
        st.title("Returns Report")

    with col2:
        selected_store = st.selectbox("Store Name", df_1['StoreName'].unique())

    with col3:    
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp(df_1['TransactionDate'].min()).to_pydatetime(), pd.Timestamp(df_1['TransactionDate'].max()).to_pydatetime()),
            min_value=pd.Timestamp(df_1['TransactionDate'].min()).to_pydatetime(),
            max_value=pd.Timestamp(df_1['TransactionDate'].max()).to_pydatetime()
        )

    # Ensure 'TransactionDate' is in datetime format
    # Ensure 'TransactionDate' is in datetime format if it exists
    if 'TransactionDate' in data.columns:
        try:
            data['TransactionDate'] = pd.to_datetime(data['TransactionDate'], format="%d-%m-%Y", dayfirst=True)
        except Exception as e:
            st.error(f"Error converting 'TransactionDate' to datetime: {e}")
            return
    # Convert date_range to datetime64[ns] for comparison
    date_range = pd.to_datetime(date_range)

    # Apply filters to the data
    filtered_data = data[(data['StoreName'] == selected_store) & 
                         (data['TransactionDate'] >= date_range[0]) & 
                         (data['TransactionDate'] <= date_range[1])]

    # Calculate the total sales and returns
    Total_Sales = (filtered_data['SalesPrice'] - filtered_data['DiscountValue']) * filtered_data['SalesQuantity']
    Total_Sales_Sum = Total_Sales.sum()
    Total_Return = (filtered_data['SalesPrice'] - filtered_data['DiscountValue']) * filtered_data['ReturnQuantity']
    Total_Return_Sum = Total_Return.sum()
    Return_Rate = (Total_Return_Sum / Total_Sales_Sum) * 100
    Return_Rate = "{:.1f}".format(Return_Rate)

    st.write(f"Total Sales Sum: {format_value(Total_Sales_Sum)}")
    st.write(f"Total Return Sum: {format_value(Total_Return_Sum)}")
    st.write(f"Return Rate: {Return_Rate}%")

    # Function to calculate return rate
    def calculate_return_rate(group_by_column):
        group_by = filtered_data.groupby(group_by_column)
        sales_value = group_by.apply(lambda x: ((x['SalesPrice'] - x['DiscountValue']) * x['SalesQuantity']).sum())
        return_value = group_by.apply(lambda x: ((x['SalesPrice'] - x['DiscountValue']) * x['ReturnQuantity']).sum())
        return_rate = (return_value / sales_value) * 100
        return_rate = return_rate.fillna(0).round(1).astype(str) + '%'
        return sales_value, return_value, return_rate

    # Function to create result DataFrame
    def create_result_df(sales_value, return_value, return_rate):
        result_df = pd.DataFrame({
            'Total Sales': sales_value.apply(format_value),
            'Total Returns': return_value.apply(format_value),
            'Return Rate': return_rate
        })
        total_sales_sum = sales_value.sum()
        total_returns_sum = return_value.sum()
        total_return_rate = (total_returns_sum / total_sales_sum) * 100
        total_return_rate = "{:.1f}%".format(total_return_rate)
        total_row = pd.DataFrame({
            'Total Sales': [format_value(total_sales_sum)],
            'Total Returns': [format_value(total_returns_sum)],
            'Return Rate': [total_return_rate]
        }, index=['Total'])
        result_df = pd.concat([result_df, total_row])
        return result_df

    st.write("### Who Returns More?")

    with st.expander("**Customer-wise Analysis**", expanded=False):
        # Calculate and display return rate per customer
        customer_sales_value, customer_return_value, customer_return_rate = calculate_return_rate('CustomerName')
        customer_result_df = create_result_df(customer_sales_value, customer_return_value, customer_return_rate)
        
        col1, col2 = st.columns([0.6, 0.4])

        with col1:
            st.dataframe(customer_result_df)

        with col2:
            # generate a pie chart by matplotlib for customer return rate "contribution of each customer to the total return rate"
            # filter zero return rate
            customer_return_value = customer_return_value[customer_return_value > 0]
            fig, ax = plt.subplots()
            ax.pie(customer_return_value, labels=customer_return_value.index, autopct='%1.1f%%')
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

    with st.expander("**User-wise Analysis**", expanded=False):
        # Calculate and display return rate per user
        user_sales_value, user_return_value, user_return_rate = calculate_return_rate('UserName')
        user_result_df = create_result_df(user_sales_value, user_return_value, user_return_rate)
        st.dataframe(user_result_df)

    with st.expander("**Item-wise Analysis**", expanded=False):
        # Calculate and display return rate per item name
        group_by_item = filtered_data.groupby('ItemNameEn')
        item_sales_qty = group_by_item['SalesQuantity'].sum()
        item_return_qty = group_by_item['ReturnQuantity'].sum()
        non_zero_return_mask = item_return_qty > 0
        item_sales_qty = item_sales_qty[non_zero_return_mask]
        item_return_qty = item_return_qty[non_zero_return_mask]
        item_return_rate = (item_return_qty / item_sales_qty) * 100
        item_return_rate = item_return_rate.fillna(0).round(1).astype(str) + '%'
        item_result_df = pd.DataFrame({
            'Total Sales Quantity': item_sales_qty,
            'Total Return Quantity': item_return_qty,
            'Return Rate': item_return_rate
        })
        total_item_sales_qty = item_sales_qty.sum()
        total_item_return_qty = item_return_qty.sum()
        total_item_return_rate = (total_item_return_qty / total_item_sales_qty) * 100
        total_item_return_rate = "{:.1f}%".format(total_item_return_rate)
        total_item_row = pd.DataFrame({
            'Total Sales Quantity': [total_item_sales_qty],
            'Total Return Quantity': [total_item_return_qty],
            'Return Rate': [total_item_return_rate]
        }, index=['Total'])
        item_result_df = pd.concat([item_result_df, total_item_row])

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Return Rate / Item Name")
            st.dataframe(item_result_df)

        with col2:
            st.write("### Return Rate / Group Name")
            # Calculate and display return rate per group name
            group_sales_value, group_return_value, group_return_rate = calculate_return_rate('GroupName')
            group_result_df = create_result_df(group_sales_value, group_return_value, group_return_rate)
            st.dataframe(group_result_df)

    with st.expander("**Days-wise Analysis**", expanded=False):
        st.write("Return Rate / Day")

def R_S00002():
    st.write("## Report 2 Overview")
    st.write("This is the Report 2 overview.")
    st.write("It contains the Report 2 data.")
