from lxml import etree
import requests
import requests.exceptions as req_e
from Time_line_proxy.log import logger
import pandas as pd
import random
import os
import json
import time
from requests.exceptions import ReadTimeout, ConnectionError



class Clawer:
    """定义爬虫基类，普遍包含采集、解析、储存三个功能"""
    def __init__(self, url, params):
        self.url = url
        self.params = params
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'}

    def requestor(self):
        """请求功能"""
        pass

    def scheduler(self):
        """调度功能"""
        pass

    def parser(self):
        """解析有效信息功能"""
        pass

    def conservator(self):
        """保存有效信息功能"""
        pass

    def __str__(self):
        """描述信息"""
        return Clawer.__name__

class User_agents:
    user_agent = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    ]

    def __init__(self):
        self.headers = self.get_user_agent()

    def get_user_agent(self):
        return random.choice(User_agents.user_agent)

class Key_Changer:
    change_num = 0
    def __init__(self,key_list):
        self.key_list = key_list
        self.key_dict = {}

    def process(self):
        if self.change_num < len(self.key_list):
            self.key_dict['key'] = self.key_list[self.change_num]
            self.change_num += 1
            logger.info("========已更换Key=========")
            print("========已更换Key=========")
            return self.key_dict
        else:
            logger.info("========Key已用完，随机选取Key=========")
            self.key_dict['key'] = random.choice(self.key_list)
            return self.key_dict
            # raise Exception("Key is used up")

