import numpy as np
from PIL import Image
from methodtools import lru_cache
import cv2
from numpy.lib.function_base import iterable
import random
import io
import copy

class ResizeableImage:
    def __init__(self, image: np.array, format_type:str = '.png') -> None:
        """
        ResizeableImage is the core object of this app. 
        It takes an image filename and stores the image pixels, width and height.
        Computes energy maps of an image and finds best seam to be removed.
        Supports all operations on seams - removal, insertion, coloring.
        """
        self.height, self.width, _= image.shape
        self.pixels = image
        self.format_type = format_type

        self.protected = set()
        self.removed = set()
        self.temp_protected = set()
        self.const = 30000 # energy constant

    #################################
    # Image operations with seam
    #################################
    def color_seam(self, seam:list, color=[0,0,255]) -> None:
        '''
        Takes a seam (a list of coordinates) and colors it all one color.
        '''
        for i,j in seam:
            self.pixels[i][j] = color

    def remove_seam(self, seam:list) -> None:
        '''
        Takes a seam (a list of coordinates with exactly one pair of
        coordinates per row). Removes pixel at each of those coordinates,
        and slides left all the pixels to its right. Shifts pixels under
        protection and removal accordingly. Decreases the width by 1.
        '''
        for i,j in seam:
            if (i,j) in self.removed:
                self.removed.remove((i,j))
            for jj in range(j, self.width-1):
                self.pixels[i][jj] = self.pixels[i][jj+1]
                if (i,jj) in self.protected:
                    self.protected.remove((i,jj))
                    self.protected.add((i,jj-1))
                if (i,jj) in self.removed:
                    self.removed.remove((i,jj))
                    self.removed.add((i,jj-1))
        self.pixels = np.delete(self.pixels,-1,1)
        self.width -= 1

    def insert_seam(self, seam:list) -> None:
        '''
        Takes a seam (a list of coordinates with exactly one pair of
        coordinates per row). Adds seam on the right which is the average of its neighbour pixels.
        '''
        self.pixels = np.insert(self.pixels,self.width,self.pixels[:,-1],axis=1)
        for i,j in seam:
            for jj in range(self.width,j,-1):
                self.pixels[i][jj] = self.pixels[i][jj-1]
                if (i,jj-1) in self.protected:
                    self.protected.remove((i,jj-1))
                    self.protected.add((i,jj))
                if (i,jj-1) in self.temp_protected:
                    self.temp_protected.remove((i,jj-1))
                    self.temp_protected.add((i,jj))
                if (i,jj-1) in self.removed:
                    self.removed.add((i,jj))
                    
            self.pixels[i][j] = self._average(i,j)

        self.width += 1
    
    def _average(self,i:int , j:int) -> list:
        '''
        Average pixels color of neihbours of pixel (i,j).
        '''
        res = []
        neighbours = [(-1,-1),(-1,1),(0,-1),(0,1),(1,-1),(1,-1)]
        for c in range(3):
            curr,count = 0,0
            for dx,dy in neighbours:
                if i+dx>=0 and i+dx<self.height and j+dy>=0 and j+dy<self.width:
                    curr += self.pixels[i+dx][j+dy][c]
                    count += 1
            res.append(curr/count)
        return res
    
    def protect_area(self, area: iterable, protection_range:int = 0) -> None:
        '''
        In-place protects cells in specified area.
        '''
        for i,j in area:
            self.temp_protected.add((i,j))
            for rang in range(protection_range+1):
                self.temp_protected.add((i,min(self.width-1,j+rang)))
                self.temp_protected.add((i,max(0,j-rang)))


    def unprotect_area(self, area:set = set(), protection_range:int = 1) -> None:
        '''
        In-place unprotects temporary protected cells.
        '''
        if len(area)==0:
            self.temp_protected = set()
        else:
            for i,j in area:
                for rang in range(protection_range+1):
                    self.temp_protected.remove((i,j+rang))
                    self.temp_protected.remove((i,j-rang))

    def marked_seam(self, seam:list, thickness:int = 0, color = [0,0,255]):
        '''
        Takes a seam and returns it marked in read.
        '''
        marked = copy.deepcopy(self.pixels)
        for i,j in seam:
            marked[i][j] = color
            for t in range(thickness+1):
                marked[i][max(0,j-t)] = color
                marked[i][min(self.width-1,j+t)] = color
        return marked

    def blur(self, area:set):
        '''
        Softens color of pixels in area by taking average of its nearby pixels.
        '''
        for i,j in area:
            newcolor = []
            for c in range(3):
                val = 0
                for jj in range(1,21):
                    val+=self.pixels[i][max(0,j-jj)][c]
                    val+=self.pixels[i][min(self.width-1,j+jj)][c]
                newcolor.append(val/40)
            self.pixels[i][j] = newcolor

    #################################
    # Energy matricies computation
    #################################
    @lru_cache()
    def energy(self, i:int, j:int) -> float:
        """
        Given coordinates (i,j), returns an energy, or cost associated with removing that pixel.
        """
        # assign high cost for edges and protected cells
        if i==0 or i==self.height-1 or j==0 or j==self.width-1 or (i,j) in self.protected:
            return self.const
        elif (i,j) in self.removed:
            return -self.const
        else: 
            return self.distance(self.pixels[i][j-1], self.pixels[i][j+1]) +\
                   self.distance(self.pixels[i-1][j], self.pixels[i+1][j]) +\
                   self.distance(self.pixels[i-1][j-1], self.pixels[i+1][j+1]) +\
                   self.distance(self.pixels[i-1][j+1], self.pixels[i+1][j-1])

    def distance(self, pixelA:list, pixelB:list) -> float:
        """
        A distance metric between two pixels, based on their colors.
        """
        ans = 0
        for i in range(len(pixelA)):
            valueA = pixelA[i]
            valueB = pixelB[i]
            ans += abs(valueA-valueB)
        return ans

    def basic_energy_mat(self) -> 'list[list]':
        '''
        Simple energy function taking distance difference of neighbour cells.
        '''
        mat = [[0]*self.width for _ in range(self.height)] 
        for i in range(self.height):
            for j in range(self.width):
                mat[i][j]=self.energy(i,j)
        return mat

    def scharr_energy_mat(self) -> 'np.array[float]':
        '''
        Scharr energy matrix.x. Additional energy constants are added in
        protected, temporary protected, removed and edge cells.
        '''
        b, g, r = cv2.split(self.pixels)
        b_energy = (np.square(cv2.Scharr(b, -1, 1, 0)) + np.square(cv2.Scharr(b, -1, 0, 1)))**0.5
        g_energy = (np.square(cv2.Scharr(g, -1, 1, 0)) + np.square(cv2.Scharr(g, -1, 0, 1)))**0.5
        r_energy = (np.square(cv2.Scharr(r, -1, 1, 0)) + np.square(cv2.Scharr(r, -1, 0, 1)))**0.5
        mat = b_energy+g_energy+r_energy

        for i,j in self.temp_protected:
            mat[i][j] = random.uniform(1,5)*self.const
        for i,j in self.protected:
            mat[i][j] = random.uniform(1,5)*self.const
        for i,j in self.removed:
            mat[i][j] = -random.uniform(1,5)*self.const

        mat[:,0] = random.uniform(1,5)*self.const
        # do not touch edge pixels
        for i in range(1,6):
            mat[:,i] = random.uniform(1,5)*self.const
            mat[:,-i] = random.uniform(1,5)*self.const

        return mat

    def sobel_energy_mat(self) -> 'np.array[float]':
        '''
        Sobel energy matrix. Additional energy constants are added in
        protected, temporary protected, removed and edge cells.
        '''
        b, g, r = cv2.split(self.pixels)
        b_energy = (np.square(cv2.Sobel(b, -1, 1, 0)) + np.square(cv2.Sobel(b, -1, 0, 1)))**0.5
        g_energy = (np.square(cv2.Sobel(g, -1, 1, 0)) + np.square(cv2.Sobel(g, -1, 0, 1)))**0.5
        r_energy = (np.square(cv2.Sobel(r, -1, 1, 0)) + np.square(cv2.Sobel(r, -1, 0, 1)))**0.5
        mat = b_energy+g_energy+r_energy

        for i,j in self.temp_protected:
            mat[i][j] = random.uniform(1,5)*self.const
        for i,j in self.protected:
            mat[i][j] = random.uniform(1,5)*self.const
        for i,j in self.removed:
            mat[i][j] = -random.uniform(1,5)*self.const

        mat[:,0] = self.const
        for i in range(1,6):
            mat[:,i] = random.uniform(1,5)*self.const
            mat[:,-i] = random.uniform(1,5)*self.const
        return mat

    #################################
    # Type conversion of images
    #################################

    def encodeBytes(self, format:str):
        _, encoded_image = cv2.imencode('.'+format, self.pixels)
        return encoded_image.tobytes()

    def openPilImage(self):
        np_img= cv2.cvtColor(self.pixels,cv2.COLOR_BGR2RGB)
        np_img = np_img.astype(np.uint8)
        return Image.fromarray(np_img)

    def byteImage(self):
        """Returns a PIL Image that is represented by self."""
        image = Image.new('RGB', (self.width, self.height))
        image.putdata([tuple(self.pixels[i][j]) for i in range(self.height) for j in range(self.width)])
        return self._pilImage_to_bytes(image)

    def _pilImage_to_bytes(self, img:Image):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format ='png')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    ###################################
    # Optimal seam computation using DP
    ###################################

    def best_seam(self) -> 'list[tuple]':
        '''
        Computes vertical seam with lowest energy using dynamic programming.
        '''
        n,m = self.width,self.height

        # initializing dp
        dp = [[None]*(n) for _ in range(m)]
        record = [[None]*(n) for _ in range(m)]
        energy_mat = self.scharr_energy_mat()
        for j in range(n):
            dp[0][j]=energy_mat[0][j]
            record[0][j]=[0,j]
            
        for i in range(1,m):
            for j in range(n):
                if j>0 and j<n-1:
                    val = min(dp[i-1][j-1],dp[i-1][j],dp[i-1][j+1])
                    if val==dp[i-1][j-1]:
                        record[i][j]=[i-1,j-1]
                    elif val==dp[i-1][j]:
                        record[i][j]=[i-1,j]
                    elif val==dp[i-1][j+1]:
                        record[i][j]=[i-1,j+1]
                elif j==0:
                    val = min(dp[i-1][j],dp[i-1][j+1])
                    if val==dp[i-1][j]:
                        record[i][j]=[i-1,j]
                    if val==dp[i-1][j+1]:
                        record[i][j]=[i-1,j+1]
                elif j==n-1:
                    val = min(dp[i-1][j-1],dp[i-1][j])
                    if val==dp[i-1][j-1]:
                        record[i][j]=[i-1,j-1]
                    if val==dp[i-1][j]:
                        record[i][j]=[i-1,j]
                dp[i][j] = val+energy_mat[i][j]
                
        opt_value = float('inf')
        for j in range(n):
            if dp[m-1][j]<opt_value:
                opt_coordinate=[m-1,j]
                opt_value=dp[m-1][j]
        res=[]
        row=m
        while row>0:
            res.append(opt_coordinate)
            opt_coordinate=record[opt_coordinate[0]][opt_coordinate[1]]
            row-=1
        return res[::-1]
