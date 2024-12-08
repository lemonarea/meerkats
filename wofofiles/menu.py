import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# import the database connection
from wofofiles.conn import username, password, host, port, database


# Create a connection string for the MySQL database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string, echo=True)

def app_menu():
    with st.sidebar:
        with st.expander("☰ Navigator", expanded=False):
            st.page_link("app.py", label="🏠︎ Home")
            st.page_link("pages/notebook.py", label="🗒 INB", disabled=True)
            st.page_link("pages/chat.py", label="🗣 Chat", disabled=True)
            st.page_link("pages/kpis.py", label="〽 KPIs", disabled=True)
            st.page_link("pages/review.py", label="☀ Review", disabled=True)
            st.page_link("pages/monitor.py", label="⏲ Monitor", disabled=True)
            st.page_link("pages/model.py", label="☢ Models", disabled=True)
            st.page_link("pages/report.py", label="🖨 Reports")

            # admin section
            #  Check user access to the admin section if the group is admin
            # Check if the user is logged in
            if st.session_state.get('logged_in'):
                try:
                    with engine.connect() as connection:
                        user_group_query = text("""
                            SELECT g.GroupName 
                            FROM users u
                            JOIN access_control ac ON u.UserCode = ac.UserCode
                            JOIN `groups` g ON ac.GroupCode = g.GroupCode
                            WHERE u.UserCode = :user_code
                        """)
                        result = connection.execute(user_group_query, {'user_code': st.session_state.get('user_code')}).fetchone()
                        user_group = result.GroupName if result else None
                        st.session_state['user_group'] = user_group
                except SQLAlchemyError as e:
                    st.error(f"Failed to retrieve user group: {str(e.__dict__['orig'])}")
                    return

                # Check user access to the MAC page if the group is admin
                if st.session_state.get('user_group') == 'Admin':
                    st.markdown("---")
                    st.page_link("pages/access_control.py", label="⚙︎ Users Management")
        




 
            