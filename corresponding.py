import numpy as np
import matplotlib.pyplot as plt

#load image as matrix
def load_image_as_matrix(path):
    image = plt.imread(path)
    if image.ndim == 3:  
        image = np.mean(image, axis=2)  
        
    return image

#normalisation of a matrix norm = (value - mean) / (ecart_type + e) to make image comparable
def normalize(matrix):
    return (matrix - np.mean(matrix)) / (np.std(matrix) + 1e-5)

#optimized function to find the position of a small image within a larger image using normalized cross-correlation
def find_subimage_optimized(large_image, small_image, threshold=0.9):
    
    large_image_norm = normalize(large_image)
    small_image_norm = normalize(small_image)

    
    large_h, large_w = large_image.shape
    small_h, small_w = small_image.shape
    
   
    correlation_map = np.zeros((large_h - small_h + 1, large_w - small_w + 1))
    
   # correlation sweep over the large image
    for i in range(correlation_map.shape[0]):
        for j in range(correlation_map.shape[1]):
            sub_matrix = large_image_norm[i:i + small_h, j:j + small_w]
            
            correlation_map[i, j] = np.sum(sub_matrix * small_image_norm)

   # and now we check for the maximum correlation value that would indicate the best match
    max_corr = np.unravel_index(np.argmax(correlation_map), correlation_map.shape)
    max_value = np.max(correlation_map)

    if max_value >= threshold:
        print(f"match found at position: {max_corr} with similarity {max_value}")
        return max_corr
    else:
        print("no strong match found.")
        return None

#load images
large_image = load_image_as_matrix('cheval.jpeg')
small_image = load_image_as_matrix('b1_cheval.png')  

#search for the small image in the large image
position = find_subimage_optimized(large_image, small_image)

#visualization of the result
if position:
    a = plt.imshow(large_image, cmap='gray')
    plt.gca().add_patch(plt.Rectangle((position[1], position[0]), small_image.shape[1], small_image.shape[0], edgecolor='red', facecolor='none', lw=2))
    plt.title('Correspondance trouvée')
    plt.axis('off')
    plt.show()
