import cv2
import numpy as np
from models.models import ImageMatrix

def compute_image_difference(image_a: ImageMatrix, image_b: ImageMatrix) -> ImageMatrix:
    """
    Computes the absolute difference between two grayscale images pixel-by-pixel.
    Both input images must have the exact same dimensions.
    
    Parameters:
    - image_a (ImageMatrix): The first input image matrix.
    - image_b (ImageMatrix): The second input image matrix to subtract from the first.
    
    Returns:
    - ImageMatrix: A new 2D list representing the absolute difference image.
    
    Raises:
    - ValueError: If the dimensions of the two images do not match.
    """
    # Get dimensions of the first image
    height_a: int = len(image_a)
    width_a: int = len(image_a[0]) if height_a > 0 else 0
    
    # Get dimensions of the second image
    height_b: int = len(image_b)
    width_b: int = len(image_b[0]) if height_b > 0 else 0
    
    # Validate that both images have matching dimensions
    if height_a != height_b or width_a != width_b:
        raise ValueError("Images must have identical dimensions to compute difference.")
        
    # Initialize a new matrix for the output difference image
    output_matrix: ImageMatrix = [[0] * width_a for _ in range(height_a)]
    
    for row in range(height_a):
        for col in range(width_a):
            # Compute raw difference
            raw_diff: int = image_a[row][col] - image_b[row][col]
            
            # Apply absolute value to keep it positive, then clamp to 8-bit boundaries
            abs_diff: int = abs(raw_diff)
            
            if abs_diff > 255:
                output_matrix[row][col] = 255
            else:
                output_matrix[row][col] = abs_diff
                
    return output_matrix

def erosion_image(image, element:list[list]):
    pass

def dilation_image(image, element:list[list]):
    pass
