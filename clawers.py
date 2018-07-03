from Clawer_Base.clawer_frame import Clawer
from Time_line_proxy.log import logger
import pandas as pd

class Timeline_clawer(Clawer):
    """高徳路径规划爬虫"""
    def __init__(self, url, params):
        Clawer.__init__(self, params)
        self.url = url
        self.key_type = '高德'


    def scheduler(self):
        """根据状态码实现调度"""
        deal_code = ['10000', '10001', '10003', '10004', '10016', '10020','10021','10022', '10023']
        pass_code = ['20800', '20801', '20802', '20803', '20003']
        self.status_dict = {
            "10000": self.status_ok,
            "10001": self.status_change_key,
            "10003": self.status_change_key,
            "10004": self.status_change_user_agent,
            "10010": self.status_change_proxy,
            "10016": self.status_change_user_agent,
            "10020": self.status_change_key,
            "10021": self.status_change_proxy,
            "10022": self.status_change_proxy,
            "10023": self.status_change_key,
            "20003": self.status_pass
        }
        status = self.respond['status']
        infocode = self.respond['infocode']
        print(infocode)

        if infocode in deal_code:
            return self.status_dict[infocode]()
        elif infocode in pass_code:
            self.status_pass()
        else:
            print(infocode)
            logger.info(infocode)
            self.status_invalid_request()

    def status_ok(self):
        return self.parser()
        # self.route = self.respond.get('route')

    def get_duration(self):
        respond = self.process()
        if respond == None:
            logger.info(u'响应为None的链接是%s'%(self.req_url))
        elif respond['duration'] == None:
            logger.info(u'duration为None的链接是%s'%(self.req_url))
        else:
            duration = respond['duration']
            return int(duration)

class Walk_clawer(Timeline_clawer):
    url = 'http://restapi.amap.com/v3/direction/walking?'
    def __init__(self, params):
        Timeline_clawer.__init__(self, Walk_clawer.url, params)

    def parser(self):
        a_dict = {}
        distances = []
        durations = []
        route = self.respond.get('route')
        if route == None:
            self.status_sleep_try()
        else:
            destination = route['destination'].split(',')
            a_dict['lng'] = destination[0]
            a_dict['lat'] = destination[1]
            for i in route['paths']:
                distances.append(float(i['distance']))
                durations.append(float(i['duration']))
            a_dict['distance'] = min(distances)
            a_dict['duration'] = min(durations)
            return a_dict

class Bus_clawer(Timeline_clawer):
    url = 'http://restapi.amap.com/v3/direction/transit/integrated?'
    def __init__(self, params):
        Timeline_clawer.__init__(self, Bus_clawer.url, params)

    def parser(self):
        a_dict = {}
        distances = []
        durations = []
        cost = []
        walking_distance = []
        route = self.respond.get('route')
        destination = route['destination'].split(',')
        a_dict['lng'] = destination[0]
        a_dict['lat'] = destination[1]
        a_dict['taxi_cost'] = route['taxi_cost']
        if self.respond['count'] != '0':
            for i in route['transits']:
                distances.append(float(i['distance']))
                durations.append(float(i['duration']))
                if i['cost']:
                    cost.append(float(i['cost']))
                walking_distance.append(float(i['walking_distance']))
            a_dict['distance'] = min(distances)
            a_dict['duration'] = min(durations)
            if cost:
                a_dict['cost'] = min(cost)
            else:
                a_dict['cost'] = ''
            a_dict['walking_distance'] = min(walking_distance)
        else:
            a_dict['distance'] = ''
            a_dict['duration'] = '9999'
            a_dict['cost'] = ''
            a_dict['walking_distance'] = ''
        return a_dict

class Drive_clawer(Timeline_clawer):
    url = 'http://restapi.amap.com/v3/direction/driving?'
    def __init__(self, params):
        Timeline_clawer.__init__(self, Drive_clawer.url, params)

    def parser(self):
        a_dict = {}
        distances = []
        durations = []
        route = self.respond.get('route')
        orign = self.params['origin'].split(',')
        destination = route['destination'].split(',')
        a_dict['ori_lng'] = orign[0]
        a_dict['ori_lat'] = orign[1]
        a_dict['lng'] = destination[0]
        a_dict['lat'] = destination[1]
        a_dict['taxi_cost'] = route['taxi_cost']
        for i in route['paths']:
            distances.append(float(i['distance']))
            durations.append(float(i['duration']))
        a_dict['distance'] = min(distances)
        a_dict['duration'] = min(durations)
        return a_dict

