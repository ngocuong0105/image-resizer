'''
Graphical User Interface for the Image Compressor App.
'''
import os,sys
import tkinter as Tkinter
import tkinter.filedialog as tkFileDialog
from compressor import ResizeableImage
from ttkthemes import ThemedTk

seam = None
image = None
temp='_gtemp_.ppm' # keeps current version of image under compression

def open_file():
    global image, status
    filename = tkFileDialog.askopenfilename()
    if filename is None: return
    status['text'] = f'Loading {os.path.basename(filename)}...'
    status.update()
    try:
        image = ResizeableImage(filename)
    except:
        status['text'] = f'Error loading {os.path.basename(filename)}!'
        raise
    update_display()
    seam = None
    status['text'] = f'Loaded {os.path.basename(filename)}.  Now compute or remove seam.'

def save_file():
    global image, status
    if image is None: return
    filename = tkFileDialog.asksaveasfilename()
    if filename is None: return
    status['text'] = f'Saving {os.path.basename(filename)}...'
    status.update()
    try:
        image.save(filename)
    except:
        status['text'] = f'Error saving {os.path.basename(filename)}!'
        raise
    status['text'] = f'Saved {os.path.basename(filename)}.'

def update_display():
    global image, photo, display, root, buttons
    image.save_ppm(temp)
    photo = Tkinter.PhotoImage(master=root, file=temp)
    display['image'] = photo
    root.geometry('1920x1080')
    os.remove(temp)

def compute_seam(count=0):
    global seam
    if seam is None:
        if count:
            status['text'] = f'Computing seam {(count+1)}...' 
        else:
            status['text'] = 'Computing seam...'
        status.update()
        seam = image.best_seam()
        if count:
            status['text'] = f'Computed seam {(count+1)}.'
        else:
            status['text'] = 'Computed seam.'

def show_seam():
    global image, seam
    if image is None: return
    compute_seam()
    image.color_seam(seam)
    update_display()
    status['text'] = 'Computed seam, as shown in red.'

def remove_seam():
    global image, seam
    if image is None: return
    count = 0
    while True:
        compute_seam(count)
        image.remove_seam(seam)
        update_display()
        seam = None
        count += 1
        try:
            repeat = int(multiple_spin.get())
        except ValueError:
            break
        if repeat <= 1: break
        repeat -= 1
        multiple_spin.delete(0,'end')
        multiple_spin.insert(0,repeat)
        multiple_spin.update()
    multiple_spin.delete(0,'end')
    multiple_spin.insert(0,1)
    if count > 1:
        status['text'] = f'Removed {count} seams.'
    else:
        status['text'] = 'Removed seam.'

# theme settings
bgColor = '#ffbc56'
secondaryColor = '#faa92c'
font = 'fixed'

# set app background color,size,theme
root = ThemedTk(theme="radiance")
root['bg'] = bgColor
root.title('Image Compressor')
root.geometry('1920x1080')
curr_dir=sys.path[0]
# set app icon
curr_dir=sys.path[0]
img = Tkinter.PhotoImage(file=os.path.join(curr_dir, "static/icon.png"))
root.tk.call('wm', 'iconphoto', root._w, img)

status = Tkinter.Label(text='Please open an image.', font=(font, 22,'bold'))
status.pack(side='top')
status.configure(background=bgColor)

# open,save,show seam, remove seam buttons
buttons = Tkinter.Frame()
open_button = Tkinter.Button(buttons, text='Open ...', command=open_file, height=2, font=(font, 12,'bold'),\
    background=secondaryColor, activebackground=bgColor,highlightbackground=secondaryColor)
open_button.pack(side='top', fill='x')
save_button = Tkinter.Button(buttons, text='Save...', command=save_file, height=2, font=(font, 12,'bold'),\
    background=secondaryColor, activebackground=bgColor,highlightbackground=secondaryColor)
save_button.pack(side='top', fill='x')
show_button = Tkinter.Button(buttons, text='Show Seam', command=show_seam, height=2, font=(font, 12,'bold'),\
    background=secondaryColor, activebackground=bgColor,highlightbackground=secondaryColor)
show_button.pack(side='top', fill='x')
remove_button = Tkinter.Button(buttons, text='Remove Seam', command=remove_seam, height=2, font=(font, 12,'bold'),\
    background=secondaryColor, activebackground=bgColor,highlightbackground=secondaryColor)
remove_button.pack(side='top', fill='x')

multiple_frame = Tkinter.Frame(buttons, background=bgColor, highlightbackground=secondaryColor)
multiple_label = Tkinter.Label(multiple_frame, text='Repeat:',\
     background=bgColor, highlightbackground=secondaryColor,font=(font, 12))
multiple_label.pack(side='left')
multiple_spin = Tkinter.Spinbox(multiple_frame,
    from_=1, to_=100, increment=1, background=bgColor, highlightbackground=bgColor,font=(font, 12))

multiple_spin.pack(side='right')
multiple_frame.pack(side='top', fill='x')
buttons.pack(side='left')
display = Tkinter.Label(root,background='#faa92c')
display.pack(side='top')
root.mainloop()

# %%
