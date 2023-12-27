import os
import cv2
import numpy as np
from PIL import Image
import random

from seal_generate import generate_salt_noise, add_texture, add_texture2, add_texture3, paste_img


def find_image(path):
    name_list = []
    for maindir, subdir, sonpath_list in os.walk(path):
        for sonpath in sonpath_list:
            sonpath_full = os.path.join(maindir, sonpath)
            print(sonpath_full)
            if sonpath_full.rsplit(".",1)[1].lower() in set(["jpg", "jpeg", "png"]):
                name_list.append(sonpath_full)
    return name_list

# seal100k
color_list1 = [[66,6,0],[122,8,0],[184,15,0],[183,67,56],[189,127,122],
            [215,144,137],[227,66,52],[255,128,128],[255,176,168],[255,200,200]]
# 10k
color_list2 = [[14,6,8],[28,6,12],[184,15,0],[255,128,128],[255,200,200],[227,66,52],[255,66,27]]
color_list = color_list1 + color_list2
def generate_color(image, binary):
    color = random.choice(color_list)[::-1] # BGR
    print(color)
    image[binary == 1] = color
    return image

# scale_list = [1.0, 0.7, 0.5, 0.4] # cicle
# scale_list = [1.0, 0.8, 0.5] # elliptic
scale_list = [1.0, 0.8] # square
def walk_dirs(seal_path, bg_paths, img_save_path, mask_save_path, idx):
    count = 0
    bg_noisy_img = Image.open("wl6.jpg")
    incomplete_img = Image.open("wl3.jpg")
    for file_name in os.listdir(seal_path):
        name = file_name.split(".")[0]
        img_path = os.path.join(seal_path, file_name)

        image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if "circle_stamp" in seal_path or "square_stamp" in seal_path:
            _, binary_origin = cv2.threshold(gray, 250, 1, cv2.THRESH_BINARY_INV)
        else:
            _, binary_origin = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY)
        image = generate_color(image, binary_origin)

        # 添加多余印泥
        noisy_img = image
        if random.random() >= 0.6:
            print("添加多余印泥")
            noisy_img = add_texture3(image, bg_noisy_img, random.randint(5,50))

        # 图片老化
        # pp = random.choice([0,0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]) # cicle
        pp = random.choice([0,0, 0.1, 0.2, 0.3, 0.4, 0.5]) # elliptic & square
        print("老化", pp)
        noisy_img = generate_salt_noise(noisy_img, pixel_p = pp, mode=random.randint(0,2))

        # 添加残缺
        mask = binary_origin*255
        if random.random() >= 0.5:
            print("添加残缺")
            noisy_img, mask = add_texture2(noisy_img, mask, incomplete_img, random.randint(5,50))

        gray = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY)
        noisy_img[binary == 0] = [255,255,255]

        gray = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2GRAY)
        u, counts = np.unique(gray, return_counts=True)
        _, binary = cv2.threshold(gray, min(u), 1, cv2.THRESH_BINARY)

        # 增加透明度
        noisy_img = noisy_img[:,:,::-1]
        alpha = np.full((noisy_img.shape[0], noisy_img.shape[1], 1), 0)
        alpha[binary == 0] = 255
        noisy_img = np.concatenate((noisy_img, alpha), axis=-1)
        noisy_img = noisy_img.astype(np.uint8)
        noisy_img = Image.fromarray(noisy_img)
        mask = Image.fromarray(mask)

        if random.random() >= 0.5:
            angle = random.randint(0,360)
            print("旋转角度", angle)
            noisy_img = noisy_img.rotate(angle, Image.BICUBIC)
            mask = mask.rotate(angle, Image.BICUBIC)
            # 尺度缩放
            scale = random.choice(scale_list)
            w,h = noisy_img.size
            noisy_img = noisy_img.resize((int(w*scale), int(h*scale)), Image.BICUBIC)
            mask = mask.resize((int(w*scale), int(h*scale)), Image.BICUBIC)

        mask = np.array(mask)
        mask[mask > 120] == 255

        bg_imgs = random.sample(bg_paths, 1)
        for bg_p in bg_imgs:
            # print(bg_p)
            bg_name = bg_p.split("/")[-1].split(".")[0]
            bg = Image.open(bg_p)
            res_img = paste_img(noisy_img, bg)

            res_img.save(os.path.join(img_save_path, name+"##"+bg_name+"_img_"+str(idx)+".png"))
            cv2.imwrite(os.path.join(mask_save_path, name+"##"+bg_name+"_mask_"+str(idx)+".png"), mask)

        count += 1


seal_path = "xxxx/square_stamp"
bg_path = "xxxx/bg"
img_save_root = "xxxx/gene_square_stamp"
mask_save_root = "xxxx/gene_square_stamp"
bg_img_list = find_image(bg_path)

# circle/elliptic stamp
# for idx in range(10):
#     for sub_dirs in os.listdir(seal_path):
#         print(sub_dirs)
#         dirs_path = os.path.join(seal_path, sub_dirs)
#         img_save_path = os.path.join(img_save_root, sub_dirs)
#         mask_save_path = os.path.join(mask_save_root, sub_dirs)
#         if not os.path.exists(img_save_path):
#             os.makedirs(img_save_path)
#         if not os.path.exists(mask_save_path):
#             os.makedirs(mask_save_path)
#         walk_dirs(dirs_path, bg_img_list, img_save_path, mask_save_path, idx) 

# square stamp
if not os.path.exists(img_save_root):
    os.makedirs(img_save_root)
if not os.path.exists(mask_save_root):
    os.makedirs(mask_save_root)
for idx in range(1):
    walk_dirs(seal_path, bg_img_list, img_save_root, mask_save_root, idx)       