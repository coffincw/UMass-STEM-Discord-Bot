import os
import os.path
import glob
import overlay
import filters
from pathlib import Path
from matplotlib.testing.compare import compare_images

base='filters'
tdir = os.path.join('tests','test_images',base)
refd = os.path.join('tests','reference_images',base)

testfiles = [os.path.join(tdir,base+'_intensify.png'),
             os.path.join(tdir,base+'_highlight.png'),
             os.path.join(tdir,base+'_customHighlight.png'),
             os.path.join(tdir,base+'_mirrorY.png'),
             os.path.join(tdir,base+'_mirrorX.png'),
             os.path.join(tdir,base+'_pixelate.png'),
             os.path.join(tdir,base+'_saturate.png')
            ]

for fn in testfiles:
    try:
        os.remove(fn)
    except:
        print('Error removing file "'+fn+'"')


TOLERANCE = 11.0

def test_intensify():

    fname = base+'_intensify.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')
    factor  = 5
    
    output = filters.intensify_image(image,factor)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_highlight():

    fname = base+'_highlight.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')
    
    output = filters.highlight_image(image)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_customHighlight():

    fname = base+'_customHighlight.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')
    red     = 30
    green   = 0
    blue    = 75

    output = filters.custom_edge_highlight_image(image, red, green, blue)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_mirrory():

    fname = base+'_mirrorY.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')

    output = filters.mirror_y(image)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_mirrorx():

    fname = base+'_mirrorX.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')

    output = filters.mirror_x(image)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_pixelate():

    fname = base+'_pixelate.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')
    factor  = 5
    
    output = filters.pixelate_image(image,factor)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_saturate():

    fname = base+'_saturate.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image   = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701320190738038837/zoomarun_final.png')
    factor  = 5
    
    output = filters.saturate_image(image,factor)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None