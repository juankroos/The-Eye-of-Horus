import numpy as np
import matplotlib.pyplot as plt
import cv2

def carre_englobant(points):
    x_min = np.min(points[:, 0])
    x_max = np.max(points[:, 0])
    y_min = np.min(points[:, 1])
    y_max = np.max(points[:, 1])
    
    width = x_max - x_min
    height = y_max - y_min
    side = max(width, height)
    
    x_corner = x_min - (side - width) / 2
    y_corner = y_min - (side - height) / 2
    
    return x_corner, y_corner, side

def vertical(I):
    m = I.shape[1]
    J = np.zeros_like(I)
    J[:,0], J[:,-1] = I[:,0], I[:,-1]
    for j in range(1,m):
        J[:,j] = np.abs(I[:,j] - I[:, j-1])
    return J

def horizontal(I):
    n = I.shape[0]
    J = np.zeros_like(I)
    J[0,:], J[-1,:] = I[0,:], I[-1,:]
    for j in range(1,n):
        J[j,:] = np.abs(I[j,:] - I[j-1, :])
    return J

def contournaif(I):
    return np.sqrt((horizontal(I))**2 + (vertical(I))**2)


def load_image_as_matrix(path):
    image = plt.imread(path)
    if image.ndim == 3: 
        image = np.mean(image, axis=2)  
        
    return image

def medianfilter(img, k):
    w,h,c = img.shape
    size = k//2

    #processus de remplissage
    _img = np.zeros(shape = (w+2*size, h+2*size, c), dtype = np.float64)
    _img[size:size+w,size:size+h] = img.copy().astype(np.float64)
    dst = _img.copy()
    
    #filtrage
    for x in range(w):
        for y in range(h):
            for z in range(c):
                dst[x+size, y+size, z] = np.median(_img[x:x+k,y:y+k,z])
    dst = dst[size:size+w,size:size+h].astype(np.uint8)
    return dst

def edge_drawing(image):
    # Convertir l'image en niveaux de gris si nécessaire
    if image.ndim == 3:
        image = np.mean(image, axis=2)
    
    # Appliquer un seuillage pour obtenir une image binaire
    threshold = np.mean(image)
    binary_image = (image > threshold).astype(np.uint8) * 255
    
    # Trouver les contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Créer une image pour dessiner les contours
    contour_image = np.zeros_like(image, dtype=np.uint8)
    
    # Dessiner les contours
    cv2.drawContours(contour_image, contours, -1, (255), thickness=1)
    
    return contour_image

# Exemple de points aléatoires
points = np.array([
    [2, 3],
    [5, 10],
    [8, 6],
    [4, 1]
])

# Calcul du carré englobant
x, y, s = carre_englobant(points)
test = load_image_as_matrix('billes.png')
contour_image = edge_drawing(test)

# Tracé
a = plt.imshow(contournaif(test[:,:]), cmap='gray')
#plt.figure(figsize=(6, 6))
#plt.scatter(points[:, 0], points[:, 1], color='blue', label='Points')
plt.gca().add_patch(plt.Rectangle((x, y), s, s, edgecolor='red', facecolor='none', lw=2, label='Carré englobant'))
#plt.title("Carré englobant autour des points")
#plt.xlabel("x")
#plt.ylabel("y")
#plt.legend()
#plt.axis('equal')
#plt.grid(True)
plt.show()