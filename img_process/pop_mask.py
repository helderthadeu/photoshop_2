import cv2
import numpy as np


def median_filter(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    final_img = []
    for index_x, x in enumerate(gray_img[:-5]):
        row_list = []

        for index_y,y in enumerate(x[:-5]):
            median_img = []

            for i in range(5):
                for j in range(5):
                    median_img.append(gray_img[index_x + i][index_y + j])

            median_img.sort()
            row_list.append(median_img[13])
        final_img.append(row_list)

    # Convert final_img to a NumPy array for display
    final_img_array = np.array(final_img, dtype=np.uint8)
    
    return final_img_array

def avg_filter(image):
    pass

def laplacian_filter(image):
    pass
    