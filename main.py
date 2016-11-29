#!/usr/bin/env python
#-*- coding: utf-8 -*-


from multiprocessing import Pool
from area_extract import get_area_urls
from page_parsing import get_house_list, get_house_info, house_list, house_info


#判断还有多少房子详细信息未被抓取
db_list = [i['url'] for i in house_list.find()]
db_info = [i['url'] for i in house_info.find()]
x = set(db_list)
y = set(db_info)
undone = x - y

#主函数
def get_all_house_list(area, stop_time=1.1):
    for num in range(1, 10000):
        temp = get_house_list(area, page=num, stop_time=stop_time)
        if temp != 0:
            continue
        else:
            break


#实现多进程
if __name__ == '__main__':
    pool = Pool()
    #pool.map(get_all_house_list, [i for i in get_area_urls('sz').values()])
    pool.map(get_house_info, undone)
    pool.close()
    pool.join()
