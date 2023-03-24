import time
import requests
import os
import sys
from lxml import etree
import re

def check_folder(save_folder):
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

def requests_get(url, max_iter=5):
    while(max_iter > 0):
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            time.sleep(3)
            max_iter -= 1
    raise Exception('get() loss connection!')

class BookSpyder():
    def __init__(self,
                 save_folder="./content",
                 project_name="我是幕后大佬",
                 url="https://www.biqooge.com/0_97/68199.html"
                 ) -> None:  
        check_folder(save_folder)              
        self.save_file = os.path.join(save_folder, f"{project_name}.txt")
        self.content = ""
        self.geturl(url)
    
    def download(self, tree):
        title = tree.xpath('//div[@class="bookname"]/h1/text()')
        print(title)
        sub_content = tree.xpath('//div[@id="content"]/text()')
        sub_content = '\n'.join([c.strip() for c in sub_content])
        self.content += f"{title[0]}\n{sub_content}\n"

    def geturl(self, url):
        try:
            resp=requests_get(url)
            if resp is None:
                sys.exit("Lose connection!")
            resp.encoding='gbk'
            html=resp.text
            tree=etree.HTML(html)
            self.download(tree)
            next_url = tree.xpath('//a[text()="下一章"]/@href')
            if next_url is not None:
                self.geturl("https://www.biqooge.com/" + next_url[0])
        except Exception as e:
            print(e)
            print(url)
            print(next_url)
            with open(self.save_file, 'w') as f:
                f.write(self.content)



if __name__ == "__main__":
    bs = BookSpyder()

