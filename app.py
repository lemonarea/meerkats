# import the libraries
import streamlit as st
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import sys
print(sys.executable)

# local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu
# import the database connection
from wofofiles.conn import username, password, host, port, database

# page config
st.set_page_config(
    page_title=get_app_title(),
    layout='centered',
    initial_sidebar_state="collapsed"
)

hide_st_style= """
<style>
#MainMenu {visability: hidden;}
footer {visability: hidden;}
header {visability: hidden;}
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Create a connection string for the MySQL database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# Create the SQLAlchemy engine to interact with the database
try:
    engine = create_engine(connection_string, echo=True)
except SQLAlchemyError as e:
    st.error(f"Failed to connect to the database: {e}")

# Hashing the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""
    st.session_state['user_code'] = None 

# Define the login action
def login_action():
    user_code = st.session_state['login_user_code']
    password = st.session_state['login_password']
    if user_code and password:
        hashed_password = hash_password(password)
        try:
            with engine.connect() as connection:
                # Query the user based on user_code and hashed password
                query = text("""
                    SELECT UserCode, UserName 
                    FROM users 
                    WHERE UserCode = :user_code AND Password = :password
                """)
                result = connection.execute(query, {'user_code': user_code, 'password': hashed_password}).fetchone()
                
                # Check if the user exists and credentials match
                if result:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = result.UserName
                    st.session_state['user_code'] = result.UserCode
                else:
                    st.error("Invalid credentials. Please try again.")
        except SQLAlchemyError as e:
            st.error(f"Failed to login: {str(e.__dict__['orig'])}")
    else:
        st.warning("Please enter both user code and password.")

# Define the logout action
def logout_action():
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""

# Login function
def login():
    st.title("Meerkat")
    
    # User login form with session state variables
    st.text_input("User Code", key='login_user_code')
    st.text_input("Password", type="password", key='login_password')
    
    # Login button with on_click callback
    st.button("**➜**", on_click=login_action)

# Display the sidebar 
def display_sidebar():

    with st.sidebar:

        # Display the user name in the sidebar
        st.write(f"**Welcome**, {st.session_state['user_name']}")

        # the main menu
        app_menu()
        
        # Add a logout button with on_click callback
        st.button("↙ logout", on_click=logout_action)

# Main function to control the app flow
def main():

    if st.session_state['logged_in']:

        # Show the sidebar and pages if logged in
        display_sidebar()
        
        # Center the image and welcome message
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.image('wofofiles/img/meerkat.jpg', width=250)
            st.title('Meerkat')
            st.markdown("<p style='color:#A79644; font-size:14px; font-weight:bold; text-align:left;'>Designed for monitoring and analyzing business data.</p>", unsafe_allow_html=True)
    else:
        # Show login form if not logged in
        login()


if __name__ == "__main__":
    main()

