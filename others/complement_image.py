import cv2
import numpy as np
from models.models import ImageMatrix

def invert_image(image_matrix: ImageMatrix) -> ImageMatrix:
    """
    Computes the complement (negative) of an 8-bit grayscale image.
    Each pixel value 'v' is transformed into '255 - v'.
    
    Parameters:
    - image_matrix (ImageMatrix): The input 2D list representing the image pixels.
    
    Returns:
    - ImageMatrix: A new 2D list representing the inverted (negative) image.
    """
    # Get image dimensions
    height: int = len(image_matrix)
    width: int = len(image_matrix[0]) if height > 0 else 0
    
    # Initialize a new matrix for the output inverted image
    output_matrix: ImageMatrix = [[0] * width for _ in range(height)]
    
    for row in range(height):
        for col in range(width):
            # Invert the pixel intensity
            output_matrix[row][col] = 255 - image_matrix[row][col]
            
    return output_matrix