#!/usr/bin/env python
#-*- coding: utf-8 -*-


import time
from page_parsing import house_list, house_info


#实时统计抓取数量
while True:
    #print(house_list.find().count())
    print(house_info.find().count())
    time.sleep(1)