class Regeocode(Timeline_clawer):
    """将经纬度转换为地址信息"""
    url = 'http://restapi.amap.com/v3/geocode/regeo?'
    def __init__(self, params):
        Timeline_clawer.__init__(self, Regeocode.url, params)

    def parser(self):
        regeocode = self.respond.get('regeocode')
        self.address = regeocode.get('formatted_address')
        addressComponent = regeocode.get('addressComponent')
        self.province = addressComponent.get('province')
        self.city = addressComponent.get('city')
        self.citycode = addressComponent.get('citycode')
        self.district = addressComponent.get('district')
        self.adcode = addressComponent.get('adcode')
        self.township = addressComponent.get('township')
        self.towncode = addressComponent.get('towncode')
        return addressComponent

    def get_citycode(self):
        self.process()
        return self.citycode







class Params(dict):
    """参数基类"""
    params = {'origin':"113.3164230000,23.0634050000",
              'destination':"116.434446,39.90816",
              'output':"JSON",
              'key':"70de561d24ed370ab68d0434d834d106"
              }
    def __init__(self):
        self.update(Params.params)
        super().__init__(self)

    def update_proxys(self, proxys):
        if isinstance(proxys,dict) and proxys.__contains__('proxys'):
            super(Params,self).update(proxys)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'proxys'")

    def update_destination(self, points):
        if isinstance(points,dict) and points.__contains__('destination'):
            super(Params,self).update(points)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'location' and 'radius'")

    def update_origin(self, points):
        if isinstance(points,dict) and points.__contains__('origin'):
            super(Params,self).update(points)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'origin'")

    def update_key(self, keys):
        if isinstance(keys,dict) and keys.__contains__('key'):
            super(Params,self).update(keys)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'key'")

class Recode_params(dict):
    """地址逆转译参数"""
    params = {'location': "113.3164230000,23.0634050000",
              'key': "70de561d24ed370ab68d0434d834d106"
              }
    def __init__(self):
        self.update(Recode_params.params)
        super().__init__(self)

    def update_location(self, points):
        """输入points 为字典"""
        if isinstance(points,dict) and points.__contains__('location'):
            super(Recode_params,self).update(points)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'location' ")

    def update_key(self, keys):
        if isinstance(keys,dict) and keys.__contains__('key'):
            super(Recode_params,self).update(keys)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'key'")




class Walk_params(Params):
    """步行参数"""
    def __init__(self,origin,key):
        Params.__init__(self)
        self.update_origin(origin)
        self.update_key(key)

class Bus_params(Params):
    """公交参数"""
    def __init__(self,origin, key):
        Params.__init__(self)
        self.update_origin(origin)
        self.update_key(key)

    def update_city(self, city):
        if isinstance(city,dict) and city.__contains__('city'):
            super(Params, self).update(city)
        else:
            raise TypeError("Imput is not a dict, or don't have key 'city'")


class Drive_params(Params):
    """驾车参数"""
    def __init__(self,origin, key):
        Params.__init__(self)
        self.update_origin(origin)
        self.update_key(key)
        self.update({'strategy':'10'})


if __name__ == "__main__":
    keys = ['70de561d24ed370ab68d0434d834d106']
    df = pd.read_excel(r'D:\GIS_workspace\威海\服务中心\体育休闲中心.xls')
    df = df.set_index('name')
#     bus_params = {'origin':"116.481028,39.989643",
#               'destination':"116.434446,39.90816",
#               'output':"JSON",
#               'city':'北京',
#               'key':"70de561d24ed370ab68d0434d834d106"
#               }
    city_names = list(df.index)
    res_list = []
    for ord, ori_city in enumerate(city_names):
        for dis_city in city_names[ord+1:]:
            origin_city = '%s,%s' % (df.loc[ori_city, 'lon'], df.loc[ori_city, 'lat'])
            distination_city = '%s,%s' % (df.loc[dis_city, 'lon'], df.loc[dis_city, 'lat'])
            link = '%s - %s'%(ori_city, dis_city)
            print(link)
            print(origin_city)
            print(distination_city)

            drive_params = {'origin': origin_city,
                      'destination': distination_city,
                      'output':"JSON",
                      'strategy':'10',
                      'key':"70de561d24ed370ab68d0434d834d106"
                      }
            drive_clawer = Drive_clawer(drive_params)
            res_dict = drive_clawer.process()
            res_dict['link'] = link
            res_list.append(res_dict)
    res_df = pd.DataFrame(res_list)
    res_df.to_excel(r'D:\GIS_workspace\威海\服务中心\体育休闲中心值.xls')



