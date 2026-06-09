from interface.interface import *
from img_process.pop_mask import *
from img_process.local_process import *
from others.differences import *
from others.histrogram_generator import (
    generate_histogram,
    normalize_histogram,
    plot_histogram,
)


IMG_PATH = "2_bracos.webp"
MECI_PATH = "meci.png"


def main():
    
    img  = load_image(IMG_PATH)
    print_img_list = []
    print("Image load succesfully")
    
    print_img_list.append((img, "2 braços - original", ""))
    
    median_img = median_filter(img,7)
    
    print_img_list.append((median_img, "Imagem Final (Filtro de Mediana)", "gray"))
    
    convolutional_img  = convolutional_mask(img, 
                                            [
                                                [0, 1, 0 ],
                                                [1, -4, 1],
                                                [0, 1, 0 ]
                                             ]
                                            )
    
    print_img_list.append((convolutional_img, "Imagem Final (Filtro laplaciano convolucional)", "gray"))
    
    average_img = avg_filter(img, 5)
    print_img_list.append((average_img, "Imagem Final (Filtro de média)", "gray"))
        
    laplacian_img = laplacian_filter(img)
    print_img_list.append((laplacian_img, "Imagem Final (Filtro Laplaciano)", "gray"))

    meci_img = load_image(MECI_PATH)
    diff_img = difference_between_colored_images(img, meci_img)
    print_img_list.append((diff_img, "Diferença entre Dois Braços e Messi"))
    
    gaussian_img = gaussian_filter(img, 7)
    print_img_list.append((gaussian_img, "Imagem Final (Filtro Gaussiano)", "gray"))
    
    display_multi_image(print_img_list)

    histogram = generate_histogram(img)
    plot_histogram(histogram, "Histograma", "Frequencia")
    normalized_histogram = normalize_histogram(histogram)
    plot_histogram(normalized_histogram, "Histograma Normalizado", "Probabilidade")
    
if __name__ == "__main__":
    print("Start image processing")
    main()