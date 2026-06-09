import cv2
import matplotlib.pyplot as plt
import numpy as np

def generate_histogram(image):
    gray_img = np.array(image)
    if gray_img.ndim == 3:
        gray_img = cv2.cvtColor(gray_img, cv2.COLOR_BGR2GRAY)

    histogram = [0] * 256

    for row in gray_img:
        for pixel in row:
            intensity = _clamp_to_byte(pixel)
            histogram[intensity] += 1

    return histogram

def normalize_histogram(histogram):
    total_pixels = sum(histogram)
    if total_pixels == 0:
        return [0] * len(histogram)

    return [count / total_pixels for count in histogram]

def histogram_matching(image1, image2):
    source_histogram = generate_histogram(image1)
    target_histogram = generate_histogram(image2)

    source_cdf = _cumulative_distribution(normalize_histogram(source_histogram))
    target_cdf = _cumulative_distribution(normalize_histogram(target_histogram))
    mapping = _build_matching_map(source_cdf, target_cdf)

    gray_image = np.array(image1)
    if gray_image.ndim == 3:
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)

    matched_image = []
    for row in gray_image:
        matched_row = []
        for pixel in row:
            intensity = _clamp_to_byte(pixel)
            matched_row.append(mapping[intensity])
        matched_image.append(matched_row)

    if isinstance(image1, np.ndarray):
        return np.array(matched_image, dtype=np.uint8)

    return matched_image

def plot_histogram(hiistogram, title="Histograma", ylabel="Frequencia"):
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(hiistogram)), hiistogram, width=1.0, color="black")
    plt.title(title)
    plt.xlabel("Intensidade")
    plt.ylabel(ylabel)
    plt.xlim(0, len(hiistogram) - 1)
    plt.tight_layout()
    plt.show()

def _clamp_to_byte(value):
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)


def _cumulative_distribution(normalized_histogram):
    cumulative = []
    total = 0

    for probability in normalized_histogram:
        total += probability
        cumulative.append(total)

    return cumulative


def _build_matching_map(source_cdf, target_cdf):
    mapping = [0] * 256
    target_index = 0

    for source_index in range(256):
        while (
            target_index < 255
            and target_cdf[target_index] < source_cdf[source_index]
        ):
            target_index += 1

        if target_index == 0:
            mapping[source_index] = target_index
            continue

        previous_distance = abs(source_cdf[source_index] - target_cdf[target_index - 1])
        current_distance = abs(source_cdf[source_index] - target_cdf[target_index])
        mapping[source_index] = (
            target_index - 1
            if previous_distance < current_distance
            else target_index
        )

    return mapping

