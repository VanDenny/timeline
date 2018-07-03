from Time_line_proxy.clawers import *
from math import radians, cos, sin, asin, sqrt, hypot
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
# from gevent import monkey
# from gevent.threadpool import ThreadPool
import numpy as np
# monkey.patch_all()
from PyQt5 import QtCore, QtGui, QtWidgets

mode_dict = {'步行': {'clawer': Walk_clawer,'params': Walk_params,'accuracy': 50, 'expand_dist': 200, 'result_dist': 100},
             '公交': {'clawer': Bus_clawer, 'params': Bus_params,'accuracy': 200,'expand_dist': 1500, 'result_dist': 500},
             '驾车': {'clawer': Drive_clawer,'params': Drive_params,'accuracy': 500, 'expand_dist': 3000, 'result_dist': 1000}}


class Geo_Point:
    def __init__(self, lng, lat):
        self.lng = lng
        self.lat = lat

    def calc_distance(self,another_point):
        # 将十进制度转化为弧度
        lng1, lat1, lng2, lat2 = map(radians, [self.lng, self.lat, another_point.lng, another_point.lat])
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        h = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        earth_radius = 6371000
        distance = 2 * asin(sqrt(h)) * earth_radius
        return distance

    def convert_to_rect(self,distance):
        # distance 单位为m
        lng_per_meter = 0.00001141
        lat_per_meter = 0.00000899
        lng1 = self.lng - (lng_per_meter * distance)
        lat1 = self.lat - (lat_per_meter * distance)
        lng2 = self.lng + (lng_per_meter * distance)
        lat2 = self.lat + (lat_per_meter * distance)
        return Rectangle(lng1, lat1, lng2, lat2)

    def convert_to_destination(self):
        a_dict = {}
        a_dict['destination'] = str(self.lng)+ ',' + str(self.lat)
        return a_dict

    def convert_to_origin(self):
        a_dict = {}
        a_dict['origin'] = str(self.lng)+ ',' + str(self.lat)
        return a_dict

    def convert_to_location(self):
        a_dict = {}
        a_dict['location'] = str(self.lng) + ',' + str(self.lat)
        return a_dict

class Geo_line:
    def __init__(self,lng1, lat1, lng2, lat2):
        self.point_1 = Geo_Point(lng1, lat1)
        self.point_2 = Geo_Point(lng2, lat2)
        self.length = self.point_1.calc_distance(self.point_2)

    def convert_to_point(self, accuracy):
        divide = int(self.length / accuracy) + 1
        lng_min = min([self.point_1.lng, self.point_2.lng])
        lng_max = max([self.point_1.lng, self.point_2.lng])
        lat_min = min([self.point_1.lat, self.point_2.lat])
        lat_max = max([self.point_1.lat, self.point_2.lat])
        lng_list = np.linspace(lng_min, lng_max, divide)
        lat_list = np.linspace(lat_min, lat_max, divide)
        point_list = [Geo_Point(*i) for i in zip(lng_list, lat_list)]
        return point_list


