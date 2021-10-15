'''
Driver code of the app.
To run it you neet to install streamlit v.1.0 and run in the terminal
streamlit run app.py
Do not forget to set the current working directory where app.py is!
'''
import streamlit as st
from PIL import Image
from pages import home, resizeImage
from utils import click_button 

# App layout settings
about_info = 'Simple image coompressor.'
menu_items = {'About': about_info}


st.set_page_config(page_title='SIR',\
                page_icon=Image.open('static/webIcon.png'),\
                initial_sidebar_state='collapsed',\
                menu_items=menu_items)

if 'home' not in st.session_state:
    home.show_title('SMART IMAGE RESIZER')
    if click_button('Start',size=18,position=65):
        st.write('In home')
        st.session_state['home'] = None
        st.experimental_rerun()
elif 'resizeImage' not in st.session_state:
    if click_button('Home',size=15,position=0):
        del st.session_state['home']
        st.experimental_rerun()
    resizeImage.run()
