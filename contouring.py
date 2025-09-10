import numpy as np
import matplotlib.pyplot as plt

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

# Exemple de points aléatoires
points = np.array([
    [2, 3],
    [5, 10],
    [8, 6],
    [4, 1]
])

# Calcul du carré englobant
x, y, s = carre_englobant(points)

# Tracé
plt.figure(figsize=(6, 6))
plt.scatter(points[:, 0], points[:, 1], color='blue', label='Points')
plt.gca().add_patch(plt.Rectangle((x, y), s, s, edgecolor='red', facecolor='none', lw=2, label='Carré englobant'))
plt.title("Carré englobant autour des points")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()