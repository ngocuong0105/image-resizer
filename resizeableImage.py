import imagematrix

class ResizeableImage(imagematrix.ImageMatrix):

    def best_seam(self):
        n,m = self.width,self.height

        # initializing dp
        dp = [[None]*(n) for _ in range(m)]
        record = [[None]*(n) for _ in range(m)]
        for j in range(n):
            dp[0][j]=self.energy(0,j)
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
                dp[i][j] = val+self.energy(i,j)
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
