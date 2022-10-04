# -*- coding: utf-8 -*-
# %%
from pathlib import Path
import os
from joblib import Parallel, delayed, parallel_backend
import pandas as pd
import requests as req
from tqdm import tqdm
tqdm.pandas(desc="Orz")

DATA_DIR = Path(r'D:\Collections\Data\街景爬取数据\武汉')
INPUT_DIR = Path(DATA_DIR, '采样点')
OUTPUT_DIR = Path(DATA_DIR, 'output')
TILE_DIR = Path(OUTPUT_DIR, 'tile')

# %%

meta_h5_path = Path('./meta.h5')
store = pd.HDFStore(meta_h5_path)
# store.keys()
tile_url_df = store['tile_url']

tile_url_df['search_id'] = tile_url_df.progress_apply(lambda row: '{}{}{}'.format(row['svid'], row['tile_x'], row['tile_y']),
                                             axis=1)
# %%

# 寻找已经爬取的，并从列表中去除


downloaded_id_list = []
for t in TILE_DIR.rglob('*.jpg'):
    tile_x, tile_y = t.stem.split('-')
    svid = t.parent.stem
    search_id = '{}{}{}'.format(svid, tile_x, tile_y)
    downloaded_id_list.append(search_id)

error_id_list = []
with open('./tile_request_error.txt', 'r') as fp:
    for line in fp:
        if line != '\n':
            tile_x, tile_y, svid = line.split('-')
            search_id = '{}{}{}'.format(svid, tile_x, tile_y)
            error_id_list.append(search_id)

if len(downloaded_id_list) != 0:
    print('Find {} downloaded tiles and {} error tiles. Remove.'.format(len(downloaded_id_list), len(error_id_list)))
    drop_list = downloaded_id_list + error_id_list
    drop_index = tile_url_df[tile_url_df.search_id.isin(drop_list)].index
    d_tile_url_df = tile_url_df.drop(drop_index)
else:
    d_tile_url_df = tile_url_df


# %%
# 先创建文件夹
meta_df = store['meta']
def func(svid):
    try:
        svid_path = Path(TILE_DIR, svid)
        if not svid_path.exists():
            svid_path.mkdir()
    except Exception as ex:
        print(svid)

for svid in meta_df.svid:
    func(svid)

# %%
def iter_func(row):
    tile_url, tile_x, tile_y, svid = row['tile_url'], row['tile_x'], row['tile_y'], row['svid']
    if svid == None:
        return
    response = req.get(url=tile_url)
    if response.status_code == 404:
        with open('./tile_request_error.txt', 'a') as fp:
            std_str = '-'.join([str(i) for i in [tile_x, tile_y, svid]])
            fp.write(std_str)
            fp.write('\n')
    else:
        img = response.content
        svid_path = Path(TILE_DIR, svid)

        img_path = Path(svid_path, '{}-{}.jpg'.format(int(tile_x), int(tile_y)))
        with open(img_path, 'wb') as fp:
            fp.write(img)


sample_tag = True
sample_tag = False
if sample_tag:
    sample_df = d_tile_url_df.sample(frac=0.1)
    _df = sample_df
else:
    _df = d_tile_url_df

print('Total: {}'.format(_df.shape[0]))
# n_jobs根据带宽来调试
with parallel_backend('threading', n_jobs=50):
    res = Parallel(verbose=1)(delayed(iter_func)(row) for _, row in _df.iterrows())

# %%
