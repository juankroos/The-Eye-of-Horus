import cv2
import numpy as np
from matplotlib import pyplot as plt

# funtion to apply a filter to an image
def load_image_as_matrix(path):
    image = plt.imread(path)
    # convert to grayscale if it's a color image
    if image.ndim == 3:
        image = np.mean(image, axis=2)
    return image

b = load_image_as_matrix('autumn.tif')
plt.imshow(b)
plt.imsave('aaa.png',b)
b1 = b[50:100,75:100]
plt.imsave('b1.png',b1)
plt.imshow(b1)
plt.savefig("pixeled_one")