class Rectangle:
    def __init__(self, lng1, lat1, lng2, lat2):
        self.lng1 = round(lng1, 6)
        self.lat1 = round(lat1, 6)
        self.lng2 = round(lng2, 6)
        self.lat2 = round(lat2, 6)
        self.left_up = Geo_Point(lng1,lat2)
        self.left_down = Geo_Point(lng1,lat1)
        self.right_up = Geo_Point(lng2,lat2)
        self.right_down = Geo_Point(lng2,lat1)
        self.center = Geo_Point((lng1+lng2)/2,(lat1+lat2)/2)
        self.wide = self.calc_wide()
        self.high = self.calc_high()
        self.radius = self.out_circle_radius()

    def calc_wide(self):
        return self.left_up.calc_distance(self.right_up)

    def calc_high(self):
        return self.left_up.calc_distance(self.left_down)

    def out_circle_radius(self):
        radius = hypot(self.wide, self.high)/2
        return radius

    def expand(self, distance, lng1=0, lat1=0, lng2=0, lat2=0):
        # distance 单位为m
        lng_per_meter = 0.00001141
        lat_per_meter = 0.00000899
        ex_lng1 = round([(self.lng1 - (lng_per_meter * distance)), lng1][lng1 != 0],6)
        ex_lng2 = round([(self.lng2 + (lng_per_meter * distance)), lng2][lng2 != 0],6)
        ex_lat1 = round([(self.lat1 - (lat_per_meter * distance)), lat1][lat1 != 0],6)
        ex_lat2 = round([(self.lat2 + (lat_per_meter * distance)), lat2][lat2 != 0],6)

        logger.info('拓展矩形为(%s,%s,%s,%s)'%(ex_lng1, ex_lat1, ex_lng2, ex_lat2))
        return Rectangle(ex_lng1, ex_lat1, ex_lng2, ex_lat2)

    def convert_to_lines(self):
        self.left_line = Geo_line(self.lng1, self.lat1, self.lng1, self.lat2)
        self.right_line = Geo_line(self.lng2, self.lat1, self.lng2, self.lat2)
        self.up_line = Geo_line(self.lng1, self.lat2, self.lng2, self.lat2)
        self.down_line = Geo_line(self.lng1, self.lat1, self.lng2, self.lat1)
        return {'left': self.left_line,
                'right': self.right_line,
                'up': self.up_line,
                'down': self.down_line
                }


    def divided_into_four(self):
        rect_left_down = Rectangle(self.left_down.lng,
                                   self.left_down.lat,
                                   self.center.lng,
                                   self.center.lat)
        rect_right_up = Rectangle(self.center.lng,
                                  self.center.lat,
                                  self.right_up.lng,
                                  self.right_up.lat)
        rect_left_up = Rectangle(self.left_down.lng,
                                 self.center.lat,
                                 self.center.lng,
                                 self.right_up.lat)
        rect_right_down = Rectangle(self.center.lng,
                                  self.left_down.lat,
                                  self.right_up.lng,
                                  self.center.lat)
        return [rect_left_down, rect_right_up, rect_left_up, rect_right_down]

    def convert_to_eight_points(self):
        self.middle_up = Geo_Point(self.center.lng,self.lat2)
        self.middle_down = Geo_Point(self.center.lng,self.lat1)
        self.middle_left = Geo_Point(self.lng1,self.center.lat)
        self.middle_right = Geo_Point(self.lng2, self.center.lat)
        return [self.left_up,
                self.left_down,
                self.right_up,
                self.right_down,
                self.middle_up,
                self.middle_down,
                self.middle_left,
                self.middle_right
               ]


    def convert_to_param_dict(self):
        a_dict = {}
        a_dict['location'] = str(self.center.lat) + ',' + str(self.center.lng)
        a_dict['radius'] = str(self.radius)
        return a_dict

    def convert_to_df_dict(self):
        a_dict = {}
        a_dict['lng'] = self.center.lng
        a_dict['lat'] = self.center.lat
        a_dict['radius'] = self.radius
        return a_dict

