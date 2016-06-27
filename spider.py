# -*- coding: utf8 -*-
import requests
import time
import sys
from itertools import combinations_with_replacement

def match(url, keys):
    try:
        r = requests.get(url, timeout=1)
    except:
        return False # 网站访问速度过慢，可能是墙外网站
    r.encoding = 'gbk'
    for key in keys:
        if key in r.text:
            return True
    return False

def generate(min, max):
    source = list('abcdefghijklmnopqrstuvwxyz0123456789')
    for length in xrange(min, max+1):
        for char in combinations_with_replacement(source, length):
            yield ''.join(char)
                
def save_data(filename, datas):
    f = open(filename, 'a')
    for data in datas:
        f.write(''.join([data, '\n']))
    f.close()

if __name__ == '__main__':
    keys = [u'人妻', u'乱伦', u'情色', u' sex ']
    prefix = 'http://'
    suffix = '.com'
    filename = 'urls_5.txt'
    cnt = 0
    start_time = time.time()
    urls_temp = list()
    last_sex_url = ''
    print time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime()),
    print 'the spider is going on ...'
    for hostname in generate(1, 1):
        # 寻找长度为a～b之间的目的网址
        url = ''.join([prefix, hostname, suffix])
        print '\r','Now: ', url, '\tLast H-site: ', last_sex_url, '\tFound: ', cnt,
        sys.stdout.flush()
        if(match(url, keys)):
            cnt += 1
            last_sex_url = url
            urls_temp.append(url)
            if(len(urls_temp) == 10):
                # 每找到10个网站保存一次
                save_data(filename, urls_temp)
                urls_temp = list()
    end_time = time.time()
    used_hour = round((end_time - start_time) / 3600, 2)
    print time.strftime('\n%Y-%m-%d  %H:%M:%S', time.localtime()),
    print 'Time used: {0} hours, Total: {1}'.format(used_hour, cnt)
