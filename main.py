from interface.interface import *
from img_process.pop_mask import *

IMG_PATH = "2_bracos.webp"


def main():
    
    img  = load_image(IMG_PATH)
    print_img_list = []
    print("Image load succesfully")
    
    print_img_list.append((img, "2 braços - original", ""))
    
    filtered_img = median_filter(img)
    
    print_img_list.append((filtered_img, "Imagem Final (Filtro de Mediana)", "gray"))
        
    display_multi_image(print_img_list)
    
if __name__ == "__main__":
    print("Start image processing")
    main()
    