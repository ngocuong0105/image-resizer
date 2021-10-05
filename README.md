# Image resizer using seam carving
- Have you ever been frustated when your favorite family picture or another wallpaper does not fit on your screen?
- Have you tried to resize your image but it just scales up/down everything making the objects in the picture look peculiar?
- Have you ever wanted to remove an unwanted item from an image and make it disappear as if it was never there?

If you answer yes to any of the questions above, you are on the right place. This project provides a [web application]() for image resizing with content awareness. Successful compression and enlargement of images should not take into account only  geometric constraints, but consider the image content as well. Inspired by this [youtube video](http://www.youtube.com/watch?v=vIFCV2spKtg) and [Avidan and Shamir](http://graphics.cs.cmu.edu/courses/15-463/2007_fall/hw/proj2/imret.pdf) paper, we use seam carving to resize images while protecting sensitive parts of the image such as objects. We achieve content-aware resizing by smartly picking which pixels to be removed or multiplied. **Rather than doing a simple scaling where all pixels are just averaged over neighbours or copied, here we use dynamic programming to determine the "best" pixels to remove.** Best pixels are chosen using either [Sobel](https://en.wikipedia.org/wiki/Sobel_operator) or [Scharr](https://en.wikipedia.org/wiki/Sobel_operator) gradient operators which  compute energy maps of the image.  
The app supports image compression, enlargement and object removal which is a combination of the previous two. Below you can see sample results produced by my [image resizer]() app. These results are compared with a generic [image editor](https://resizeimage.net/), which is one of the top results in google search.

------------------------------------------------------------------------------------
## Object removal
### Vase bye bye!
![](results/object_removal/sofa.gif)

### Original image
<img src="results/object_removal/sofa.jpg" width = "600" height="402">

### Vase removed
<img src="results/object_removal/sofa_removed.jpeg" width = "600" height="402">

------------------------------------------------------------------------------------
## Image enlargement

### Protect Charmander!
![](results/image_enlargement/charmander.gif)

### Original image
<!-- ![](results/image_enlargement/charmander_Original.png) -->
<img src="results/image_enlargement/charmander_Original.png" width = "600" height="380">

### Generic image enalrgement with scaling using first [google result](https://resizeimage.net/)
![](results/image_enlargement/charmander_Scale.png)

### Image enlargement with content awareness
![](results/image_enlargement/charmander_ImageResizer.png)

------------------------------------------------------------------------------------
## Image compression

### The ship shall not sink!
![](results/image_compression/ship.gif)

### Original image
![](results/image_compression/ship_Original.jpg)

### Generic compression with scaling using first [google result](https://resizeimage.net/) 
![](results/image_compression/ship_Scale.jpg)

### Image compression with content protection
![](results/image_compression/ship_ImageResizer.jpg)


