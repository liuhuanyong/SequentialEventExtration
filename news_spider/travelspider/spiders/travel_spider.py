# coding=utf-8
import scrapy
from urllib import request
import pymongo
from lxml import etree
from travelspider.items import TravelspiderItem

class TravelSpider(scrapy.Spider):
    name = 'travel'
    '''资讯采集主控函数'''
    def start_requests(self):
        for index in range(1, 505831):
            url = 'http://you.ctrip.com/travels/china110000/t3-p%s.html'%index
            response = request.urlopen(url)
            page = response.read().decode('utf-8')
            urls = self.get_urls(page)
            if urls:
                for url in urls:
                    try:
                        print(url)
                        param = {'url': url}
                        yield scrapy.Request(url=url, meta=param, callback=self.page_parser, dont_filter=True)
                    except:
                        pass

    '''获取url列表'''
    def get_urls(self, content):
        selector = etree.HTML(content)
        urls = ['http://you.ctrip.com' + i for i in selector.xpath('//a[starts-with(@class,"journal-item")]/@href')]
        return set(urls)

    '''网页解析'''
    def page_parser(self, response):
        selector = etree.HTML(response.text)
        title = selector.xpath('//title/text()')[0]
        paras = [p.xpath('string(.)').replace('\xa0', '') for p in selector.xpath('//div[@class="ctd_content"]/p') if
                 p.xpath('string(.)').replace('\xa0', '')]
        if not paras:
            paras = [p.xpath('string(.)').replace('\xa0', '') for p in
                     selector.xpath('//div[@class="ctd_content wtd_content"]/p') if
                     p.xpath('string(.)').replace('\xa0', '')]
        if not paras:
            paras = [p.xpath('string(.)').replace('\xa0', '') for p in selector.xpath('//div[@class="ctd_content"]')]
        content = "\n".join([i.replace('\r', '').replace('\n', '') for i in paras])
        item = TravelspiderItem()
        item['url'] = response.meta['url']
        item['title'] = title
        item['content'] = content
        yield item
        return
