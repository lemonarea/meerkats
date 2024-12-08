import streamlit as st
import pandas as pd
import openai

# local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu
# import the database connection

# import the data from the xlsx file from drafts folder
df = pd.read_excel('draft/data_sample.xlsx')
# remove the columns that are not needed TRNS_TYPE_CODE, TRNS_SERIAL, INSERT_USER, STORE_CODE, CUSTOMER_CODE, ITEM_GROUP_CODE, ITEM_CODE, ITEM_NAME
df.drop(['TRNS_TYPE_CODE', 'TRNS_SERIAL', 'INSERT_USER', 'STORE_CODE', 'CUSTOMER_CODE', 'ITEM_GROUP_CODE', 'ITEM_CODE', 'ITEM_NAME'], axis=1, inplace=True)
# fill null values with "Walk-in" in the column CUSTOMER_NAME
df['CUSTOMER_NAME'].fillna('Walk-in', inplace=True)
# fill null values with 0 in the column LIST_RATE
df['LIST_RATE'].fillna(0, inplace=True) 

# Streamlit App Layout
st.title("Streamlit App with ChatGPT API Integration")

st.subheader("DataFrame")
#st.dataframe(df)

# Input Section
st.subheader("Query ChatGPT")
query = st.text_area("Enter your query related to the DataFrame or anything else:")

if st.button("Send Query"):
    if query.strip():
        with st.spinner("Processing your query..."):
            try:
                # Send the query to ChatGPT
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o",  # Specify the model version
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Here's the data: {df.to_dict()}. {query}"}
                    ],
                    max_tokens=150
                )

                # Extract and display the response
                chat_response = response.choices[0].message.content.strip()
                st.success("Response from ChatGPT:")
                st.write(chat_response)

            except openai.APIError as e:
                if "insufficient_quota" in str(e):
                    st.error("OpenAI API quota exceeded. Please check your billing details or try again later.")
                else:
                    st.error(f"An error occurred with the OpenAI API: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a query before clicking the button.")



# Display the MAC page if this script is run
def main():
    # Check if the user is logged in
    if st.session_state.get('logged_in'):

        # Sidebar with navigation options
        with st.sidebar:
            st.write(f"Welcome, {st.session_state['user_name']}!")
            # the main menu
            app_menu()

    else:
        st.warning("You must log in to access this page.")
        st.stop()  # Stops execution if not logged in

if __name__ == "__main__":
    main()

