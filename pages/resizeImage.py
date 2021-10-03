import streamlit as st
from PIL import Image
import cv2
import numpy as np
import io
import pandas as pd
from streamlit_drawable_canvas import st_canvas

from utils import click_button,click_buttons
from imageResizer import ResizeableImage

def open_file() -> 'tuple[ResizeableImage,str]':
    st.write("Check out this [video](https://www.youtube.com/watch?v=vIFCV2spKtg) to understand the compression approach.")
    uploaded_file = st.file_uploader("Upload image file", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        st.write('File is loaded.')
        file_bytes = np.asarray(bytearray(uploaded_file.getbuffer()))
        np_img= cv2.imdecode(file_bytes,cv2.IMREAD_COLOR).astype(np.float32)
        resImage = ResizeableImage(np_img)
        format_type = uploaded_file.type.split('/')[-1]
        return resImage,format_type
    return None,None

def run():
    resImage,format_type = open_file()
    if resImage==None:
        st.stop()
    ratio = resImage.height//resImage.width+1
    display_width=min(max(resImage.width,800),1000)
    display_height=ratio*500
    options = ['🖼️ Image resizing','📸 Image resizing with protected area','✂️ Object removal','Enlarge image','']
    mode = st.selectbox('Select action',options, index = 4)
    # image resizing
    if mode=='🖼️ Image resizing':
        # select new height and width
        new_height,new_width = new_width_height(resImage)

        button = click_button('Resize',size=15)
        width_place = st.empty()
        if button:
            # display image
            bar = st.progress(0)
            img_place = st.empty()
            img_place.image(resImage.encodeBytes(format_type),width=display_width)
            w = resImage.width
            for i in range(w-new_width):
                # text and image placeholders
                width_place.write(f'Resizing image... Current width: {resImage.width}')
                bar.progress((i+1)/(w-new_width+1))
                # seam computation
                vertical_seam = resImage.best_seam()
                resImage.color_seam(vertical_seam) 
                img_place.image(resImage.encodeBytes(format_type),width=display_width)
                resImage.remove_seam(vertical_seam)
            st.session_state['result']=resImage
        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],format_type)

    # resizing with object protection/removal
    elif mode=='📸 Image resizing with protected area':
        # select new height and width
        new_height,new_width = new_width_height(resImage)
        
        # canvas for selecting protected/removed area. Stops run until selected.
        protect = True
        canvas(resImage,protect,resImage.height,resImage.width)

        # # plot weights
        # mat = resImage.scharr_energy_mat()
        # import seaborn as sns
        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots()
        # sns.heatmap(mat, ax=ax, cmap='Spectral')
        # st.pyplot(fig)

        # image resizing
        txt = f'{"Resize"*protect+"Remove area"*(1-protect)}'
        button = click_button(txt,size=15)
        if button:
            # display image
            txt_place = st.empty()
            bar = st.progress(0)
            img_place = st.empty()
            img_place.image(resImage.encodeBytes(format_type),width=display_width)
            w = resImage.width
            for i in range(w-new_width):
                # text and bar placeholders
                txt_place.write(f'{"Resizing image"*protect+"Removing object"*(1-protect)}...\
                    Current width: {resImage.width}')
                bar.progress((i+1)/(w-new_width+1))
                # seam computation
                vertical_seam = resImage.best_seam()
                resImage.color_seam(vertical_seam) 
                img_place.image(resImage.encodeBytes(format_type),width=display_width)
                resImage.remove_seam(vertical_seam)
            st.session_state['result'] = resImage
            img_place.image(resImage.encodeBytes(format_type),width=display_width)
            txt_place.write('Finished. Click save button below to download.')
            bar.progress(1.0)

        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],format_type)
            
    elif  mode=='✂️ Object removal':
        # canvas for selecting protected/removed area. Stops run until selected.
        protect = False
        canvas(resImage,protect,resImage.height,resImage.width)

        # image resizing
        txt = f'{"Resize"*protect+"Remove area"*(1-protect)}'
        button = click_button(txt,size=15)
        if button:
            # display image
            txt_place = st.empty()
            bar = st.progress(0)
            img_place = st.empty()
            img_place.image(resImage.encodeBytes(format_type),width=display_width)
            n = len(resImage.removed)
            prev,curr=n,n
            removed_pixls = 0
            # plot_place= st.empty()
            while len(resImage.removed)>0:
                # text and bar placeholders
                txt_place.write(f'{"Resizing image"*protect+"Removing object"*(1-protect)}...\
                    Current width: {resImage.width}. Removed pixels: {removed_pixls}')
                removed_pixls+=prev-curr
                bar.progress(removed_pixls/n)
                
                # # plot weights
                # mat = resImage.sobel_energy_mat()
                # import seaborn as sns
                # import matplotlib.pyplot as plt
                # fig, ax = plt.subplots()
                # sns.heatmap(mat, ax=ax, cmap='Spectral')
                # plot_place.write(fig)

                # seam computation
                prev = curr
                vertical_seam = resImage.best_seam()
                resImage.color_seam(vertical_seam) 
                img_place.image(resImage.encodeBytes(format_type),width=display_width)
                resImage.remove_seam(vertical_seam)
                curr = len(resImage.removed)
            st.session_state['result'] = resImage
            img_place.image(resImage.encodeBytes(format_type),width=display_width)
            bar.progress(1.0)
            txt_place.write('Finished. Click save button below to download.')

        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],format_type)

    elif mode == 'Enlarge image':
        num_enlarge = st.number_input('Number of seams to add:',1,1000,10,1)
        if click_button('Go!'):
            txt_place = st.empty()
            image_place = st.empty()
            vertical_seam = resImage.best_seam()
            for i in range(num_enlarge):
                prev_seam = vertical_seam
                if i>0:
                    resImage.uncolor_seam(prev_seam)
                vertical_seam = resImage.best_seam()
                resImage.insert_seam(vertical_seam)
                resImage.color_seam(vertical_seam)
                txt_place.write(f'Seam {i+1}')
                image_place.image(resImage.encodeBytes(format_type),width=display_width)

            image_place.image(resImage.encodeBytes(format_type),width=display_width)
            st.session_state['result'] = resImage

        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],format_type)

