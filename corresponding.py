import numpy as np
import matplotlib.pyplot as plt

#load image as matrix
def load_image_as_matrix(path):
    image = plt.imread(path)
    if image.ndim == 3:  
        image = np.mean(image, axis=2)  
        
    return image

#normalisation of a matrix
def normalize(matrix):
    return (matrix - np.mean(matrix)) / (np.std(matrix) + 1e-5)


def find_subimage_optimized(large_image, small_image, threshold=0.9):
    
    large_image_norm = normalize(large_image)
    small_image_norm = normalize(small_image)

    
    large_h, large_w = large_image.shape
    small_h, small_w = small_image.shape
    
   
    correlation_map = np.zeros((large_h - small_h + 1, large_w - small_w + 1))
    
   
    for i in range(correlation_map.shape[0]):
        for j in range(correlation_map.shape[1]):
            sub_matrix = large_image_norm[i:i + small_h, j:j + small_w]
            
            correlation_map[i, j] = np.sum(sub_matrix * small_image_norm)

   
    max_corr = np.unravel_index(np.argmax(correlation_map), correlation_map.shape)
    max_value = np.max(correlation_map)

    if max_value >= threshold:
        print(f"Match found at position: {max_corr} with similarity {max_value}")
        return max_corr
    else:
        print("No strong match found.")
        return None


large_image = load_image_as_matrix('autumn.tif')
small_image = load_image_as_matrix('xx.png')  


position = find_subimage_optimized(large_image, small_image)


if position:
    a = plt.imshow(large_image, cmap='gray')
    plt.gca().add_patch(plt.Rectangle((position[1], position[0]), small_image.shape[1], small_image.shape[0], edgecolor='red', facecolor='none', lw=2))
    plt.title('Correspondance trouvée')
    plt.axis('off')
    plt.show()
