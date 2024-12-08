# import the libraries
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu
# import the database connection
from wofofiles.conn import username, password, host, port, database
# import the sales reports
import pages.reports.R_S as R_S
import inspect

# page config
st.set_page_config(
    page_title=get_app_title(),
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create the SQLAlchemy engine to interact with the database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string, echo=True)


# Function to check user access
def user_has_access(user_code, section_name):
    try:
        with engine.connect() as connection:
            # Check direct user access and group-based access
            result = connection.execute(text("""
                SELECT DISTINCT s.SectionName
                FROM access_control ac
                JOIN sections s ON ac.SectionCode = s.SectionCode
                WHERE (ac.UserCode = :user_code 
                      OR ac.GroupCode IN (
                          SELECT GroupCode 
                          FROM access_control 
                          WHERE UserCode = :user_code AND GroupCode IS NOT NULL
                      ))
                AND s.SectionName = :section_name
            """), {"user_code": user_code, "section_name": section_name})
            return result.fetchone() is not None
    except SQLAlchemyError as e:
        st.error(f"Error checking user access: {e}")
        return False

# Get the current user code (this should be set based on your authentication system)
current_user_code = st.session_state.get("user_code")

# Function to get all sections for a user
def get_user_sections(user_code):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT DISTINCT s.SectionName
                FROM access_control ac
                JOIN sections s ON ac.SectionCode = s.SectionCode
                WHERE ac.UserCode = :user_code 
                OR ac.GroupCode IN (
                    SELECT GroupCode 
                    FROM access_control 
                    WHERE UserCode = :user_code AND GroupCode IS NOT NULL
                )
            """), {"user_code": user_code})
            return [row[0] for row in result]
    except SQLAlchemyError as e:
        st.error(f"Error fetching user sections: {e}")
        return []

# Display sales report function
def display_sales_report():
    if user_has_access(current_user_code, "Sales"):
        try:
            with engine.connect() as connection:
                # Get report names with page-level permission check
                result = connection.execute(text("""
                    SELECT DISTINCT p.Pagename 
                    FROM pages p
                    JOIN access_control ac ON p.PageRef = ac.PageRef
                    WHERE p.PageRef LIKE 'R_S%'
                    AND (ac.UserCode = :user_code 
                        OR ac.GroupCode IN (
                            SELECT GroupCode 
                            FROM access_control 
                            WHERE UserCode = :user_code AND GroupCode IS NOT NULL
                        ))
                """), {"user_code": current_user_code})
                reports = [row[0] for row in result]
                
                # Create sidebar selection
                with st.sidebar:
                    st.title("Sales Department")
                    report = st.selectbox(
                        "**Select a report ⤵**",
                        [""] + reports,
                        index=0,
                        key="report_selectbox_1"
                    )

                # Get page references with permission check
                result = connection.execute(text("""
                    SELECT DISTINCT p.Pagename, p.PageRef
                    FROM pages p
                    JOIN access_control ac ON p.PageRef = ac.PageRef
                    WHERE p.PageRef LIKE 'R_S%'
                    AND (ac.UserCode = :user_code 
                        OR ac.GroupCode IN (
                            SELECT GroupCode 
                            FROM access_control 
                            WHERE UserCode = :user_code AND GroupCode IS NOT NULL
                        ))
                """), {"user_code": current_user_code})
                pagesidx = {row[0]: row[1] for row in result}
        except SQLAlchemyError as e:
            st.error(f"Error fetching reports: {e}")
            return

        # Get the page code for the selected report
        pagecode = pagesidx.get(report)

        # Get all functions from the R_S module
        report_functions = {}
        for name, obj in inspect.getmembers(R_S, inspect.isfunction):
            if name.startswith("R_S"):
                report_functions[name] = obj

        # Display the report based on the page code
        if pagecode and pagecode in report_functions:
            report_functions[pagecode]()
        else:
            st.warning("Please select a report from sidebar")



# Display the MAC page if this script is run
def main():
    # Check if the user is logged in
    if st.session_state.get('logged_in'):

        # Sidebar with navigation options
        with st.sidebar:
            st.write(f"Welcome, {st.session_state['user_name']}!")
            # the main menu
            app_menu()

        if current_user_code:
            user_sections = get_user_sections(current_user_code)
            if "Sales" in user_sections:
                display_sales_report()
            else:
                st.warning("You do not have access to any section. Please contact the administrator.")
        else:
            st.warning("Please log in to access the system.")

    else:
        st.warning("You must log in to access this page.")
        st.stop()  # Stops execution if not logged in

if __name__ == "__main__":
    main()










