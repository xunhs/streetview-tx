# -*- coding: utf-8 -*-
# %%
from pathlib import Path
import os
from joblib import Parallel, delayed, parallel_backend
import pandas as pd
from TecentStreetViewDownloaderV2.CoordinateTransctionTools import wgs2gcj
import requests as req

DATA_DIR = Path(r'D:\Collections\Data\街景爬取数据\武汉')
INPUT_DIR = Path(DATA_DIR, '采样点')
OUTPUT_DIR = Path(DATA_DIR, 'output', )

key = 'K76BZ-W3O2Q-RFL5S-GXOPR-3ARIT-6KFE5'
output_format = 'json'
query_base_url = 'https://sv.map.qq.com/xf?lat={lat}&lng={lng}&r=200&key={key}&output={output_format}&pf=jsapi&ref=jsapi&cb=qq.maps._svcb2.cbjxjooc8y5'
level = 0
tile_base_url = 'https://sv0.map.qq.com/tile?svid={svid}&x={tile_x}&y={tile_y}&from=web&level={level}&v=2'

# %%

# 坐标集合
points_path = Path(INPUT_DIR, 'WHRoadPntSamples.csv')
points_df = pd.read_csv(points_path, header=0)

points_df['uuid'] = points_df['id'].apply(int)

# 坐标转换
func = lambda row: wgs2gcj(row['wgs_lat'], row['wgs_lon'])
points_df['gcj_lat'], points_df['gcj_lon'] = zip(*points_df.apply(func, axis=1))

# %%

'''
来源于-街景拾取器
通过坐标查询svid等相关信息
注： 此处坐标为：腾讯地图坐标系？
    key值姑且不变
    output可选项json

demo_url = https://sv.map.qq.com/xf?lat=30.611174806403625&lng=114.42840103787603&r=200&key=K76BZ-W3O2Q-RFL5S-GXOPR-3ARIT-6KFE5&output=jsonp&pf=jsapi&ref=jsapi&cb=qq.maps._svcb2.cbjxjooc8y5

'''


def iter_func(row):
    metadata_url = query_base_url.format(
        lat=str(row['gcj_lat']),
        lng=str(row['gcj_lon']),
        key=key,
        output_format=output_format)
    response = req.get(url=metadata_url)

    response_json = None
    if response.status_code == 200:
        response_json = response.json()
    else:
        with open('meta_request_error.txt', 'a') as fp:
            std_str = '-'.join([row['id'], row['gcj_lat'], row['gcj_lon']])
            fp.write(std_str)
            fp.write('\n')
        return

    '''
    response_json sample:ss
    {'detail': {'get_way': 1, 'heading': 85, 'pitch': 0, 'road_name': 'NA', 'src': '1', 'svid': '10141019121231110908700', 
    'x': 12735087.78, 'y': 3570390.62, 'zoom': 1}, 'info': {'errno': 0, 'type': 1}}
    '''
    detail = response_json.get('detail')
    svid = detail.get('svid')
    road_name = detail.get('road_name', '')
    # 构建图片下载url
    tile_list = [(x, y) for y in range(1, 3) for x in range(0, 8)]
    image_dict_list = []
    for (tile_x, tile_y) in tile_list:
        image_dict = {}
        tile_url = tile_base_url.format(
            svid=str(svid),
            tile_x=str(tile_x),
            tile_y=str(tile_y),
            level=str(level))
        image_dict['tile_x'] = tile_x
        image_dict['tile_y'] = tile_y
        image_dict['tile_url'] = tile_url
        image_dict['svid'] = svid
        image_dict_list.append(image_dict)
        meta_dict = {'svid': svid, 'road_name': road_name,
                     'gcj_lat': row['gcj_lat'], 'gcj_lon': row['gcj_lon'],
                     'wgs_lat': row['wgs_lat'], 'wgs_lon': row['wgs_lon'], }
    return meta_dict, image_dict_list



# meta_dict_list = []
# tile_url_list = []
#
# ptqdm = tqdm(total=points_df.shape[0])
# for _, row in points_df.iterrows():
#     meta_dict, image_dict_list = iter_func(row)
#     meta_dict_list.append(meta_dict)
#     tile_url_list.extend(image_dict_list)
#     ptqdm.update(1)
# ptqdm.close()

# rows = [row for _, row in points_df.iterrows()]

with parallel_backend('threading', n_jobs=50):
    res = Parallel(verbose=1)(delayed(iter_func)(row) for _, row in points_df.iterrows())



# %%

meta_dict_list = []
tile_url_list = []

for (meta_dict, image_dict_list) in res:
    meta_dict_list.append(meta_dict)
    tile_url_list.extend(image_dict_list)


meta_df = pd.DataFrame(meta_dict_list)
tile_url_df = pd.DataFrame(tile_url_list)
meta_h5_path = Path('./meta.h5')
if meta_h5_path.exists():
    os.remove(meta_h5_path)
store = pd.HDFStore(meta_h5_path)
# 将 Series 或 DataFrame 存入 store
store["meta"], store["tile_url"] = meta_df, tile_url_df
print(store.keys())
store.close()
# %%
