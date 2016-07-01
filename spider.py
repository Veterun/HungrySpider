# -*- coding: utf8 -*-
import requests

import time
import sys
from itertools import combinations_with_replacement
from threading import Thread
from Queue import Queue


class GenerateThread(Thread):
    '''产生所有的字母组合，拼接成网址'''

    def __init__(self, queue, min, max, consumer_num):
        super(GenerateThread, self).__init__()
        self.queue = queue
        self.min = min
        self.max = max
        self.consumer_num = consumer_num

    def run(self):
        source = list('abcdefghijklmnopqrstuvwxyz0123456789')
        prefix = 'http://'
        suffix = '.com'
        for length in xrange(self.min, self.max + 1):
            for chars in combinations_with_replacement(source, length):
                hostname = ''.join(chars)
                url = ''.join([prefix, hostname, suffix])
                self.queue.put(url)
                print '\r', 'Now detecting: ', url,
                sys.stdout.flush()
        for i in xrange(self.consumer_num):
            # 放入 None 终止匹配线程
            self.queue.put(None)


class MatchThread(Thread):
    '''判断队列中的网址是否为黄网'''

    def __init__(self, source_queue, result_queue):
        super(MatchThread, self).__init__()
        self.source_queue = source_queue
        self.result_queue = result_queue
        self.keys = [u'人妻', u'乱伦', u'情色', u' sex ']

    def run(self):
        while True:
            url = self.source_queue.get()
            self.source_queue.task_done()
            if url is None:
                break  # 网址已全部遍历
            try:
                r = requests.get(url, timeout=1)
            except:
                continue  # 网站访问速度过慢，可能是墙外网站
            r.encoding = 'gbk'
            for key in self.keys:
                if key in r.text:
                    self.result_queue.put(url)  # 在网页中找到关键字
        self.result_queue.put(None)  # 终止保存网址进程


class SaveThread(Thread):
    '''将黄网网址保存至文件'''

    def __init__(self, filename, result_queue):
        super(SaveThread, self).__init__()
        self.filename = filename
        self.result_queue = result_queue
        self.count = 0

    def run(self):
        f = open(self.filename, 'w')
        while True:
            url = self.result_queue.get()
            self.result_queue.task_done()
            if url is None:
                break  # 网址已全部遍历
            f.write(''.join([url, '\n']))
            f.flush()
            self.count += 1
        f.close()
        print '\nTotal: {0}, '.format(self.count)


class HungrySpider:
    '''控制爬虫逻辑'''

    def __init__(self, min, max, match_thread_num=10, filename='urls.txt'):
        self.min = min
        self.max = max
        self.match_thread_num = match_thread_num
        self.filename = filename

    def show_begin_info(self):
        print time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime()),
        print 'the spider is going on ...'

    def show_end_info(self):
        print 'Time used: {0} hours'.format(self.used_hour)
        print time.strftime('Ended: %Y-%m-%d  %H:%M:%S', time.localtime())

    def get_used_time(self):
        return self.used_hour

    def crawl(self):
        start_time = time.time()

        source_queue = Queue(self.match_thread_num)
        result_queue = Queue()
        generate_thread = GenerateThread(
            source_queue, self.min, self.max, self.match_thread_num)
        generate_thread.start()
        match_thread_list = []
        for i in xrange(self.match_thread_num):
            match_thread_list.append(MatchThread(source_queue, result_queue))
            match_thread_list[i].start()
        save_thread = SaveThread(self.filename, result_queue)
        save_thread.start()
        # Main thread ends at last
        generate_thread.join()
        for i in xrange(self.match_thread_num):
            match_thread_list[i].join()
        save_thread.join()

        end_time = time.time()
        self.used_hour = round((end_time - start_time) / 3600, 3)


if __name__ == '__main__':
    spider = HungrySpider(1, 3, match_thread_num=20, filename='x.txt')
    spider.show_begin_info()
    spider.crawl()
    spider.show_end_info()
