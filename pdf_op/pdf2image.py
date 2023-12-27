import os
import fitz

def pdf_image3(pdfPath, imgPath, name):

    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.page_count):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 3  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 3
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        if not os.path.exists(imgPath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imgPath)  # 若图片文件夹不存在就创建

        pix._writeIMG(os.path.join(imgPath , name + '_images_%s.jpg' % pg), 1, jpg_quality=1000)  # 将图片写入指定的文件夹内
    return pdfDoc.page_count