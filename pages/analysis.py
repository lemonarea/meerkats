# import the libraries
import streamlit as st

# local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu

# page config
st.set_page_config(
    page_title=get_app_title(),
    layout="wide",
    initial_sidebar_state="collapsed"
)


# the main menu
app_menu()

import streamlit.components.v1 as components

components.html(
    """
    <iframe
      src="https://jupyterlite.github.io/demo/lab/index.html"
      width="100%"
      height="1000px"
      style="border:none;"
    ></iframe>
    """,
    height=850,
    scrolling=True
)