class Fetch_proxy:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        self.proxys = self.fetch_new_proxyes(5)

    def proxy_vaild(self,proxy_dict):
        url = "http://ip.chinaz.com/getip.aspx"  #用来测试IP是否可用的url
        try:
            r = requests.get(url, proxies=proxy_dict, headers=self.headers, timeout=3, allow_redirects = False)
            if r.status_code == 200:
                print(r.text)
                return (True, proxy_dict)
            else:
                logger.info('_______%s 无效代理________'%r.status_code)
                return (False, )
        except (req_e.ReadTimeout, req_e.ConnectTimeout, req_e.ProxyError,req_e.ConnectionError,req_e.ChunkedEncodingError):
            logger.info('_______连接超时 无效代理________')
            return (False, )


    def fetch_ip181(self, num):
        """抓取http://www.ip181.com/，10分钟更新100个，质量55%"""
        proxyes = []
        url = 'http://www.ip181.com/'
        req = requests.get(url, headers=self.headers)
        html = req.text
        selector = etree.HTML(html)
        tbody = selector.xpath('//tr')
        for line in tbody[1:]:
            tds = line.xpath('td/text()')
            ip = tds[0]
            port = tds[1]
            latency = tds[4].split(' ')[0]
            if float(latency) < 0.5:
                proxy = "%s:%s"%(ip, port)
                proxy_dict = {'http':proxy, 'https':proxy}
                valid_res = self.proxy_vaild(proxy_dict)
                if valid_res[0]:
                    proxyes.append(valid_res[1])
                if len(proxyes) >= num:
                    break
        logger.info('抓取 ip181，有效代理 %d 个'%(len(proxyes)))
        return proxyes

    def fetch_66ip(self, num):
        """抓取http://www.66ip.cn/，质量25%"""
        proxyes = []
        url = "http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
        req = requests.get(url, headers=self.headers)
        html = req.text
        urls = html.split("</script>")[1].split("<br />")
        for u in urls[:-1]:
            if u.strip():
                proxy = u.strip()
                proxy_dict = {'http':proxy, 'https':proxy}
                valid_res = self.proxy_vaild(proxy_dict)
                if valid_res[0]:
                        proxyes.append(valid_res[1])
                if len(proxyes) >= num:
                    break
                else:
                    continue
        logger.info('抓取 66ip，有效代理 %d 个'%(len(proxyes)))
        return proxyes

    def fetch_xici(self, num):
        """抓取http://www.xicidaili.com/，质量10%"""
        page = 1
        proxyes = []
        while len(proxyes) <= num and page <= 2:
            url = "http://www.xicidaili.com/nn/%s" %page
            req = requests.get(url, headers=self.headers)
            html = req.text
            selector = etree.HTML(html)
            tbody = selector.xpath('//tr[@class]')
            for line in tbody:
                tds = line.xpath('td/text()')
                ip = tds[0]
                port = tds[1]
                speed = line.xpath('td[7]/div/@title')[0][:-1]
                latency = line.xpath('td[8]/div/@title')[0][:-1]
    #             print('%s,%s,%s,%s'%(ip, port, speed, latency))
                if float(speed) < 3 and float(latency) < 1:
                    proxy = "%s:%s"%(ip, port)
                    proxy_dict = {'http':proxy, 'https':proxy}
                    valid_res = self.proxy_vaild(proxy_dict)
                    if valid_res[0]:
                        proxyes.append(valid_res[1])
            logger.info('抓取 xicidaili 第 %d 页，有效代理 %d 个'%(page, len(proxyes)))
            page += 1
        return proxyes

    def fetch_kxdaili(self, num):
        """抓取http://www.kxdaili.com/，质量 5%"""
        page = 1
        proxyes = []
        while len(proxyes) <= num and page <= 10:
            url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
            req = requests.get(url,headers=self.headers)
            html = req.text
            selector = etree.HTML(html)
            tbody = selector.xpath('//tr')
            for line in tbody:
                tds = line.xpath('td/text()')
                ip = tds[0]
                port = tds[1]
                latency = tds[4].split(' ')[0]
                if float(latency) < 0.5:
                    proxy = "%s:%s"%(ip, port)
                    proxy_dict = {'http':proxy, 'https':proxy}
                    valid_res = self.proxy_vaild(proxy_dict)
                    if valid_res[0]:
                        proxyes.append(valid_res[1])
            logger.info('抓取 kxdaili 第 %d 页，有效代理 %d 个'%(page, len(proxyes)))
            page += 1
        return proxyes

    def save_proxy(self, res_list):
        df = pd.DataFrame(res_list)
        df.to_csv('proxy.csv')
        logger.info('_______代理已储存________')

    def read_proxy_file(self, csv_path):
        df = pd.read_csv(csv_path)[['http','https']]
        read_dict = df.to_dict(orient='records')
        return read_dict

    def fetch_new_proxyes(self, num):
        crawls = [self.fetch_ip181, self.fetch_66ip, self.fetch_xici, self.fetch_kxdaili]
        valid_proxyes =[]
        if os.path.exists('proxy.csv'):
            local_proxyes = self.read_proxy_file('proxy.csv')
            for proxy in local_proxyes:
                valid_res = self.proxy_vaild(proxy)
                if valid_res[0]:
                    valid_proxyes.append(valid_res[1])
        else:
            pass
        if len(valid_proxyes) < num:
            demand_num = num - len(valid_proxyes)
            logger.info('_______有效代理%s，需要抓取%s________'%(len(valid_proxyes), demand_num))
            for crawl in crawls:
                new_proxyes = crawl(demand_num)
                logger.info('_______抓取新代理%s________'%len(new_proxyes))
                valid_proxyes += new_proxyes
                demand_num = demand_num - len(new_proxyes)
                if demand_num <= 0:
                    logger.info('_______代理抓取完毕，共%s________'%len(valid_proxyes))
                    self.save_proxy(valid_proxyes)
                    break
                else:
                    continue
        return valid_proxyes

    def process(self):
        if self.proxys:
            return self.proxys.pop()
        else:
            self.proxys = self.fetch_new_proxyes(5)
            return False

    def get_proxy(self):
        if len(self.proxys) == 0:
            self.proxys = self.fetch_new_proxyes(5)
            return self.proxys.pop()
        else:
            return self.proxys.pop()






if __name__ == "__main__":
    proxy_clawer = Fetch_proxy()
    for i in range(11):
        print(i)
        print(proxy_clawer.process())