def download_image_button(resImage: ResizeableImage, format_type:str):
    txt = 'Save file'
    button = click_button(txt,size=15)
    if button:
        st.download_button(
            label='Click to download',
            data=resImage.encodeBytes(f'.{format_type}'),
            file_name=f'result.{format_type}',
            mime=f'image/{format_type}')

def new_width_height(resImage:ResizeableImage) -> tuple:
    txt_height = f'Select desired height\
            (should be smaller than the current height of {resImage.height}px):'
    new_height = st.number_input(txt_height, value = 128, step=1)
    txt_width = f'Select desired width\
            (should be smaller than the current height of {resImage.width}px):'
    new_width = st.number_input(txt_width, value = 256, step=1)
    width_removed = resImage.width-new_width
    height_removed = resImage.height-new_height
    if width_removed<0 or height_removed<0:
        st.write('Please select width and height which are smaller than the initial ones.')
        st.stop()
    return new_height,new_width

def canvas(resImage:ResizeableImage, protect:bool, height:float, width:float):

    # canvas options
    drawing_mode = st.selectbox(
        f"Tool for selecting {'protected'*protect+'to be removed'*(1-protect)} area:",\
                ("rectangle", "circle","polygon")
    )
    if drawing_mode=='rectangle':
        drawing_mode = 'rect'

    # Create a canvas component
    if protect:
        st.write('Select protected area on the image:')
    else:
        st.write('Select area to be removed on the image:')
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=1,
        height = height,
        width = width,
        background_image=resImage.openPilImage() if resImage else None,
        update_streamlit=True,
        drawing_mode=drawing_mode,
        key="canvas"
    )

    # canvas annotated data is either protected or removed
    if canvas_result.json_data and canvas_result.json_data['objects']!=[]:
        canvas_dict = canvas_result.json_data["objects"][0]
        if drawing_mode=='rect':
            top,left = canvas_dict['top'],canvas_dict['left']
            w,h = canvas_dict['width'],canvas_dict['height']
            area = set()
            for i in range(top,top+h):
                for j in range(left,left+w):
                    area.add((i,j))
        elif drawing_mode=='circle':
            center = int(canvas_dict['top']+canvas_dict['radius']),int(canvas_dict['left']+canvas_dict['radius'])
            r = int(canvas_dict['radius'])+1
            area = set()
            for i in range(center[0]-r,center[0]+r):
                for j in range(center[1]-r,center[1]+r):
                    if (i-center[0])**2+(j-center[1])**2<r**2:
                        area.add((i,j))
        if protect:
            resImage.protected=area
            st.write('You are ready to resize!')
        else:
            resImage.removed=area
            st.write('You are ready to remove object!')
    else:
        st.stop() # canvas area not selected