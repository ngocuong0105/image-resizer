import os
import struct
from PIL import Image
from methodtools import lru_cache

class ImageMatrix(dict):
    def __init__(self, image):
        """Takes a image filename and stores pixels, width and height."""
        image = Image.open(image)
        self.width, self.height = image.size
        pixels = iter(image.getdata())
        for i in range(self.height):
            for j in range(self.width):
                self[i,j] = pixels.__next__()

    def color_seam(self, seam, color=(255,0,0)):
        """Takes a seam (a list of coordinates) and colors it all one color."""
        for i,j in seam:
            self[i,j] = color

    def remove_seam(self, seam):
        """Takes a seam (a list of coordinates with exactly one pair of
        coordinates per row). Removes pixel at each of those coordinates,
        and slides left all the pixels to its right. Decreases the width
        by 1."""
        seen = [False for _ in range(self.height)]
        for i,j in seam:
            seen[i] = True
            for jj in range(j, self.width-1):
                self[i,jj] = self[i,jj+1]
            del self[i,self.width-1]
        self.width -= 1

    def image(self):
        """Returns a PIL Image that is represented by self."""
        image = Image.new('RGB', (self.width, self.height))
        image.putdata([self[i,j] for i in range(self.height) for j in range(self.width)])
        return image

    def save(self,*args,**keyw):
        self.image().save(*args,**keyw)

    def ppm(self):
        """Returns self in (binary) ppm form."""
        return b'P6 %d %d 255\n' % (self.width, self.height) + \
            b''.join ([struct.pack('BBB', *self[i,j])
                      for i in range(self.height) for j in range(self.width)])

    def save_ppm(self, filename):
        """Saves self as a .ppm"""
        f = open(filename, 'wb')
        f.write(self.ppm())
        f.close()
    
    @lru_cache()
    def energy(self, i, j):
        """Given coordinates (i,j), returns an energy, or cost associated
        with removing that pixel."""
        if i==0 or i==self.height-1 or j==0 or j==self.width-1:
            # Punish highly if remove edge
            return 10000
        else: # Sobel gradient magnitude?
            return self.distance(self[i-1,j], self[i+1,j]) +\
                   self.distance(self[i,j-1], self[i,j+1]) +\
                   self.distance(self[i-1,j-1], self[i+1,j+1]) +\
                   self.distance(self[i+1,j-1], self[i-1,j+1])

    def distance(self, pixelA, pixelB):
        """A distance metric between two pixels, based on their colors."""
        ans = 0
        for i in range(len(pixelA)):
            valueA = pixelA[i]
            valueB = pixelB[i]
            ans += abs(valueA-valueB)
        return ans
