import cv2
import numpy as np
from matplotlib import pyplot as plt

# funtion to apply a filter to an image
def apply_filter(image, filter_type='blur', ksize=(5, 5), sigma=1.0):
    if filter_type == 'blur':
        return cv2.GaussianBlur(image, ksize, sigma)
    elif filter_type == 'sharpen':
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)
    elif filter_type == 'edge':
        return cv2.Canny(image, 100, 200)
    else:
        raise ValueError("unsupported filter type. use 'blur', 'sharpen', or 'edge'.")
    

path = 'authumn.tif'
image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
filtered_image = apply_filter(image, filter_type='blur', ksize=(7, 7), sigma=1.5)
plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(image, cmap='gray')
plt.axis('off')