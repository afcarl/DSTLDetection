import json

import pandas as pd
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon

classType_to_filename = {
    1: '006_VEG_L2_SCRUBLAND',  # 灌木丛
    2: '006_VEG_L5_GROUP_TREES',  # 林地，群树
    3: '006_VEG_L5_STANDALONE_TREES',  # 单树
    4: '007_AGR_L2_CONTOUR_PLOUGHING_CROPLAND',  # 耕地，农田
    5: '007_AGR_L2_ORCHARD',  # 果园
    6: '007_AGR_L6_ROW_CROP'  # 农作物
}


# 读取指定的img对应的class的geojson文件的polygons
def load_geojson_to_polygons(img_id, class_type):
    file = json.load(open('../data/train_geojson_v3/' + img_id + '/' +
                          classType_to_filename.get(class_type) + '.geojson'))
    # print(file)
    polygon_list = list()
    for feature in file['features']:
        # print(len(feature['geometry']['coordinates'][0]))
        # print(Polygon(feature['geometry']['coordinates'][0]))
        polygon_list.append(Polygon(feature['geometry']['coordinates'][0]))
    # print(polygon_list)
    # print(type(MultiPolygon(polygon_list)))
    return MultiPolygon(polygon_list)


# 读取指定的img所有的class的geojson文件的polygons
def load_all_geojson(img_id):
    polygons = dict()
    for class_type in classType_to_filename.keys():
        polygons[class_type] = load_geojson_to_polygons(img_id, class_type)
    return polygons


# 读取指定的img对应的class的csv文件的polygons,注意这里的class与geojson文件的class不同
def load_wkt_to_polygons(img_id, class_type):
    df = pd.read_csv('../data/train_wkt_v4.csv')
    df_image = df[df.ImageId == img_id]
    polygons = df_image[df_image.ClassType == class_type].MultipolygonWKT
    polygon_list = None
    if len(polygons) > 0:
        polygon_list = wkt.loads(polygons.values[0])
    # print(polygon_list)
    return polygon_list


# 读取指定的img所有的class的csv文件的polygons
def load_all_wkt(img_id):
    polygons = dict()
    # 因为wkt共有10类
    for class_type in range(1, 11):
        polygons[class_type] = load_wkt_to_polygons(img_id, class_type)
    return polygons


# 从grid_sizes.csv中读取指定图像的 Xmax 和 Ymin
def get_xmax_ymin(image_id):
    gs = pd.read_csv('../data/grid_sizes.csv', names=['ImageId', 'Xmax', 'Ymin'], skiprows=1)
    xmax, ymin = gs[gs.ImageId == image_id].iloc[0, 1:].astype(float)
    return xmax, ymin


# 得到polygons地理坐标到像素坐标点映射的缩放因子
def get_scales(im_size, x_max, y_min):
    h, w = im_size
    w_ = w * (w / (w + 1))
    h_ = h * (h / (h + 1))
    return w_ / x_max, h_ / y_min
