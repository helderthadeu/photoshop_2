from interface.interface import load_image, display_multi_image
from img_process.local_process import apply_convolution
from img_process.pop_mask import (
    apply_average_filter,
    apply_derivative_filter,
    apply_gaussian_filter,
    apply_laplacian_filter,
    apply_median_filter,
)
from others.differences import compute_color_difference
from others.histogram_generator import generate_histogram, normalize_histogram, plot_histogram

SOURCE_IMAGE_PATH = "2_bracos.webp"
MECI_IMAGE_PATH = "meci.png"


def main() -> None:
    source_image = load_image(SOURCE_IMAGE_PATH)
    print("Image loaded successfully.")

    images_to_display = [(source_image, "2 braços - original", "")]

    median_result = apply_median_filter(source_image, 7)
    images_to_display.append((median_result, "Filtro de Mediana", "gray"))

    laplacian_conv_result = apply_convolution(
        source_image,
        [
            [0,  1, 0],
            [1, -4, 1],
            [0,  1, 0],
        ],
    )
    images_to_display.append((laplacian_conv_result, "Filtro Laplaciano Convolucional", "gray"))

    average_result = apply_average_filter(source_image, 5)
    images_to_display.append((average_result, "Filtro de Média", "gray"))

    laplacian_result = apply_laplacian_filter(source_image)
    images_to_display.append((laplacian_result, "Filtro Laplaciano", "gray"))

    meci_image = load_image(MECI_IMAGE_PATH)
    color_difference = compute_color_difference(source_image, meci_image)
    images_to_display.append((color_difference, "Diferença entre Dois Braços e Messi"))

    gaussian_result = apply_gaussian_filter(source_image, 7)
    images_to_display.append((gaussian_result, "Filtro Gaussiano", "gray"))

    derivative_result = apply_derivative_filter(source_image, 7)
    images_to_display.append((derivative_result, "Filtro de Derivada", "gray"))

    display_multi_image(images_to_display)

    histogram = generate_histogram(source_image)
    plot_histogram(histogram, "Histograma", "Frequência")

    normalized_histogram = normalize_histogram(histogram)
    plot_histogram(normalized_histogram, "Histograma Normalizado", "Probabilidade")


if __name__ == "__main__":
    print("Iniciando processamento de imagem.")
    main()