class Sample_Generator:
    def __init__(self, origin_point, g_key, mode):
        self.point = origin_point
        self.g_key = g_key
        self.mode = mode
        self.rect = self.point.convert_to_rect(mode_dict[mode]['expand_dist'])
        self.origin_city = point_to_citycode(origin_point, g_key)

    def filter_duration(self, duration, accuracy, expand_dist):
        """获取最大耗时duration, 采样精度为accuracy，矩形扩张圈为expand_dist的抓取范围"""
        # duration 单位为分钟
        line_dict = self.rect.convert_to_lines()
        key_list = ['left', 'down', 'right', 'up']


        def filter_point(point):
            a_clawer = clawer_init(self.point, self.g_key, self.mode)
            a_clawer.params.update_destination(point.convert_to_destination())
            if self.mode == '公交':
                cityinfo = {'city': '广州', 'cityd': '广州'}
                cityinfo['city'] = self.origin_city
                cityinfo['cityd'] = point_to_citycode(point, self.g_key)
                a_clawer.params.update_city(cityinfo)
            return a_clawer.get_duration()

        def filter_edge(line_name):
            line = line_dict[line_name]
            point_list = line.convert_to_point(accuracy)
            pool_lv2 = ThreadPool(8)
            duration_list = pool_lv2.map(filter_point, point_list)
            pool_lv2.close()
            pool_lv2.join()
            none_num = duration_list.count(None)
            try:
                if none_num != 0:
                    for i in range(none_num):
                        duration_list.remove(None)
                if min(duration_list) >= (duration*60):
                    return (line_name, 1)
                else:
                    return (line_name, 0)
            except:
                print(duration_list)

        pool_lv1 = ThreadPool(2)
        bool_list = pool_lv1.map(filter_edge, key_list)
        pool_lv1.close()
        pool_lv1.join()

        # for i in range(bool_list.count(None)):
        #     bool_list.remove(None)
        judge_dict = {'left': [0, self.rect.lng1],
                      'right': [0, self.rect.lng2],
                      'up': [0, self.rect.lat2],
                      'down': [0, self.rect.lat1]
                      }
        link_dict = {'left': 'lng1',
                     'right': 'lng2',
                     'up': 'lat2',
                     'down': 'lat1'
                     }

        bool_values = [i[1] for i in bool_list]
        if min(bool_values) == 0:
            coord = dict(lng1=0, lat1=0, lng2=0, lat2=0)
            for i in bool_list:
                if i[1] == 1:
                    logger.info(u'======已经找到%s边界======'%i[0])
                    coord[link_dict[i[0]]] = judge_dict[i[0]][i[1]]
            self.rect = self.rect.expand(expand_dist,**coord)
            self.filter_duration(duration, accuracy, expand_dist)
        else:
            logger.info(u'======已经找到所有边界======')
            return self.rect

    def filter_radius(self, distance):
        radius_correct = []
        rect_list = [self.rect]
        while rect_list:
            rect = rect_list.pop()
            if rect.radius > distance:
                rect_list.extend(rect.divided_into_four())
            else:
                radius_correct.append(rect)
        logger.info(u"生成少于 %s m采样点 %s 个"%(distance, len(radius_correct)))
        print(u"生成少于 %s m采样点 %s 个"%(distance, len(radius_correct)))
        self.save_as_csv(radius_correct,'d:/radius_correct.csv')
        return radius_correct

    def save_as_csv(self,rect_list,file_path):
        a_list = [i.convert_to_df_dict() for i in rect_list]
        df = pd.DataFrame(a_list)
        df.to_csv(file_path, encoding= 'utf-8')

def point_to_citycode(point,keys):
    location = point.convert_to_location()
    params = Recode_params()
    params.update_location(location)
    recode_clawer = Regeocode(params,keys)
    return recode_clawer.get_citycode()

def clawer_init(point, g_key, mode):
    origin = point.convert_to_origin()
    param_mode = mode_dict[mode]['params']
    key_dict = {'key': g_key[0]}
    thread_params = param_mode(origin, key_dict)
    a_clawer = mode_dict[mode]['clawer'](thread_params, g_key)
    return a_clawer


def main(place_name,point, g_key, mode, path):
    start_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    origin_city = point_to_citycode(point, g_key)
    generator = Sample_Generator(point, g_key, mode)
    generator.filter_duration(60, mode_dict[mode]['accuracy'], mode_dict[mode]['expand_dist'])
    rect_list = generator.filter_radius(mode_dict[mode]['result_dist'])
    def thread_clawer(rect):
        a_clawer = clawer_init(point, g_key, mode)
        a_clawer.params.update_destination(rect.center.convert_to_destination())
        if mode == '公交':
            cityinfo = {'city': '广州', 'cityd': '广州'}
            cityinfo['city'] = origin_city
            cityinfo['cityd'] = point_to_citycode(rect.center,g_key)
            a_clawer.params.update_city(cityinfo)
        return a_clawer.process()
    pool = ThreadPool()
    results = pool.map(thread_clawer, rect_list)
    pool.close()
    pool.join()
    end_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    try:
        df = pd.DataFrame(results)
    except:
        logger.info('%s'%results)
    df.to_csv(path + '/%s_%s_%s_%s.csv'%(place_name, mode, start_time, end_time))
    logger.info('抓取成功，结果已保存')

