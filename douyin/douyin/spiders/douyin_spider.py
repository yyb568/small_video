# -*- coding:utf-8 -*-

import scrapy
import json
import logging
import requests
import os
from datetime import datetime


class DouYinSpider(scrapy.Spider):
    name = "douyin"
    def start_requests(self):
        self.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'

        urls = [
            "https://v.douyin.com/JBAEwxM/",
            "https://v.douyin.com/JByw4yE/"
            # "https://v.douyin.com/JBAmdpG/",
            # "https://v.douyin.com/JBAj51e/",
            # "https://v.douyin.com/JBAYQM7/",
            # "https://v.douyin.com/JBAfrvc/",
            # "https://v.douyin.com/JBAyoro/",
            # "https://v.douyin.com/JBAPdPq/",
            # "https://v.douyin.com/JBAAgLe/",
            # "https://v.douyin.com/JBA26Wj/",
            # "https://v.douyin.com/JBARQyG/",
            # "https://v.douyin.com/JBAy4Ek/",
            # "https://v.douyin.com/JBAMPtc/",
            # "https://v.douyin.com/JBAj4Te/",
            # "https://v.douyin.com/JBAAqAB/",
            # "https://v.douyin.com/JBA6ofU/",
            # "https://v.douyin.com/JBAfwhw/",
            # "https://v.douyin.com/JBAaNrC/",
            # "https://v.douyin.com/JBAavxS/",
            # "https://v.douyin.com/JBAfhYW/",
            # "https://v.douyin.com/JBAmHPG/",
            # "https://v.douyin.com/JBAUABx/",
            # "https://v.douyin.com/JBAkL21/",
            # "https://v.douyin.com/JBAU9SH/",
            # "https://v.douyin.com/JBAAGBo/",
            # "https://v.douyin.com/JBAeHq9/",
            # "https://v.douyin.com/JBAewWF/",
            # "https://v.douyin.com/JBASRQe/",
            # "https://v.douyin.com/JBAyA3Q/",
            # "https://v.douyin.com/JBALDj5/",
            # "https://v.douyin.com/JBArk67/",
            # "https://v.douyin.com/JBAAqXn/",
            # "https://v.douyin.com/JBA2FE4/",
            # "https://v.douyin.com/JBAu29E/",
            # "https://v.douyin.com/JBAtnNm/",
            # "https://v.douyin.com/JBAGpB1/",
            # "https://v.douyin.com/JBACsax/",
            # "https://v.douyin.com/JBA9u2B/",
            # "https://v.douyin.com/JBAKS9E/",
            # "https://v.douyin.com/JBAXKtb/",
            # "https://v.douyin.com/JBAcXRv/",
            # "https://v.douyin.com/JBAGH2R/",
            # "https://v.douyin.com/JBAxheN/",
            # "https://v.douyin.com/JBAnNfB/"
           ]

        meta = {}

        meta['number'] = len(urls)

        for url in urls:
            logging.info('正在下载: '+url)
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 meta=meta,
                                 headers={
                                     'user-agent': self.user_agent
                                 }
                                 )

    def parse(self, response):
        meta = response.meta
        redirect_url = response.url
        # 获取视频ID
        redirect_url = redirect_url.split("/")
        video_id = redirect_url[5]
        logging.info('获取到视频ID:'+video_id)
        meta['video_id'] = video_id
        


        # 通过这个接口获取视频信息，其中包括带有水印的链接
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='+video_id
        yield scrapy.Request(url=url,
                             callback=self.watermark,
                             meta=meta,
                             headers={
                                 'user-agent': self.user_agent
                             }
                             )


    def watermark(self, response):
       
        # 获取请求结果
        res = response.text
        list = json.loads(res)
        vid = list['item_list'][0]['video']['vid']
        # 自行拼接成无水印的链接
        videoLink = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + vid + "&ratio=720p&line=0"

        yield scrapy.Request(url=videoLink,
                             callback=self.download,
                             meta=response.meta,
                             headers={
                                 'user-agent': self.user_agent
                             }
                             )


    def download(self, response):

        meta = response.meta
        video_id = meta['video_id'].rstrip()
        file_name = video_id+'.mp4'

        # 今日日期
        day_time = datetime.now().strftime('%Y-%m-%d')

        base_dir = '../download/'+day_time

        video_local_path = base_dir+'/'+file_name
         
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
         
        with open(video_local_path, "wb") as f:
           f.write(response.body)      

        logging.info('下载完成！')          




