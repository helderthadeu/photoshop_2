import cv2
import numpy as np

def load_image(path:str):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError("Image file not found: 2_bracos.webp")
    else:
        print("HERE")
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
        
    return img

import matplotlib.pyplot as plt

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
    
def save_pgm_file(imamge, path:str):
    pass

def load_pgm_file(image, path:str):
    pass