# import cv2
# import numpy as np

# def change_bright(image, value):
#     pass

# def limiar_fitler(image, limiar):
#     pass

from models import ImageMatrix

def adjust_brightness(image_matrix: ImageMatrix, bias: int) -> ImageMatrix:
    """
    Adjusts the brightness of a grayscale image by adding a bias value to each pixel.
    """
    height: int = len(image_matrix)
    width: int = len(image_matrix[0]) if height > 0 else 0
    
    output_matrix: ImageMatrix = [[0] * width for _ in range(height)]
    
    for row in range(height):
        for col in range(width):
            new_value: int = image_matrix[row][col] + bias
            
            if new_value > 255:
                output_matrix[row][col] = 255
            elif new_value < 0:
                output_matrix[row][col] = 0
            else:
                output_matrix[row][col] = int(new_value)
                
    return output_matrix


def apply_threshold(image_matrix: ImageMatrix, threshold_value: int) -> ImageMatrix:
    """
    Applies a binary thresholding operation to a grayscale image.
    """
    height: int = len(image_matrix)
    width: int = len(image_matrix[0]) if height > 0 else 0
    
    output_matrix: ImageMatrix = [[0] * width for _ in range(height)]
    
    for row in range(height):
        for col in range(width):
            if image_matrix[row][col] >= threshold_value:
                output_matrix[row][col] = 255
            else:
                output_matrix[row][col] = 0
                
    return output_matrix