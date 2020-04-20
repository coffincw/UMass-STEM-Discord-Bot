import os
import os.path
import glob
import overlay
from pathlib import Path
from matplotlib.testing.compare import compare_images

base='overlay'
tdir = os.path.join('tests','test_images',base)
refd = os.path.join('tests','reference_images',base)

# globpattern = os.path.join(tdir,base+'*.png')
# oldtestfiles = glob.glob(globpattern)

# for fn in oldtestfiles:
#     try:
#         os.remove(fn)
#     except:
#         print('Error removing file "'+fn+'"')


TOLERANCE = 11.0

def test_overlay01():

    fname = base+'01.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    text    = 'This is a test'
    path    = Path('memes/tim/tdraw.png')
    origin  = overlay.tim_origin

    output = overlay.draw_text(text,path,origin)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_overlay02():

    fname = base+'02.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    text    = 'This is a|multi-line test'
    path    = Path('memes/tim/tdraw.png')
    origin  = overlay.tim_origin

    output = overlay.draw_text(text,path,origin)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None


def test_overlay03():

    fname = base+'03.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image_link  = 'https://s.hdnux.com/photos/51/23/24/10827008/3/920x920.jpg'
    path        = Path('memes/lan/landrew.png')
    origin      = overlay.landrew_origin

    output = overlay.overlay_image(overlay.url_to_image(image_link), path, origin)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_overlay04():

    fname = base+'04.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image       = overlay.url_to_image('https://pngimg.com/uploads/farmer/farmer_PNG59.png')
    ttext       = 'HA'
    btext       = 'Farmer'

    output = overlay.paste_text_top_bottom(ttext, btext, image)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_overlay05():

    fname = base+'05.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image       = overlay.url_to_image('https://cdn.discordapp.com/attachments/501594682820788224/701314537420488714/barrify.png')
    ttext       = 'You know...'
    btext       = 'We could create a student who finishes the homework faster'

    output = overlay.paste_text_top_bottom(ttext, btext, image)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_overlay06():

    fname = base+'06.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    image_link  = 'https://cdn.discordapp.com/attachments/501594682820788224/701087623925465108/barrify.png'

    output = overlay.url_to_image(image_link)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None

def test_overlay07():

    fname = base+'07.png'
    tname = os.path.join(tdir,fname)
    rname = os.path.join(refd,fname)

    path        = Path('memes/arun/zoom-arun.png')
    image_link  = 'https://live.staticflickr.com/7656/26933132905_23c3e806af_b.jpg'

    output = overlay.paste_in_streamer_corner(path,image_link)
    output.save(tname)

    tsize = os.path.getsize(tname)
    print(glob.glob(tname),'[',tsize,'bytes',']')

    rsize = os.path.getsize(rname)
    print(glob.glob(rname),'[',rsize,'bytes',']')

    result = compare_images(rname,tname,tol=TOLERANCE)
    if result is not None:
       print('result=',result)
    assert result is None