# -*- coding: utf-8 -*-
# %%
from pathlib import Path
from joblib import Parallel, delayed, parallel_backend
import PIL.Image as Image
import multiprocessing

DATA_DIR = Path(r'D:\Collections\Data\街景爬取数据\武汉')
INPUT_DIR = Path(DATA_DIR, '采样点')
OUTPUT_DIR = Path(DATA_DIR, 'output')
TILE_DIR = Path(OUTPUT_DIR, 'tile')
SV_DIR = Path(OUTPUT_DIR, 'street_view')

for dir in [TILE_DIR, SV_DIR]:
    if not dir.exists():
        dir.mkdir()
# %%

def image_compose(images_root_path, image_names, images_size=512, images_row=2, images_column=8,
                  images_save_path='./final.jpg'):
    """
    定义图像拼接函数
    :param images_root_path: # 图片集根地址
    :param image_names: 获取图片集地址下的所有图片名称
    :param images_size: # 每张小图片的大小
    :param images_row: 图片间隔，也就是合并成一张图后，一共有几行
    :param images_column: 图片间隔，也就是合并成一张图后，一共有几列
    :param images_save_path: 图片转换后的地址
    :return:
    """

    # 简单的对于参数的设定和实际图片集的大小进行数量判断
    if len(image_names) != images_row * images_column:
        raise ValueError("合成图片的参数和要求的数量不能匹配！")

    to_image = Image.new('RGB', (images_column * images_size, images_row * images_size))  # 创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    for y in range(1, images_row + 1):
        for x in range(1, images_column + 1):
            from_image = Image.open(Path(images_root_path, image_names[images_column * (y - 1) + x - 1])).resize(
                (images_size, images_size), Image.ANTIALIAS)
            to_image.paste(from_image, ((x - 1) * images_size, (y - 1) * images_size))
    return to_image.save(images_save_path)  # 保存新图


def worker(dir):
    if dir.is_dir():
        image_root_path = str(dir)
        dir_name = dir.stem

        destination_path = Path(SV_DIR, dir_name)
        if not destination_path.exists():
            destination_path.mkdir(exist_ok=True)

        # # 全景图
        # tile_list = [(x, y) for y in range(1,3) for x in range(0, 8)]
        # image_names = ['{}-{}.jpg'.format(str(tile_x), str(tile_y)) for (tile_x, tile_y) in tile_list]
        # image_compose(images_root_path=image_root_path, image_names=image_names,
        #               images_size=512, images_row=2, images_column=8,
        #               images_save_path=Path(destination_path, '{}-all.jpg'.format(str(dir_name))))

        # 正前方 3 + 4
        tile_list = [(x, y) for y in range(1, 3) for x in range(3, 5)]
        image_names = ['{}-{}.jpg'.format(str(tile_x), str(tile_y)) for (tile_x, tile_y) in tile_list]

        work_tag = True  # 设定 判断标记，如果True，则合成该方向街景
        for image_name in image_names:
            p = Path(image_root_path, image_name)
            if not p.exists():
                work_tag = False
                break

        if work_tag:
            image_compose(images_root_path=image_root_path, image_names=image_names,
                          images_size=512, images_row=2, images_column=2,
                          images_save_path=Path(destination_path, '{}-front.jpg'.format(str(dir_name))))  # 调用函数

        # 正后方 0 + 7
        tile_list = [(x, y) for y in range(1, 3) for x in [7, 0]]
        image_names = ['{}-{}.jpg'.format(str(tile_x), str(tile_y)) for (tile_x, tile_y) in tile_list]

        work_tag = True  # 设定 判断标记，如果True，则合成该方向街景
        for image_name in image_names:
            p = Path(image_root_path, image_name)
            if not p.exists():
                work_tag = False
                break
        if work_tag:
            image_compose(images_root_path=image_root_path, image_names=image_names,
                          images_size=512, images_row=2, images_column=2,
                          images_save_path=Path(destination_path, '{}-back.jpg'.format(str(dir_name))))

        # 左边 1 + 2
        tile_list = [(x, y) for y in range(1, 3) for x in [1, 2]]
        image_names = ['{}-{}.jpg'.format(str(tile_x), str(tile_y)) for (tile_x, tile_y) in tile_list]
        work_tag = True  # 设定 判断标记，如果True，则合成该方向街景
        for image_name in image_names:
            p = Path(image_root_path, image_name)
            if not p.exists():
                work_tag = False
                break
        if work_tag:
            image_compose(images_root_path=image_root_path, image_names=image_names,
                          images_size=512, images_row=2, images_column=2,
                          images_save_path=Path(destination_path, '{}-left.jpg'.format(str(dir_name))))

        # 右边
        tile_list = [(x, y) for y in range(1, 3) for x in [5, 6]]
        image_names = ['{}-{}.jpg'.format(str(tile_x), str(tile_y)) for (tile_x, tile_y) in tile_list]
        work_tag = True  # 设定 判断标记，如果True，则合成该方向街景
        for image_name in image_names:
            p = Path(image_root_path, image_name)
            if not p.exists():
                work_tag = False
                break
        if work_tag:
            image_compose(images_root_path=image_root_path, image_names=image_names,
                          images_size=512, images_row=2, images_column=2,
                          images_save_path=Path(destination_path, '{}-right.jpg'.format(str(dir_name))))

# %%

if __name__ == "__main__":
    cores_num = multiprocessing.cpu_count()


    with parallel_backend('multiprocessing', n_jobs=cores_num):
        res = Parallel(verbose=1)(delayed(worker)(d) for d in TILE_DIR.iterdir())
