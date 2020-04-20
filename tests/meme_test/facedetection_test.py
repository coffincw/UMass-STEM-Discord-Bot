import os
import os.path
import glob
import face_detection
from pathlib import Path
from matplotlib.testing.compare import compare_images

base='facedetection'
tdir = os.path.join('tests','test_images',base)
refd = os.path.join('tests','reference_images',base)

globpattern = os.path.join(tdir,base+'*.png')
oldtestfiles = glob.glob(globpattern)

for fn in oldtestfiles:
    try:
        os.remove(fn)
    except:
        print('Error removing file "'+fn+'"')


TOLERANCE = 11.0

def test_facedetection01():

    fname = base+'01.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image_link = 'https://s.hdnux.com/photos/51/23/24/10827008/3/920x920.jpg'
    scale = face_detection.barr_scale
    path = Path('memes/barrington/barr-face.png')

    print(os.getcwd())
    print(tname)

    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))

    output = face_detection.paste_on_face(path,image_link,scale)
    output.save(tname)

    

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None
    assert 1 == 0

def test_facedetection02():
    fname = base+'02.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image_link = 'https://p1.pxfuel.com/preview/133/768/57/sikhs-india-indians-people-turban-sikhism-smile.jpg'
    scale = face_detection.mar_scale
    path = Path('memes/marius/marius-face.png')

    output = face_detection.paste_on_face(path,image_link,scale)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_facedetection03():
    
    image_link = 'https://p1.pxfuel.com/preview/133/768/57/sikhs-india-indians-people-turban-sikhism-smile.jpg'
    image_for_coordinates = face_detection.open_image_cv(image_link)
    faces = face_detection.face_coordinates(image_for_coordinates)

    reference = [[141, 205, 197, 197],
               [569, 216, 214, 214]]
    
    face_i = 0
    for (x, y, w, h) in faces:
        assert x == reference[face_i][0]
        assert y == reference[face_i][1]
        assert w == reference[face_i][2]
        assert h == reference[face_i][3]
        face_i += 1


