import streamlit as st
from PIL import Image

from pages import home, resizeImage
from utils import click_button 

# App layout settings
about_info = 'Simple image coompressor.'
menu_items = {'About': about_info}


st.set_page_config(page_title='Image resizer',\
                page_icon=Image.open('static/webIcon.png'),\
                layout='wide',\
                initial_sidebar_state='collapsed',\
                menu_items=menu_items)

if 'home' not in st.session_state:
    home.show_title('IMAGE RESIZER')
    if click_button('Start', position=48):
        st.write('In home')
        st.session_state['home'] = None
        st.experimental_rerun()
elif 'resizeImage' not in st.session_state:
    if click_button('Home',size=15,position=0):
        del st.session_state['home']
        st.experimental_rerun()
    resizeImage.run()