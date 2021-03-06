import os

import math
import pickle

from PIL import Image

BLACK = 0
WHITE = 255

current_dir = os.path.dirname(os.path.abspath(__file__))


class VectorTools:
    # 计算矢量大小
    def magnitude(self, concordance):
        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    # 计算矢量之间的 cos 值
    def relation(self, concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


class CardCaptcha:
    """
    一卡通系统的验证码工具类
    """

    def __init__(self, im):
        """
        :param im: PIL.image对象
        """
        self.im = im.convert('L')
        self._reduce_noise()

    def _reduce_noise(self):

        threshold = 200
        # 去除杂色点
        for x in range(self.im.width):
            for y in range(self.im.height):
                pix = self.im.getpixel((x, y))
                if pix > threshold:
                    self.im.putpixel((x, y), WHITE)
                else:
                    self.im.putpixel((x, y), BLACK)

    def handle_split_image(self):
        # 切割验证码，返回包含五个字符图像的列表
        y_min, y_max = 0, 82
        split_lines = [7, 49, 91, 133, 175, 217]
        ims = [self.rotate_img(self.im.crop([u, y_min, v, y_max])) for u, v in zip(split_lines[:-1], split_lines[1:])]
        return ims

    def rotate_img(self, im):
        """
        根据图像在x轴方向投影大小确定字符的摆放方向
        :param im: PIL.Image object
        :return: rotated Image object
        """
        min_count = 1000
        final_angle = 0
        for angle in range(-45, 45):
            x_count = 0
            ti = im.rotate(angle, expand=True)
            for x in range(ti.width):
                for y in range(ti.height):
                    if ti.getpixel((x, y)) == WHITE:
                        x_count += 1
                        break
            if x_count < min_count:
                min_count = x_count
                final_angle = angle
        im = im.rotate(final_angle, expand=False)
        return im

    @staticmethod
    def buildvector(im):
        d1 = {}
        count = 0
        for i in im.getdata():
            d1[count] = 1 if i > 0 else 0
            count += 1
        return d1

    def _abs_image(self):
        self.im = self.im.cro(self.im.getbbox())

    def crack(self):
        result = []
        v = VectorTools()
        # 装载训练数据集
        with open(os.path.join(current_dir, 'imageset.dat'), 'rb+') as f:
            imageset = pickle.load(f)
        for letter in self.handle_split_image():
            guess = []
            for image in imageset:
                for x, y in image.items():
                    if len(y) != 0:
                        guess.append((v.relation(y[0], self.buildvector(letter)), x))
            guess.sort(reverse=True)
            neighbors = guess[:10]  # 距离最近的十个向量
            class_votes = {}  # 投票
            for neighbor in neighbors:
                class_votes.setdefault(neighbor[-1], 0)
                class_votes[neighbor[-1]] += 1
            sorted_votes = sorted(class_votes.items(), key=lambda x: x[1], reverse=True)
            result.append(sorted_votes[0][0])
        return ''.join(result)

    def __str__(self):
        return self.crack()


if __name__ == "__main__":
    im = Image.open("captchas/12272.gif")
    im.show()
    print(CardCaptcha(im).crack())
