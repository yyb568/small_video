# -*- coding:utf-8 -*-

import scrapy
import re
import json
import logging
from datetime import datetime
from moviepy.editor import *



class DouYinSpider(scrapy.Spider):

    name = "douyin"

    def start_requests(self):
        self.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'

        f = open("link.txt", "r")  # 设置文件对象
        data = f.readlines()  # 直接将文件中按行读到list里，效果与方法2一样
        f.close()  # 关闭文件

        urls =[]
        for item in data:
            if item == "\n":
                continue
            pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            url_list = re.findall(pattern,item)
            if url_list:
                urls.append(url_list[0])


        meta = {}
        meta['url_num'] = len(urls)
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
        info = json.loads(res)
        vid = info['item_list'][0]['video']['vid']
        # 自行拼接成无水印的链接
        video_link = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + vid + "&ratio=720p&line=0"

        yield scrapy.Request(url=video_link,
                             callback=self.download,
                             meta=response.meta,
                             headers={
                                 'user-agent': self.user_agent
                             }
                             )

    def download(self, response):
        meta = response.meta

        # 要下载的文件数量
        url_num = numbe = meta['url_num']
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
        #合成视频
        # self.synthesis(base_dir, url_num)

    @staticmethod
    def synthesis(base_dir, url_num):
       
        for curDir, dirs, files in os.walk(base_dir):
            # 获取该文件夹下的文件数量
            files_num = len(files)
            if url_num == files_num:
                # 按文件名排序
                files.sort()
                # 定义一个数组
                video_list = []
                # 遍历所有文件
                for file in files:
                    # 拼接成完整路径
                    file_path = os.path.join(curDir, file)
                    # 视频载入内存
                    video = VideoFileClip(file_path)

                    # 添加到数组
                    video_list.append(video)
                # 拼接视频
                final_clip = concatenate_videoclips(video_list, method='compose')

                # 改变视频的分辨率
                # final_clip.resize(newsize=(2160,4096))

                # 生成目标视频文件
                final_clip.write_videofile(base_dir+"/synthesis.mp4",fps=75, codec='mpeg4', verbose=False, audio=True, audio_codec="aac")

                # final_clip.to_videofile(str(file), fps=30, remove_temp=True)








