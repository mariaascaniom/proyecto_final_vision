from typing import List
import numpy as np
import imageio
import cv2
import copy
import glob
import os


def load_images(filenames: List) -> List:
    return [imageio.imread(filename) for filename in filenames]

def show_image(img):
    cv2.imshow('Chessboard Corners', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def write_image(dir_path, file_path, img):
    # Check if the directory exists
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)  # Create the directory if it doesn't exist

    filename = os.path.join(dir_path, file_path)
    cv2.imwrite(filename, img)

def get_chessboard_points(chessboard_shape, dx, dy):
    
    chessboard = []

    for i in range(chessboard_shape[1]):
        for j in range(chessboard_shape[0]):
            chessboard.append(np.array([i*dx, j*dy, 0]))
    
    return np.array(chessboard, dtype=np.float32)


if __name__ == "__main__":

    # Cargar imágenes
    imgs_path = [f"foto{i}.jpg" for i in range(1,13)]
    imgs = load_images(imgs_path)   

    # Ver los corners (meter las cornes correspondientes al tablero en la tupla!!!)
    corners = []
    for img in imgs:
        corner = cv2.findChessboardCorners(img, (7,7))
        corners.append(corner)

    #Refinar corners
    #En este caso ponemos 24 porque es lo qeu mide el cuadrado
    corners_copy = copy.deepcopy(corners)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 24, 0.01)

    imgs_gray = [cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) for img in imgs]
    corners_refined = [cv2.cornerSubPix(i, cor[1], (7, 7), (-1, -1), criteria) if cor[0] else [] for i, cor in zip(imgs_gray, corners_copy)]

    pictures = []
    imgs_copy = copy.deepcopy(imgs)

    for img, corners_ind in zip(imgs_copy, corners_refined):
        corners_ind= np.array(corners_ind)
        picture = cv2.drawChessboardCorners(img, (8, 6), corners_ind, True)
        pictures.append(picture)

    dir_path = "./corners/"

    for i in range(len(pictures)):
        picture = pictures[i]

        show_image(picture)
        if i <= 9:
            file_path = f"corner_00{i}.jpg"
        else:
            file_path = f"orner_0{i}.jpg"

        write_image(dir_path, file_path, picture)


    chessboard_points = get_chessboard_points((7, 7), 24, 24)
    # Sacamos los chessboard points para todas las imágenes, no solo para una
    chessboard_points_total = [chessboard_points for i in range(len(imgs))] 

    # Filter data and get only those with adequate detections
    valid_corners = [cor[1] for cor in corners if cor[0]]
    # Convert list to numpy array
    valid_corners = np.asarray(valid_corners, dtype=np.float32)

    rms, intrinsics, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(chessboard_points_total, valid_corners, (7,7), None, None)

    # Obtain extrinsics
    extrinsics = list(map(lambda rvec, tvec: np.hstack((cv2.Rodrigues(rvec)[0], tvec)), rvecs, tvecs))

    # Print outputs
    print("Intrinsics:\n", intrinsics)
    print("Distortion coefficients:\n", dist_coeffs)
    print("Root mean squared reprojection error:\n", rms)


