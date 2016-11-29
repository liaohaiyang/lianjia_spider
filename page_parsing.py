#!/usr/bin/env python
#-*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from area_extract import hds
import requests
import time
import random
import pymongo
import re


client = pymongo.MongoClient('localhost', 27017)
lianjia = client.lianjia
house_list =lianjia.house_list
house_info = lianjia.houes_info

#房子概要信息抓取
def get_house_list(area, page=1, stop_time=1,):
#    http://sz.lianjia.com/xiaoqu/luohuqu/pg1/
    list_view = area + 'pg{}'.format(str(page))
    wb_data = requests.get(list_view, headers=hds[random.randint(0, len(hds)-1)])
    wb_data.encoding = 'utf-8'
    time.sleep(stop_time)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    if not soup.find('div', 'house-lst-page-box'):         #检查是否存在下一页，不存在返回0， 方便主函数判断中断
        return 0
    titles_list = soup.select('div.title > a')
    average_price_list = soup.select('div.totalPrice > span')
    sell_count_list = soup.select('a.totalSellCount > span')
    position_info_list = soup.find_all('div', 'positionInfo')
    year_built_list = soup.find_all('div', 'positionInfo')
    metro_list = soup.find_all('div', 'tagList')
    house_dynamic_list = soup.find_all('div', 'houseInfo')
    imgs = soup.find_all('img', 'lj-lazy')
    for title, average_price, sell_count, position_info, \
        year_built, metro, house_dynamic, img in zip(titles_list, average_price_list, sell_count_list, position_info_list, \
                                                   year_built_list, metro_list, house_dynamic_list, imgs):
        data = {
            'title': title.get_text(),      #小区名称
            'average_price': average_price.get_text(),      #小区平均价格
            'sell_count': sell_count.get_text(),        #在售二手房数量
            'position_info': list(position_info.stripped_strings)[:-1],     #区域位置
            'built_in': list(year_built.stripped_strings)[-1].strip('/\xa0'),       #建成年份
            'metro': metro.get_text().strip(),      #是否地铁线路附近
            'sale_in_90_days': re.search(r'\d+\w+(\d+)', house_dynamic.find_all('a')[-2].get_text()).group(1),      #90天内成交
            'rent': house_dynamic.find_all('a')[-1].get_text(),     #正在出租数量
            'type_count': house_dynamic.find_all('a')[-3].get_text() if len(house_dynamic.find_all('a')) == 3 else None,        #户型数量
            'img': img.get('data-original') if img.get('data-original') else None,      #小区缩略图
            'house_number': title.get('href').split('/')[-2],       #小区编号
            'url': title.get('href'),       #小区详细页
        }
        print(data)
        #house_list.insert_one(data)

#房子详细信息抓取
def get_house_info(house_url, stop_time=1,):
#    http://sz.lianjia.com/xiaoqu/2411050506921/
    wb_data = requests.get(house_url, headers=hds[random.randint(0, len(hds) - 1)])
    wb_data.encoding = 'utf-8'
    time.sleep(stop_time)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    data = {
        'title': soup.find('h1', 'detailTitle').get_text(),     #小区名称
        'address': soup.find('div', 'detailDesc').get_text(),       #小区地址
        'average_price': soup.find('span', 'xiaoquUnitPrice').get_text() if soup.find('span', 'xiaoquUnitPrice') else None,     #小区平均价格
        'follow': soup.find('span', {'data-role': 'followNumber'}).get_text(),      #所在链家网关注度
        'house_number': house_url.split('/')[-2],       #小区编号
        'year_built': soup.select('div.xiaoquInfo > div:nth-of-type(1) > span.xiaoquInfoContent')[0].get_text(),        #建成年份
        'building_type': soup.select('div.xiaoquInfo > div:nth-of-type(2) > span.xiaoquInfoContent')[0].get_text().strip(),     #建筑类型
        'property_fee': soup.select('div.xiaoquInfo > div:nth-of-type(3) > span.xiaoquInfoContent')[0].get_text(),      #物业费用
        'property_management_company': soup.select('div.xiaoquInfo > div:nth-of-type(4) > span.xiaoquInfoContent')[0].get_text(),       #物业公司
        'developers': soup.select('div.xiaoquInfo > div:nth-of-type(5) > span.xiaoquInfoContent')[0].get_text(),        #开发商
        'big_count': soup.select('div.xiaoquInfo > div:nth-of-type(6) > span.xiaoquInfoContent')[0].get_text(),     #楼栋总数
        'small_count': soup.select('div.xiaoquInfo > div:nth-of-type(7) > span.xiaoquInfoContent')[0].get_text(),       #房屋总数
        'nearby': list(soup.select('div.xiaoquInfo > div:nth-of-type(8) > span.xiaoquInfoContent')[0].stripped_strings),        #附近链家门店
        'img': [i.get('data-src') for i in soup.find('ol', {'id': 'overviewThumbnail'}).find_all('li')] if soup.find('ol', {'id': 'overviewThumbnail'}).find_all('li') else None,       #小区缩略图列表
        'url': wb_data.url,     #小区详细页
    }
    print(data)
    house_info.insert_one(data)


if __name__ == '__main__':
    get_house_list('http://sz.lianjia.com/xiaoqu/pingshanxinqu/')
    #get_house_info('http://sz.lianjia.com/xiaoqu/2411050506921/')