# class ClawerThread(QtCore.QThread):
#     progressSignal = QtCore.pyqtSignal(float, str)
#     statusSignal = QtCore.pyqtSignal(str)
#     finishSignal = QtCore.pyqtSignal()
#
#     def __init__(self, ):





if __name__ == "__main__":
    a_dict = {
        # '湛江CBD': (110.386677, 21.235136),
        # '天河CBD': (113.333026, 23.120495),
        # '福田CBD': (114.030657, 22.538324),
        '茂南区CBD': (110.929024, 21.644562),
        '南片区CBD_建设中_': (110.929459, 21.649175),
        # '江城区CBD': (111.96681, 21.854052),
        # '蓬江区CBD': (113.084279, 22.617895),
        # '云城区CBD': (112.046295, 22.931489),
        # '端州区CBD': (112.470865, 23.055311),
        # '清城区CBD': (113.030492, 23.707625),
        # '欧浦御龙湾': (113.575603, 24.793524),
        # '石岐区CBD_大信新都汇': (113.247341, 22.67052),
        # '十字门CBD': (113.526414, 22.174303),
        # '九洲城_城市之心': (113.580927, 22.257145),
        # '佛山新城': (113.140384, 22.962309),
        # '季华CBD_建设中_': (113.053983, 22.993636),
        # '南城CBD': (113.727088, 22.977552),
        # '惠城区江北_华贸天地_': (114.41473, 23.104025),
        # '越王大道沿线': (114.720984, 23.769719),
        '汕尾新区CBD_万盛广场_': (115.362296, 22.780107)
        # '新津片区_建设中_': (116.780237, 23.33503),
        # '榕城区CBD_金门龙庭_': (116.372887, 23.563248),
        # '梅江CBD_南门商业广场_': (116.113731, 24.305589),
        # '湘桥区CBD': (116.643753, 23.662817)
    }
    # a_dict = {'广州南站': (113.26908, 22.989033),
    #           '虎门站': (113.673131, 22.861129),
    #           '深圳北站': (113.673131, 22.861129),
    #           '前海湾站': (113.897868, 22.537042),
    #           '机场北站': (113.797299, 22.652712),
    #           '滨海湾站': (113.700712, 22.765153),
    #           '珠海北站': (113.551849, 22.400757),
    #           '中山北站': (113.382768, 22.557043),
    #           '南朗镇站': (113.432948, 22.544041),
    #           '横琴站': (113.54462, 22.136599),
    #           '庆盛站': (113.490336, 22.866953),
    #           '万顷沙站': (113.546924, 22.699854),
    #           '城轨松山湖北站': (113.896687, 22.95779),
    #           '容桂站': (113.312357, 22.751182)}
    # for i in list(a_dict.keys()):
    for i in a_dict:
        point = Geo_Point(*a_dict[i])
        logger.info('_________开始抓取%s________'%i)
        g_key = ['4a8f97b5b29c20bc21e8d58e0122281b',
                 'ceb9aaa9e1692f3ca497b58163e12de7',
                 'd93d6632b7d90134a2d4e949ca69bc1f',
                 '70d06b71c196d7c3e71ed084b6beb014',
                 '95eba7f5e12828d5699e3d19d95659be',
                 'ed15337b525ec9097b1fd35d476b992d',
                 '159e5e70247db21e0884e9fc2cc48a83',
                 '70de561d24ed370ab68d0434d834d106'
                 ]
        mode = '驾车'
        path = 'D:\program_lib\Time_line_proxy'
        # print(point_to_citycode(point,g_key))
        logger.info("高德等时线生成工具V1.0 QQ:575548935")
        main(i, point, g_key, mode, path)
    # bus_params = Bus_params({'origin': '1,2'},{'key': '70de561d24ed370ab68d0434d834d106'},{'city':'北京'})
    # walk_params = Walk_params({'origin': '2,3'},{'key': '70de561d24ed370ab68d0434d834d106'})
    # drive_params = Drive_params({'origin': '3,4'},{'key': '70de561d24ed370ab68d0434d834d106'})
    # print(bus_params)
    # print(walk_params)
    # print(drive_params)
    # ['Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    #  'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    #  'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    #  'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    #  'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    #  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101',
    #  'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    #  'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    #  'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    #  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
    #  'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)']


