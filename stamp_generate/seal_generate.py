import cv2
import numpy as np
from PIL import Image,ImageFilter
from math import pi, cos, sin, tan
from random import randint


def gen_intensity_area(num_point, stages):
    # 线性
    nums_point = list()
    temp = 0
    for i in range(stages):
        temp = temp+0.1*num_point
        nums_point.append(temp)
    nums_point = nums_point[::-1]
    return nums_point


def generate_salt_noise(image, pixel_p, mode=0):
    # 设置添加椒盐噪声的数目比例
    s_vs_p = pixel_p
    # 设置添加噪声图像像素的数目
    amount = 0.1
    h,w = image.shape[:2]
    short_edge = min(h,w)
    noisy_img = np.copy(image)
    num_salt = np.ceil(amount * image.size * s_vs_p)

    if mode == 0:
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
        noisy_img[coords[0],coords[1],:] = [255,255,255]
    elif mode == 1:
        stages = 5
        nums_salt = gen_intensity_area(num_salt, stages)
        step = short_edge//stages
        for i in range(stages):
            num_salt = nums_salt[i]
            coords = [np.random.randint(i*step, i*step+step-1, int(num_salt))]
            coords += [np.random.randint(0, w-1, int(num_salt))]
            noisy_img[coords[0],coords[1],:] = [255,255,255]
    elif mode == 2:
        stages = 5
        nums_salt = gen_intensity_area(num_salt, stages)
        step = short_edge//stages
        for i in range(stages):
            num_salt = nums_salt[i]
            coords = [np.random.randint(0, h-1, int(num_salt))]
            coords += [np.random.randint(i*step, i*step+step-1, int(num_salt))]
            noisy_img[coords[0],coords[1],:] = [255,255,255]

    return noisy_img

def retro_style(img):
    img2 = img.copy()
    height,width, n = img.shape
    for i in range(height):
        for j in range(width):
            b = img[i, j][0]
            g = img[i, j][1]
            r = img[i, j][2]
            # 计算新的图像中的RGB值
            B = int(0.273 * r + 0.535 * g + 0.131 * b)
            G = int(0.347 * r + 0.683 * g + 0.167 * b)
            R = int(0.395 * r + 0.763 * g + 0.188 * b)  # 约束图像像素值，防止溢出
            img2[i, j][0] = max(0, min(B, 255))
            img2[i, j][1] = max(0, min(G, 255))
            img2[i, j][2] = max(0, min(R, 255))
    return img2


def add_texture(img, img_wl):
    # 随机圈一部分纹理图
    pos_random = (randint(0,200), randint(0,100))
    box = (pos_random[0], pos_random[1], pos_random[0]+300, pos_random[1]+300)
    img_wl_random = img_wl.crop(box).rotate(randint(0,360))
    # 重新设置im2的大小，并进行一次高斯模糊
    img_wl_random = img_wl_random.resize(img.size).convert('L').filter(ImageFilter.GaussianBlur(1))

    # 将纹理图的灰度映射到原图的透明度，由于纹理图片自带灰度，映射后会有透明效果，所以fill的透明度不能太低
    L, H = img.size
    for h in range(H):
        for l in range(L):
            dot = (l, h)
            # print(img.getpixel(dot)[:3], img.getpixel(dot)[:3] + (int(img_wl_random.getpixel(dot)/255),))
            img.putpixel(dot, img.getpixel(dot)[:3] + (int(img_wl_random.getpixel(dot)/255*img.getpixel(dot)[3]),))
    # 进行一次高斯模糊，提高真实度
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    return img

def add_texture2(image, binary, img_wl, threshold):
    img = image.copy()
    mask = binary.copy()
    # 随机圈一部分纹理图
    pos_random = (randint(0,200), randint(0,100))
    box = (pos_random[0], pos_random[1], pos_random[0]+300, pos_random[1]+300)
    img_wl_random = img_wl.crop(box).rotate(randint(0,360))
    # 重新设置im2的大小，并进行一次高斯模糊
    img_wl_random = img_wl_random.resize(img.shape[:2]).convert('L').filter(ImageFilter.GaussianBlur(1))
    img_wl_random = np.array(img_wl_random)

    img[img_wl_random < threshold] = [255,255,255]
    mask[img_wl_random < threshold] = 0

    return img, mask

def add_texture3(image, img_wl, threshold):

    img = image.copy()
    img_2D = np.reshape(img,(-1,3))

    # 统计b,g,r 最大像素的值
    b_max =  np.max(img_2D[:,0])+1
    g_max =  np.max(img_2D[:,1])+1
    r_max =  np.max(img_2D[:,2])+1

    img_tuple = (img_2D[:,0],img_2D[:,1],img_2D[:,2])
    nbin = np.array([b_max,g_max,r_max])

    # 将三维数值 双射 到一个一维数据
    xy = np.ravel_multi_index(img_tuple, nbin) # 0.007s
    # 统计这个数组中每个元素出现的个数
    H = np.bincount(xy, minlength=nbin.prod()) # 0.055s
    H_sort = sorted(H, reverse=True)
    H = H.reshape(nbin)

    # 得到最多出现像素在结果中的像素值
    b,g,r = np.where(H == H_sort[1])
    max_value = [b[0],g[0],r[0]]

    # 随机圈一部分纹理图
    pos_random = (randint(0,200), randint(0,100))
    box = (pos_random[0], pos_random[1], pos_random[0]+300, pos_random[1]+300)

    img_wl_random = img_wl.crop(box)

    # 重新设置im2的大小，并进行一次高斯模糊
    img_wl_random = img_wl_random.resize(img.shape[:2]).convert('L').filter(ImageFilter.GaussianBlur(1))
    img_wl_random = np.array(img_wl_random)

    img[img_wl_random < threshold] = list(max_value)

    return img


def paste_img(seal_img, bg_img):
    w,h = seal_img.size
    W,H = bg_img.size
    if W < w or H < h:
        bg_img = bg_img.resize((w*3, h*3), Image.BICUBIC)
        W,H = bg_img.size
    # 高斯模糊看起来更自然
    seal_img = seal_img.filter(ImageFilter.GaussianBlur(1))
    r,g,b,a = seal_img.split()

    pos_random = (randint(0,W-w-1), randint(0,H-h-1))
    bg_img.paste(seal_img, pos_random, mask=a)

    box = (pos_random[0], pos_random[1], pos_random[0]+w, pos_random[1]+h)
    img_random = bg_img.crop(box)

    return img_random
                                               