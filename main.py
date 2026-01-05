import os
import streamlit as st
from streamlit_option_menu import option_menu
import rooms,manage,reserve

st.set_page_config(
    initial_sidebar_state="expanded")

styles = {
    "nav": { "background-color": "transparent"},
    "nav-link-selected": {"background-color": "rgb(174,28,43)", "font-size": "17px", "font-weight": "bold", "color": "white"},
    "container": {"background-color": "transparent", "font-size": "17px"},
    "menu-icon": {"color": "transparent"}
}

st.markdown(
    f"""
    <style>
        [data-testid="stSidebar"] {{
            background-image: url("https://i.imgur.com/lbbGYKw.png");
            background-repeat: no-repeat;
            background-position: center top;
            padding-top: 80px;
            background-size: 178.6px 100px !important;
            width: 250px !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


class MultApp:
    def __init__(self):
        self.apps = []
    def app_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run():
        with st.sidebar:
            app = option_menu(
                "",
                options= ['Rooms', 'Reserve', 'Manage'],
                icons=["house", "calendar-plus", "gear"],
                default_index=0,
                styles=styles)
            
        if app == 'Rooms':
            rooms.app()
        if app == 'Reserve':
            reserve.app()
        if app == 'Manage':
            manage.app()
    run()


    

