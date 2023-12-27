from random import randint
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from faker import Faker
import os

def validate_leader(strs):
    if len(strs) < 2 or len(strs) > 4:
        raise ValueError(u'姓名长度2~4个中文')

    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            raise ValueError(u'姓名只能为中文')


class Leave():
    def __init__(self, name) -> None:
        self.leader = name

    def getChars(self):
        if len(self.leader) == 2:
            chars = self.leader + '之印'
        elif len(self.leader) == 3:
            chars = self.leader + '印'
        else:
            chars = self.leader
        return chars

    def generate_stamp(self, save_path):
        """ 生成印章算法 """
        img = Image.new("RGBA", (200, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(((0, 0), (200, 200)), 16, outline='red', width=8)

        chars = self.getChars()
        font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 92, encoding="utf-8")
        draw.text((98, 8), chars[0], fill='red', font=font)
        draw.text((98, 98), chars[1], fill='red', font=font)
        draw.text((2, 8), chars[2], fill='red', font=font)
        draw.text((2, 98), chars[3], fill='red', font=font)

        wl_path = 'wl2.jpg'
        img_wl = Image.open(wl_path)
        pos_random = (randint(100, 200), randint(120, 200))
        box = (pos_random[0], pos_random[1], pos_random[0] + 400, pos_random[1] + 200)
        img_wl_random = img_wl.crop(box)
        img_wl_random = img_wl_random.resize(img.size).convert('L').filter(ImageFilter.GaussianBlur(1))

        X, Y = img.size
        for x in range(X):
            for y in range(Y):
                dot = (x, y)
                img.putpixel(dot,
                             img.getpixel(dot)[:3] + (int(img_wl_random.getpixel(dot) / 255 * img.getpixel(dot)[3]),))

        self.img = img.filter(ImageFilter.GaussianBlur(0.6)) # 进行一次高斯模糊，提高真实度

        self.save_path = save_path
        img.save(self.save_path)

def generate_name(my_fake):
    return my_fake.name()

my_fake = Faker("zh-CN")
save_path = "xxxxx"
# # STXINWEI.TTF  simsun.ttc  STXINGKA.TTF  FZSTK.TTF
for _ in range(1):
    name = generate_name(my_fake)
    stamp = Leave(name)
    stamp.generate_stamp(os.path.join(save_path, name+"##simsun_stamp_square.png"))
