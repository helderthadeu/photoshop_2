import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from models.models import ImageMatrix, FilePath

def load_image(path:str):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError("Image file not found: 2_bracos.webp")
    else:
        print("HERE")
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
        
    return img

def display_image(image, title = "", cmap="viridis"):
    plt.imshow(image, cmap=cmap)
    plt.title(title)
    plt.axis("off")

    plt.show()

def display_multi_image(images:list):
    if not images:
        return
    # Accept items as: image, (image, title), or (image, title, cmap)
    imgs = []
    titles = []
    cmaps = []

    for item in images:
        if isinstance(item, tuple):
            if len(item) == 2:
                img, title = item
                cmap = None
            elif len(item) == 3:
                img, title, cmap = item
            else:
                # fallback
                img = item[0]
                title = item[1] if len(item) > 1 else ""
                cmap = None
        else:
            img = item
            title = ""
            cmap = None

        imgs.append(img)
        titles.append(title)
        cmaps.append(cmap)

    total = len(imgs)
    cols = min(3, total)
    rows = (total + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    if isinstance(axes, np.ndarray):
        axes = axes.flatten()
    else:
        axes = [axes]

    for ax, image, title, cmap in zip(axes, imgs, titles, cmaps):
        use_cmap = cmap if cmap not in (None, "") else ("gray" if getattr(image, 'ndim', 3) == 2 else None)
        ax.imshow(image, cmap=use_cmap)
        ax.set_title(title)
        ax.axis("off")

    for ax in axes[total:]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()

def load_pgm_file(image, path:str):
    pass

def select_pgm_file() -> FilePath:
    """
    Opens a file dialog filtered for .pgm files and returns the selected path.
    """
    # Create a hidden tkinter root window to avoid showing an empty main window
    root = tk.Tk()
    root.withdraw()

    # Open the file dialog with a filter for .pgm files
    file_path: FilePath = filedialog.askopenfilename(
        title="Select a PGM File",
        filetypes=[("PGM Files", "*.pgm"), ("All Files", "*.*")]
    )

    if file_path:
        print(f"Selected file: {file_path}")
        return file_path
    else:
        print("No file was selected.")
        return None


def save_pgm_file() -> FilePath:
    """
    Opens a save file dialog enforcing the .pgm extension.
    """
    root = tk.Tk()
    root.withdraw()

    # Open the save dialog suggesting .pgm as the default extension
    file_path: FilePath = filedialog.asksaveasfilename(
        title="Save PGM File",
        defaultextension=".pgm",
        filetypes=[("PGM Files", "*.pgm")]
    )
    
    if file_path:
        print(f"File will be saved to: {file_path}")
        return file_path
    else:
        print("Save operation cancelled.")
        return None
    
def load_pgm_to_matrix(file_path: str) -> ImageMatrix:
    """
    Reads a Plain PGM (P2) file from scratch and converts it into an ImageMatrix.
    
    Parameters:
    - file_path (str): The system path to the target .pgm file.
    
    Returns:
    - ImageMatrix: A 2D list containing integer pixel values.
    """
    with open(file_path, 'r') as file:
        # Read all tokens/words from the file, ignoring newlines and spaces
        tokens = file.read().split()
        
    if not tokens:
        raise ValueError("The selected file is empty.")
        
    # 1. Verify Magic Number (Must be P2 for ASCII Grayscale)
    magic_number = tokens[0]
    if magic_number != "P2":
        raise ValueError(f"Unsupported PGM format '{magic_number}'. Only 'P2' (ASCII) is allowed.")
        
    # 2. Extract Header Data (Width, Height, Max Value)
    # This logic skips any potential comments if they weren't stripped, 
    # but standard .split() handles basic formatting safely if no '#' comments exist.
    width = int(tokens[1])
    height = int(tokens[2])
    max_val = int(tokens[3])
    
    if max_val > 255:
        raise ValueError("Only 8-bit images (Max value <= 255) are supported.")
        
    # 3. Reconstruct the 2D Matrix from the remaining pixel tokens
    pixel_data = tokens[4:]
    
    matrix: ImageMatrix = []
    token_index = 0
    
    for _ in range(height):
        row = []
        for _ in range(width):
            # Convert string token to integer pixel value
            row.append(int(pixel_data[token_index]))
            token_index += 1
        matrix.append(row)
        
    return matrix


def save_matrix_to_pgm(file_path: str, matrix: ImageMatrix) -> None:
    """
    Converts an ImageMatrix back into a definitive P2 PGM file structural string 
    and writes it to the disk.
    
    Parameters:
    - file_path (str): The destination path where the file will be saved.
    - matrix (ImageMatrix): The 2D image matrix to save.
    """
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0
    max_val = 255  # Standard max value for 8-bit grayscale
    
    # Build the structural PGM header string
    header = f"P2\n{width} {height}\n{max_val}\n"
    
    # Convert matrix elements into plain text pixels
    body_lines = []
    for row in matrix:
        # Join all pixel integers in a row with spaces
        line = " ".join(str(pixel) for pixel in row)
        body_lines.append(line)
        
    # Combine header and body content
    full_pgm_content = header + "\n".join(body_lines) + "\n"
    
    # Write the raw structural string directly to the file system
    with open(file_path, 'w') as file:
        file.write(full_pgm_content)