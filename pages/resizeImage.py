'''
Streamlit page for resizing image.
'''

import streamlit as st
import cv2
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

import alphashape
from shapely.geometry import Point
from utils import click_button
from imageResizer import ResizeableImage, resizeableImage

def open_file() -> 'tuple[ResizeableImage,str]':
    '''
    Image uploader for resizing image page. Return ResizeableImage object which supports
    all operations for seam computation, insertion, removal.
    '''
    txt = 'If this is your first time here please do check out sample results in my [GitHub](https://github.com/ngocuong0105/imageResizer).'
    st.write(txt)
    uploaded_file = st.file_uploader("Upload your own image file", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        st.write('File is loaded.')
        file_bytes = np.asarray(bytearray(uploaded_file.getbuffer()))
        np_img= cv2.imdecode(file_bytes,cv2.IMREAD_COLOR).astype(np.float32)
        format_type = uploaded_file.type.split('/')[-1]
        resImage = ResizeableImage(np_img,format_type)
        return resImage
    else:
        from PIL import Image
        image = Image.open('static/ballons.jpg')
        st.session_state['default_seam'] = [255,255,255]
        st.write('Default upload:')
        st.image(image)
        np_img = cv2.imread('static/ballons.jpg', cv2.IMREAD_COLOR)
        resImage = ResizeableImage(np_img,'.jpg')
        return resImage

def run() -> None:
    '''
    Driver function for running the whole page.
    Controls user flow on streamlit UI.
    '''
    resImage = open_file()
    if resImage==None:
        st.stop()
    options = ['🗜️ Image compression',' 🖼️ Image enlargement','🪞 Soften Image','']
    mode = st.selectbox('Select action',options, index = 0)
    # image compression
    if mode==options[0]:
        # select compression mode
        txt = 'Select compression mode'
        options = ['🗜️ Simply compress image','🛡️ Compress image with protected area', '✂️ Compress image with object removal']
        d = dict(zip(['simple','protect','removal'],options))
        compress_mode = st.selectbox(txt,options)

        if compress_mode==d['simple']:
            # select new height and width
            new_height,new_width = new_width_height(resImage)
            
        elif compress_mode==d['protect']:
            # select new height and width
            new_height,new_width = new_width_height(resImage)
            tool_txt = 'Select drawing tool:'
            start_txt = 'Select protected area:'
            end_txt = 'You are ready to compress!'
            resImage.protected = canvas_protection(resImage,tool_txt,start_txt,end_txt,resImage.height,resImage.width)
        
        elif compress_mode==d['removal']:
            tool_txt = 'Select drawing tool:'
            start_txt = 'Select area to be removed:'
            end_txt = 'You are ready to compress!'
            resImage.removed = canvas_protection(resImage,tool_txt,start_txt,end_txt,resImage.height,resImage.width)
        
        # resizing image
        if click_button('Resize',size=15):
            if compress_mode==d['removal']:
                compress_image(resImage, None, remove = True)
            else:
                compress_image(resImage, new_width)

        # download image
        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],resImage.format_type)

    elif mode==options[1]:
        # select enlarge mode
        txt = 'Select enlarging mode'
        options = ['🖼️ Simply enlarge image','🛡️ Enlarge with protected area', '✏️ Enlarge with specified area for enlargement']
        d = dict(zip(['simple','protect','removal'],options))
        enlarge_mode = st.selectbox(txt,options)

        # select new height and width
        new_height,new_width = new_width_height_enlarge(resImage)
        
        # canvas for selecting protected/removed area. Stops run until selected.
        if enlarge_mode==d['protect']:
            tool_txt = 'Select drawing tool:'
            start_txt = 'Select protected area:'
            end_txt = 'You are ready to enlarge!'
            resImage.protected = canvas_protection(resImage,tool_txt,start_txt,end_txt,resImage.height,resImage.width)
        elif enlarge_mode==d['removal']:
            tool_txt = 'Select drawing tool:'
            start_txt = 'Select area to be enlarged:'
            end_txt = 'You are ready to enlarge!'
            resImage.removed = canvas_protection(resImage,tool_txt,start_txt,end_txt,resImage.height,resImage.width)
        
        # enlarge image
        if click_button('Enlarge image',size=15):
            enlarge_image(resImage, new_width)

        # download image
        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],resImage.format_type)

    elif mode == options[2]:
        st.write('Softening certain parts of the image is usually used after object \
                     removal of an image because of unwanted edge appearance')
        tool_txt = 'Select drawing tool:'
        start_txt = 'Select "edgy" area to soften:'
        end_txt = 'You are ready to soften!'
        area = canvas_protection(resImage,tool_txt,start_txt,end_txt,resImage.height,resImage.width)
        if click_button('Soften!', size=15):
            soften_area(resImage, area)

        # download image
        if 'result' in st.session_state:
            download_image_button(st.session_state['result'],resImage.format_type)

