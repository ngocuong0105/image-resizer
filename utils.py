'''
Some css wrappers for streamlit texts, buttons, progress bars.
'''

import time
import streamlit as st

def markdown_css(txt:str, font_size:int, color:str,
                    height:int = 17, position:str = 'left',col:int = 1) -> None:
    '''
    CSS wrapper for streamlit's markdown.
    '''
    css_txt = f'<p style="font-family:sans-serif;color:{color}; font-size: {font_size}px;' + \
                f' text-align:{position};line-height: {height}px;"> {txt} </p>'
    if col==1:
        st.markdown(css_txt, unsafe_allow_html=True)
    else:
        col.markdown(css_txt, unsafe_allow_html=True)

def click_button(txt:str, on_click = None, args = None,
                    size:int =20, position:int = None):
    '''
    Customizable streamlit button with CSS style wrap. 
    '''
    color = '#ff9e00'
    if position is None:
        css_style = f'<style>div.stButton > button:first-child' + \
            f'{{background-color:{color};color:white;' + \
            f'font-size:{size}px;text-align:center;font-weight:bold}} </style>'
        st.markdown(css_style, unsafe_allow_html=True)
        return st.button(f'{txt}', on_click = on_click, args = args)
    else:
        columns = st.columns(101)
        css_style = f'<style>div.stButton > button:first-child {{background-color:{color};' + \
                    f'color:white;font-size:{size}px;text-align:center;font-weight:bold}} </style>'
        columns[position].markdown(css_style, unsafe_allow_html=True)
        return columns[position].button(f'{txt}', on_click = on_click, args = args)

def click_buttons(texts: 'list[str]', size:int, positions:'list[int]'):
    '''
    Multiple customizable streamlit buttons. 
    '''
    color = '#ff9e00'
    columns = st.columns(len(texts))
    buttons = []
    for i,pos in enumerate(positions):
        css_style  = f'<style>div.stButton > button:first-child {{background-color:{color};' + \
                    f'color:white;font-size:{size}px;text-align:center;font-weight:bold}} </style>'
        columns[pos].markdown(css_style, unsafe_allow_html=True)
        buttons.append(columns[pos].button(f'{texts[i]}'))
    return buttons

def wait_message(txt:str, seconds:int):
    '''
    Displays wait message with a flashing bar.
    '''
    placeholder = st.empty()
    placeholder.text(f'{txt}')
    bar = st.progress(0)
    for i in range(seconds):
        bar.progress((i+1)/seconds)
        time.sleep(1)
    bar.empty()
    placeholder.empty()
