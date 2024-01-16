import numpy as np
from PIL import Image

def pad_image(im, mask):

    w,h = im.size
    if w>=h:
        if (h%2 != 0 and w%2 == 0) or (h%2 == 0 and w%2 != 0):
            w -= 1
        im_new = Image.new(mode='RGB', size=(w,w), color=(255,255,255))
        im_new.paste(im, box=(0, (w-h)//2))
        W,H = im_new.size
        alpha = np.full((im_new.size[1],im_new.size[0]), 0)
        h, w = mask.shape
        alpha[(H-h)//2:(H+h)//2] = mask
    else:
        if (h%2 != 0 and w%2 == 0) or (h%2 == 0 and w%2 != 0):
            h -= 1   
        im_new = Image.new(mode='RGB', size=(h,h), color=(255,255,255))
        im_new.paste(im, box=((h-w)//2, 0))
        W,H = im_new.size
        alpha = np.full((im_new.size[1],im_new.size[0]), 0)
        h, w = mask.shape
        alpha[:,(W-w)//2:(W+w)//2] = mask
    
    alpha = alpha[..., np.newaxis]
    im_new = np.concatenate((im_new, alpha), axis=-1).astype(np.uint8)
    return im_new