import cv2
import numpy as np

def complete_img(image, padding):
    height, width, channels = image.shape
    complete_arr = []
    
    for index_x, x in enumerate(image):
        complete_arr.append([0, 0])
        for index_y, y in enumerate(x):
            complete_arr[index_x].append(y[0])
            
        complete_arr[index_x].append(0)
        complete_arr[index_x].append(0)
        
    return complete_arr
        

def median_filter(image, filter_size=5):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if (filter_size % 2) == 1:
        padding = int((filter_size+1)/2)
        
        completed_img = complete_img(image, padding)
        
        final_img = []
        for index_x, x in enumerate(completed_img[padding:-padding]):
            row_list = []

            for index_y,y in enumerate(x[padding:-padding]):
                median_img = []

                for i in range(filter_size):
                    for j in range(filter_size):
                        median_img.append(completed_img[index_x + i - padding][index_y + j - padding])

                median_img.sort()
                row_list.append(median_img[int(((filter_size*filter_size)+1)/2)])
            final_img.append(row_list)

        # Convert final_img to a NumPy array for display
        final_img_array = np.array(final_img, dtype=np.uint8)
    else:
        raise Exception("Size filter error! Please select a filter with odd size.")
    return final_img_array

def avg_filter(image):
    pass

def laplacian_filter(image):
    pass
    