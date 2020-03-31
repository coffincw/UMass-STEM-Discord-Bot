import cv2 #requires Aptfile
import numpy as np
from urllib.request import Request, urlopen
from PIL import Image
from overlay import url_to_image
import requests
from io import BytesIO

# face scale, x adjustment, y adjustment
barr_scale = (2.2, 0.625, 0.9375)
liam_scale = (1.7, 0.45, 0.5)
sp_scale = (1.9, 0.55, 0.75)
mar_scale = (2.0, 0.625, 0.85)
tim_scale = (1.7, 0.3, 0.5)

# pastes image "face" on image opened from image_path
def paste_on_face(face_path, image_url, face_scale):
    # open image in opencv format and find the coordinates and dimensions of faces
    image_for_coordinates = open_image_cv(image_url)
    faces = face_coordinates(image_for_coordinates)

    #open the image and face to paste with the Image library
    image = url_to_image(image_url)
    face = Image.open(face_path)

    #check if there were no faces found in the inputed image
    if len(faces) == 0:
        return 0

    for (x, y, w, h) in faces:
        # make a copy of the face to resize
        selected_face = face.copy()

        #set face width and height
        face_width = int(w*face_scale[0])
        face_height = int(h*face_scale[0])

        # resizes to the size of the face in the image
        selected_face = selected_face.resize([face_width, face_height], Image.ANTIALIAS)

        # set x and y position with adjustments for centering
        x_pos = x-int(face_scale[1]*h)
        y_pos = y-int(face_scale[2]*h)

        # paste face onto the inputed image at the specified coordinates
        image.paste(selected_face, (x_pos, y_pos), selected_face)

    return image

# returns a list of the face coordinates and widths and heights of the faces in the inputed image
def face_coordinates(image):
    #sets the cascade file, change this for learning to identify different features
    casc_path = "opencv-data/haarcascade_frontalface_default.xml"

    # Create haar cascade
    face_cascade = cv2.CascadeClassifier(casc_path)

    # grayscale the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.26,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return faces

# opens the url in the form of an opencv image
def open_image_cv(url):
    #download image
    response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))

    # convert to numpy array
    image = np.asarray(bytearray(response.read()), dtype="uint8")

    # read into opencv format
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image
