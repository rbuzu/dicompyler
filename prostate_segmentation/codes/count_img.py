import os

import numpy as np


PathDicom = '../data/test/'
dcm_dict = dict()

img_1 = 143
img_2 = 179
img_3 = 208

count = 0
for dirName, subdirList, fileList in os.walk(PathDicom):
    if any(".dcm" in s for s in fileList):
        print(count) 

        ptn_name = dirName.split('/')[3]
        fileList = list(filter(lambda x: '.dcm' in x, fileList))
        indice = [ int( fname[:-4] ) for fname in fileList]
        indice = sorted(indice)

        for filename in np.sort(fileList):
            print(count)
            count +=1
            if count >= img_1:
                print(ptn_name)
                import sys
                sys.exit()

