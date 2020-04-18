import os
import os.path
import glob
from matplotlib.testing.compare import compare_images

base='ify'
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

def test_ify01():
    pass