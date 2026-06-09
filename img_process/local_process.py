import cv2
import numpy as np
import math
from img_process.util import complete_img



def convolutional_mask(image, mask:list[list]):

    height = mask.__len__() 
    width = mask[0].__len__()
    
    height_img, width_img, _ =  image.shape
    if (height % 2) == 0 or (width % 2) == 0 :
        raise Exception("Size filter error! Please select a filter with odd size.")
    
    if(height>height_img) or (width> width_img):
        raise Exception("Size filter error! Please select a filter with lower size.")
    
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_img = gray_img.astype(np.int32)
    
    padding_x = int((height-1)/2)
    padding_y = int((width-1)/2)
    
    completed_img = complete_img(gray_img, padding_x, padding_y)
    
    final_img = []
    for index_x, x in enumerate(completed_img[padding_x:-padding_x]):
        row_list = []

        for index_y,y in enumerate(x[padding_y:-padding_y]):
            filtered_img = []

            for i in range(height):
                for j in range(width):
                    temp = completed_img[index_x + i][index_y + j] * mask[i][j]
                    filtered_img.append(temp)

            row_list.append(sum(filtered_img))
        final_img.append(row_list)

    # Convert final_img to a NumPy array for display
    final_img_array = np.array(final_img, dtype=np.uint32)
    
    return final_img_array

def gaussian_filter(image, mask_size = 3):
    height_img, width_img, _ =  image.shape
    
    if (mask_size % 2) == 0:
        raise Exception("Size filter error! Please select a filter with odd size.")
    
    if(mask_size>height_img) or (mask_size> width_img):
        raise Exception("Size filter error! Please select a filter with lower size.")
    
    padding = int((mask_size-1)/2)
    mask = []
    for y in range(-padding, padding + 1):
        row_list = []

        for x in range(-padding, padding + 1):
            
            distance = math.sqrt(x*x + y*y)
            row_list.append(distance)
        mask.append(row_list)
    
    return convolutional_mask(image, mask)

