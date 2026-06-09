import cv2
import numpy as np
from img_process.util import complete_img


def difference_between_grey_images(img1, img2):

    height = min(len(img1), len(img2))
    width = min(len(img1[0]), len(img2[0]))

    if len(img1) != len(img2) or len(img1[0]) != len(img2[0]):
        print(
            f"Aviso: as imagens possuem tamanhos diferentes.\n"
            f"Imagem 1: ({len(img1)}, {len(img1[0])})\n"
            f"Imagem 2: ({len(img2)}, {len(img2[0])})\n"
            f"Comparando apenas a região comum ({height}x{width})."
        )

    diff_img = []

    for i in range(height):
        row = []

        for j in range(width):
            diff = abs(
                int(img1[i][j]) -
                int(img2[i][j])
            )

            row.append(diff)

        diff_img.append(row)

    return diff_img


def difference_between_colored_images(img1, img2):
    height = min(len(img1), len(img2))
    width = min(len(img1[0]), len(img2[0]))

    if len(img1) != len(img2) or len(img1[0]) != len(img2[0]):
        print(
            f"Aviso: as imagens possuem tamanhos diferentes.\n"
            f"Imagem 1: ({len(img1)}, {len(img1[0])}, 3)\n"
            f"Imagem 2: ({len(img2)}, {len(img2[0])}, 3)\n"
            f"Comparando apenas a região comum ({height}x{width})."
        )

    diff_img = []

    for i in range(height):
        row = []

        for j in range(width):

            pixel = []

            for c in range(3):  # B, G, R
                diff = abs(
                    int(img1[i][j][c]) -
                    int(img2[i][j][c])
                )

                pixel.append(diff)

            row.append(pixel)

        diff_img.append(row)

    return diff_img