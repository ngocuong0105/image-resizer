'''
Streamlit home page
'''
import streamlit as st

def show_title(title:str):
    with open('static/title_style.css') as f:
        title_html = f'<style>{f.read()}</style><h1>{title}</h1>'
    st.markdown(title_html,unsafe_allow_html=True)