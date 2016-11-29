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
            'title': title.get_text(),
            'average_price': average_price.get_text(),
            'sell_count': sell_count.get_text(),
            'position_info': list(position_info.stripped_strings)[:-1],
            'built_in': list(year_built.stripped_strings)[-1].strip('/\xa0'),
            'metro': metro.get_text().strip(),
            'sale_in_90_days': re.search(r'\d+\w+(\d+)', house_dynamic.find_all('a')[-2].get_text()).group(1),
            'rent': house_dynamic.find_all('a')[-1].get_text(),
            'type_count': house_dynamic.find_all('a')[-3].get_text() if len(house_dynamic.find_all('a')) == 3 else None,
            'img': img.get('data-original') if img.get('data-original') else None,
            'house_number': title.get('href').split('/')[-2],
            'url': title.get('href'),
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
        'title': soup.find('h1', 'detailTitle').get_text(),
        'address': soup.find('div', 'detailDesc').get_text(),
        'average_price': soup.find('span', 'xiaoquUnitPrice').get_text() if soup.find('span', 'xiaoquUnitPrice') else None,
        'follow': soup.find('span', {'data-role': 'followNumber'}).get_text(),
        'house_number': house_url.split('/')[-2],
        'year_built': soup.select('div.xiaoquInfo > div:nth-of-type(1) > span.xiaoquInfoContent')[0].get_text(),
        'building_type': soup.select('div.xiaoquInfo > div:nth-of-type(2) > span.xiaoquInfoContent')[0].get_text().strip(),
        'property_fee': soup.select('div.xiaoquInfo > div:nth-of-type(3) > span.xiaoquInfoContent')[0].get_text(),
        'property_management_company': soup.select('div.xiaoquInfo > div:nth-of-type(4) > span.xiaoquInfoContent')[0].get_text(),
        'developers': soup.select('div.xiaoquInfo > div:nth-of-type(5) > span.xiaoquInfoContent')[0].get_text(),
        'big_count': soup.select('div.xiaoquInfo > div:nth-of-type(6) > span.xiaoquInfoContent')[0].get_text(),
        'small_count': soup.select('div.xiaoquInfo > div:nth-of-type(7) > span.xiaoquInfoContent')[0].get_text(),
        'nearby': list(soup.select('div.xiaoquInfo > div:nth-of-type(8) > span.xiaoquInfoContent')[0].stripped_strings),
        'img': [i.get('data-src') for i in soup.find('ol', {'id': 'overviewThumbnail'}).find_all('li')] if soup.find('ol', {'id': 'overviewThumbnail'}).find_all('li') else None,
        'url': wb_data.url,
    }
    print(data)
    house_info.insert_one(data)


if __name__ == '__main__':
    get_house_list('http://sz.lianjia.com/xiaoqu/pingshanxinqu/')
    #get_house_info('http://sz.lianjia.com/xiaoqu/2411050506921/')