def soften_area(resImage:resizeableImage, area: set()) -> None:
    '''
    Image blurring/softening on certain area selected in canvas by user.
    '''
    resImage.blur(area)
    st.write('Image is ready:')
    st.image(resImage.encodeBytes(resImage.format_type),width=resImage.width)
    st.session_state['result'] = resImage
    
def compress_image(resImage:resizeableImage, new_width:int, remove:bool = False) -> None:
    '''
    Image compression - supports object removal and object protection.
    Protected objects and object tobe removed are chosen by user in canvas drawing.
    '''
    # text and image placeholders
    txt_place = st.empty()
    bar = st.progress(0)
    img_place = st.empty()
    if not remove:
        w = resImage.width
        for i in range(w-new_width):
            txt_place.write(f'Compressing image... Current width: {resImage.width}')
            bar.progress((i+1)/(w-new_width+1))
            # seam computation
            vertical_seam = resImage.best_seam()
            resImage.color_seam(vertical_seam, st.session_state.get('default_seam',[0,0,255]))
            img_place.image(resImage.encodeBytes(resImage.format_type),width=resImage.width)
            resImage.remove_seam(vertical_seam)

    else:
        n = len(resImage.removed)
        prev,curr=n,n
        removed_pixls = 0
        while len(resImage.removed)>0:
            # text and bar placeholders
            txt_place.write(f'Removing object... Current width: {resImage.width}. ')
            removed_pixls+=prev-curr
            bar.progress(removed_pixls/n)
            # seam computation
            prev = curr
            vertical_seam = resImage.best_seam()
            resImage.color_seam(vertical_seam) 
            img_place.image(resImage.encodeBytes(resImage.format_type),width=resImage.width)
            resImage.remove_seam(vertical_seam)
            curr = len(resImage.removed)
            if prev==curr:
                break
    bar.progress(1.0)
    st.session_state['result']=resImage

def enlarge_image(resImage:resizeableImage, new_width:int) -> None:
    '''
    Image enlargment supports object protection and certain areas for enlargment.
    Protected objects and areas for enlargment are chosen by user in canvas drawing.
    '''
    txt_place = st.empty()
    bar = st.progress(0)
    image_place = st.empty()
    vertical_seam = resImage.best_seam()
    w = resImage.width
    for i in range(new_width - w):
        resImage.protect_area(vertical_seam,2)
        vertical_seam = resImage.best_seam()
        if i%10==0:
            resImage.unprotect_area()
        resImage.insert_seam(vertical_seam)
        txt_place.write(f'Resizing image... Current width: {resImage.width}.')
        bar.progress((i+1)/(new_width - w))
        resImage_copy= ResizeableImage(resImage.marked_seam(vertical_seam))
        image_place.image(resImage_copy.encodeBytes(resImage.format_type),width=resImage.width)
    image_place.image(resImage.encodeBytes(resImage.format_type),width=resImage.width)
    bar.progress(1.0)
    st.session_state['result'] = resImage

def download_image_button(resImage: ResizeableImage, format_type:str) -> None:
    '''
    Button for downloading an image.
    '''
    txt = 'Save file'
    button = click_button(txt,size=15)
    if button:
        st.download_button(
            label='Click to download',
            data=resImage.encodeBytes(f'.{format_type}'),
            file_name=f'result.{format_type}',
            mime=f'image/{format_type}')
        del st.session_state['result']

