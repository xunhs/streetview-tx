
1. 数据准备：RoadPntSamples.csv 
主要字段：id，wgs_lon，wgs_lat （其他坐标也可以，有转换函数CoordinateTransctionTools）,腾讯地图用的是gcj坐标
2. 运行GetTecentStreetViewMetadata.py, 获取元数据 meta.h5，其中包含两个主要的DataFrame：meta_df 和 tile_url_df
meta_df主要字段:svid, wgs_lon，wgs_lat, gcj_lon, gcj_lat
tile_url_df主要字段：svid, tile_x, tile_y, tile_url
3. 运行GetImgFromMeta.py， 下载街景tile
4. 运行Tile2GSV.py拼接tile，合成完整Street View

建议PyCharm逐步运行