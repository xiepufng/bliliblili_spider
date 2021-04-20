import requests
import re
import time
from threading import Thread
from queue import Queue
import json


class BlilibliliSpider(object):
    """B站多线程爬虫"""

    def __init__(self):
        self.q = Queue()
        self.url = 'https://api.bilibili.com/x/web-interface/popular?ps=20&pn={}'
        # 浏览器抓包获得
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            # "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "cookie": "fingerprint=bd1b6509a35f4e22e5bf2537271fbea9; buvid_fp=CD574209-D446-429D-911C-CDAF4D8A458E143111infoc; buvid_fp_plain=C072413D-321F-4708-A6EC-49A7372D080B185000infoc; CURRENT_FNVAL=80; _uuid=8F83D8E1-5AA8-52A8-E681-ABB6DCE25A2C47038infoc; buvid3=CD574209-D446-429D-911C-CDAF4D8A458E143111infoc; blackside_state=1; rpdid=|(umR~lmRlkm0J'uY|JYmk)l); LIVE_BUVID=AUTO1216146669857273; CURRENT_QUALITY=64; fingerprint=bd1b6509a35f4e22e5bf2537271fbea9; buvid_fp=CD574209-D446-429D-911C-CDAF4D8A458E143111infoc; buvid_fp_plain=C072413D-321F-4708-A6EC-49A7372D080B185000infoc; sid=jz5uhvmb; PVID=2",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "referer": "https://www.bilibili.com/video/BV1SK4y1m7Ct",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
        }
        self.filename = '/home/tarena/bliliblili'
        self.i = 0

    # 生成url放入队列
    def url_in(self):
        for pn in range(1, 3):
            url = self.url.format(pn)
            self.q.put(url)

    # 解析一级页面
    def parse_one_page(self):
        while True:
            if not self.q.empty():
                url = self.q.get()
                data = requests.get(url=url, headers=self.headers).text
                # data.decode('utf8')

                print(data)
                data = json.loads(data)['data']['list']

                L = {}
                for info in data:
                    L['title'] = info['title']
                    L['bvid'] = info['bvid']
                    L['tname'] = info['tname']
                    print(L)
                    self.parse_two_page(L['bvid'], L['title'])
                    time.sleep(6)
            else:
                break

    # 解析二级页面
    def parse_two_page(self, bvid, title):
        url = 'https://www.bilibili.com/video/' + bvid
        html = requests.get(url=url, headers=self.headers).text
        bds = 'window.__playinfo__=(.*?)</script>'
        pattern = re.compile(bds, re.S)
        data = pattern.findall(html)[0]
        data = json.loads(data)
        data = data['data']['dash']['audio'][0]
        video_url = data['base_url']
        voice_url = data['backup_url'][0]
        # print(video_url)
        # print(voice_url)


        self.save_data(video_url, voice_url, title)

    # 保存数据
    def save_data(self, video_url, voice_url, title):
        video = requests.get(url=video_url, headers=self.headers).content
        with open(self.filename + title + '.mp4', 'wb')as f:
            print(video)
            f.write(video)
            print('视频下载完成')
        video = requests.get(url=voice_url, headers=self.headers).content
        # html=video.decode('utf8')
        with open(self.filename + title + '.mp3', 'wb')as f:
            f.write(video)
            print('声音下载完成')
        self.i += 1

    def main(self):
        self.url_in()
        t_list = []
        for t in range(3):
            t = Thread(target=self.parse_one_page)
            t_list.append(t)
            t.start()
        for t in t_list:
            t.join()
        print('共抓取%s条视频' % self.i)


if __name__ == '__main__':
    spider = BlilibliliSpider()
    spider.main()