def new_width_height(resImage:ResizeableImage) -> tuple:
    '''
    Selection boxes for users to choose desired height and width when compressing.
    Currently the app supports compression only on the width side.
    '''
    # txt_height = f'Select desired height\
    #         (should be smaller than the current height of {resImage.height}px):'
    # new_height = st.number_input(txt_height, value = int(resImage.height*0.8), step=1)
    txt_width = f'Select target width\
            (should be smaller than the current width of {resImage.width}px):'
    new_width = st.number_input(txt_width, value =  int(resImage.width*0.8), step=1)
    width_removed = resImage.width-new_width
    new_height = 0 # remove if vertical seam removal is supported
    height_removed = resImage.height-new_height
    if width_removed<0 or height_removed<0:
        st.write('Please select width and height which are smaller than the initial ones.')
        st.stop()
    return new_height,new_width

def new_width_height_enlarge(resImage:ResizeableImage) -> tuple:
    '''
    Selection boxes for users to choose desired height and width when enlarging.
    Currently the app supports enlargement only on the width side.
    '''
    # txt_height = f'Select desired height\
    #         (should be larger than the current height of {resImage.height}px):'
    # new_height = st.number_input(txt_height, value = int(resImage.height*1.5), step=1)
    txt_width = f'Select target width\
            (should be larger than the current width of {resImage.width}px):'
    new_width = st.number_input(txt_width, value =  int(resImage.width*1.5), step=1)
    width_removed = resImage.width-new_width
    new_height = 2**31
    height_removed = resImage.height-new_height
    if width_removed>0 or height_removed>0:
        st.write('Please select width and height which are larger than the initial ones.')
        st.stop()
    return new_height,new_width

def canvas_protection(resImage:ResizeableImage, tool_txt:str, start_txt:str, end_txt:str, height:float, width:float, key = None) -> set:
    '''
    User interface for canvas drawing to select certain areas in the image.
    '''

    # canvas options
    drawing_mode = st.selectbox(tool_txt,('polygon', 'circle','rectangle'),key=key)

    st.write(start_txt)
    if drawing_mode=='rectangle':
        drawing_mode = 'rect'
    elif drawing_mode=='polygon':
        st.write('• Left click to choose point.')
        st.write('• Two left clicks to undo last point.')
        st.write('• Right click to close polygon.')
        st.write('• Polygon should have more than 4 vertices and concave shapes are discouraged.')
    # Create a canvas 
    canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=1,
    height = height,
    width = width,
    background_image=resImage.openPilImage() if resImage else None,
    update_streamlit=True,
    drawing_mode=drawing_mode,
    key = key
    )

    # canvas annotated data is either protected or removed or enlarged
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
        elif drawing_mode=='polygon':
            points = []
            min_x,max_x = 2**31,-2**31
            min_y,max_y = 2**31,-2**31
            for _,y,x in canvas_dict['path'][:-1]:
                points.append([x,y])
                min_x=min(min_x,x)
                max_x=max(max_x,x)
                min_y=min(min_y,y)
                max_y=max(max_y,y)
            alpha_shape = alphashape.alphashape(points) # Create the alpha shape
            area = set()
            min_x=int(min_x)
            max_x=int(max_x)
            min_y=int(min_y)
            max_y=int(max_y)
            for x in range(min_x,max_x):
                for y in range(min_y,max_y):
                    if alpha_shape.contains(Point(x,y)):
                        area.add((x,y))
        return area
    else:
        st.stop() # canvas area not selected

def _display_energy(resImage: ResizeableImage):
    '''
    Helper function when debugging. Displays energy map of the image.
    Useful to put in loops while computing seams and image is compressed or enlarged.
    '''
    mat = resImage.scharr_energy_mat()
    fig, ax = plt.subplots()
    sns.heatmap(mat, ax=ax, cmap='Spectral')
    # put this code below wherever you want to display the energy map
    # energy_place = st.empty()
    # energy_place.write(_display_energy(resImage))
    return fig

