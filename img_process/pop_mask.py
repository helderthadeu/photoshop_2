import cv2
import numpy as np
from img_process.util import complete_img


        

def median_filter(image, filter_size=5):
    if (filter_size % 2) == 0:
        raise Exception("Size filter error! Please select a filter with odd size.")
    
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    padding = int((filter_size-1)/2)
    
    completed_img = complete_img(gray_img, padding)
    
    final_img = []
    for index_x, x in enumerate(completed_img[padding:-padding]):
        row_list = []

        for index_y,y in enumerate(x[padding:-padding]):
            median_img = []

            for i in range(filter_size):
                for j in range(filter_size):
                    median_img.append(completed_img[index_x + i][index_y + j])

            median_img.sort()
            row_list.append(median_img[((filter_size*filter_size)+1)//2])
        final_img.append(row_list)

    # Convert final_img to a NumPy array for display
    final_img_array = np.array(final_img, dtype=np.uint8)
    
    return final_img_array

def avg_filter(image, filter_size=5):
    if (filter_size % 2) == 0:
        raise Exception("Size filter error! Please select a filter with odd size.")
    
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_img = gray_img.astype(np.int32)
    padding = int((filter_size-1)/2)
    
    completed_img = complete_img(gray_img, padding)
    
    final_img = []
    for index_x, x in enumerate(completed_img[padding:-padding]):
        row_list = []

        for index_y,y in enumerate(x[padding:-padding]):
            avg_img = []

            for i in range(filter_size):
                for j in range(filter_size):
                    avg_img.append(completed_img[index_x + i][index_y + j])

            row_list.append(sum(avg_img)//(filter_size*filter_size))
        final_img.append(row_list)

    # Convert final_img to a NumPy array for display
    final_img_array = np.array(final_img, dtype=np.uint8)
    
    return final_img_array

def laplacian_filter(image):
    
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_img = gray_img.astype(np.int32)
    padding = 1
    
    completed_img = complete_img(gray_img, padding)
    
    final_img = []
    for index_x, x in enumerate(completed_img[padding:-padding]):
        row_list = []

        for index_y,y in enumerate(x[padding:-padding]):
            filtered_point = completed_img[index_x][index_y-1] + completed_img[index_x][index_y+1] - (2 * completed_img[index_x][index_y])
            row_list.append(filtered_point)

        final_img.append(row_list)

    # Convert final_img to a NumPy array for display
    final_img_array = np.array(final_img, dtype=np.uint8)
    
    return final_img_array
    