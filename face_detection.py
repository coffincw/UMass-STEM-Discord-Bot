import cv2
from urllib.request import urlopen

# pastes image "face" on image opened from image_path
def paste_on_face(face_path, image):
    face = cv2.imread(face_path)
    faces = face_coordinates(image)
    for (x, y, w, h) in faces:
        # resizes to the size of the face in the image
        face_resized = cv2.resize(face, (w, h), interpolation=cv2.INTER_AREA)
        image[x, y] = face_resized
    return image

# returns a list of the face coordinates and widths and heights of the faces in the inputed image
def face_coordinates(image):
    casc_path = "haarcascade_frontalface_default.xml"

    # Create haar cascade
    face_cascade = cv2.CascadeClassifier(casc_path)

    # grayscale the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    return faces

def open_image_cv(url):
    with urlopen(url) as file:
        return cv2.imread(file, mode='RGB')
