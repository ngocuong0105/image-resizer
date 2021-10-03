import numpy as np
from PIL import Image
from methodtools import lru_cache
import cv2

class ResizeableImage:
    def __init__(self, image: np.array, protected = set(), removed = set()):
        """Takes a image filename and stores pixels, width and height."""
        self.height, self.width, _= image.shape
        self.pixels = image
        self.protected = protected
        self.removed = removed
        self.const = 5000
        
    def color_seam(self, seam, color=[0,0,255]):
        """Takes a seam (a list of coordinates) and colors it all one color."""
        for i,j in seam:
            self.pixels[i][j] = color

    def remove_seam(self, seam):
        """Takes a seam (a list of coordinates with exactly one pair of
        coordinates per row). Removes pixel at each of those coordinates,
        and slides left all the pixels to its right. Shifts pixels under protection and removal
        accordingly. Decreases the width by 1."""
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

    @lru_cache()
    def energy(self, i, j) -> float:
        """Given coordinates (i,j), returns an energy, or cost associated
        with removing that pixel."""
        # assign high cost for edges and protected cells
        if i==0 or i==self.height-1 or j==0 or j==self.width-1 or (i,j) in self.protected:
            return 5000
        elif (i,j) in self.removed:
            return -5000
        else: 
            return self.distance(self.pixels[i][j-1], self.pixels[i][j+1]) +\
                   self.distance(self.pixels[i-1][j], self.pixels[i+1][j]) +\
                   self.distance(self.pixels[i-1][j-1], self.pixels[i+1][j+1]) +\
                   self.distance(self.pixels[i-1][j+1], self.pixels[i+1][j-1])

    def distance(self, pixelA, pixelB):
        """A distance metric between two pixels, based on their colors."""
        ans = 0
        for i in range(len(pixelA)):
            valueA = pixelA[i]
            valueB = pixelB[i]
            ans += abs(valueA-valueB)
        return ans

    def basic_energy_mat(self):
        mat = [[0]*self.width for _ in range(self.height)] 
        for i in range(self.height):
            for j in range(self.width):
                mat[i][j]=self.energy(i,j)
        return mat
        
    def scharr_energy_mat(self) -> 'np.array[float]':
        b, g, r = cv2.split(self.pixels)
        b_energy = np.absolute(cv2.Scharr(b, -1, 1, 0)) + np.absolute(cv2.Scharr(b, -1, 0, 1))
        g_energy = np.absolute(cv2.Scharr(g, -1, 1, 0)) + np.absolute(cv2.Scharr(g, -1, 0, 1))
        r_energy = np.absolute(cv2.Scharr(r, -1, 1, 0)) + np.absolute(cv2.Scharr(r, -1, 0, 1))
        mat = b_energy+g_energy+r_energy
        for i,j in self.protected:
            mat[i][j] = 3*self.const
        for i,j in self.removed:
            mat[i][j] = -3*self.const
        return mat
        
    def sobel_energy_mat(self) -> 'np.array[float]':
        b, g, r = cv2.split(self.pixels)
        b_energy = np.absolute(cv2.Sobel(b, -1, 1, 0)) + np.absolute(cv2.Sobel(b, -1, 0, 1))
        g_energy = np.absolute(cv2.Sobel(g, -1, 1, 0)) + np.absolute(cv2.Sobel(g, -1, 0, 1))
        r_energy = np.absolute(cv2.Sobel(r, -1, 1, 0)) + np.absolute(cv2.Sobel(r, -1, 0, 1))
        mat = b_energy+g_energy+r_energy
        for i,j in self.protected:
            mat[i][j] = self.const
        for i,j in self.removed:
            mat[i][j] = -self.const
        return mat

    def encodeBytes(self,format:str):
        _, encoded_image = cv2.imencode('.'+format, self.pixels)
        return encoded_image.tobytes()

    def openPilImage(self):
        np_img= cv2.cvtColor(self.pixels,cv2.COLOR_BGR2RGB)
        np_img = np_img.astype(np.uint8)
        return Image.fromarray(np_img)

    # def byteImage(self):
    #     """Returns a PIL Image that is represented by self."""
    #     image = Image.new('RGB', (self.width, self.height))
    #     image.putdata([tuple(self.pixels[i][j]) for i in range(self.height) for j in range(self.width)])
    #     return self._pilImage_to_bytes(image)

    # def _pilImage_to_bytes(self, img:Image):
    #     img_byte_arr = io.BytesIO()
    #     img.save(img_byte_arr, format ='png')
    #     img_byte_arr = img_byte_arr.getvalue()
    #     return img_byte_arr

    def best_seam(self) -> 'list[tuple]':
        '''
        Computes vertical seam with lowest energy.
        '''
        n,m = self.width,self.height

        # initializing dp
        dp = [[None]*(n) for _ in range(m)]
        record = [[None]*(n) for _ in range(m)]
        energy_mat = self.sobel_energy_mat()
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
