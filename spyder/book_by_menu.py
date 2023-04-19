import time
import requests
import os
import sys
from lxml import etree
import re
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import shutil
import queue

def check_path(save_folder):
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
                save_folder,
                remain_every_chap,
                project_name,
                menu_url,
                root,
                menu_title_pattern,
                menu_title_href_pattern,
                chap_content_pattern
                 ) -> None:  
        self.remain_every_chap = remain_every_chap
        self.menu_title_pattern = menu_title_pattern
        self.menu_title_href_pattern = menu_title_href_pattern
        self.chap_content_pattern = chap_content_pattern

        save_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), save_folder))
        check_path(save_folder)              
        self.project_folder = os.path.join(save_folder, project_name)
        check_path(self.project_folder) 
        # 根据章节数调整maxsize，否则会阻塞 
        self.tasks = queue.Queue(maxsize=5000)      
        self.phase_menu(root, menu_url)
        self.run()
    
    def run(self):
        print('Downloading...')
        all_executors = []
        with ThreadPoolExecutor(1000) as executor:
            while (not self.tasks.empty()):         
                t, a, idx = self.tasks.get()      
                # print(a)          
                all_executors.append(executor.submit(self.download, t=t, url=a, idx=idx))
                if self.tasks.empty():
                    print('延长等待时间处理...')
                    wait(all_executors, return_when=ALL_COMPLETED)
                    if self.tasks.empty():
                        break
        self.merge_content()
        

    def phase_menu(self, root, url):
        print("Phase menu...")
        try:
            resp=requests_get(url)
        except Exception as e:
            print(e)
            sys.exit("Can`t download menu!")
        resp.encoding='gbk'
        html=resp.text
        tree=etree.HTML(html)
        titles = tree.xpath(self.menu_title_pattern)
        title_herfs = tree.xpath(self.menu_title_href_pattern)  
        for i, t in enumerate(titles):
            if i > 20:
                sys.exit('请确认是否存在第一章！')
            if re.search(r"第\s*[1一]\s*章", t):
                titles = titles[i:]
                title_herfs = title_herfs[i:]
                print(f"从第{i}个目录开始...")
                break
        
        for idx, (t, a) in enumerate(zip(titles, title_herfs)):
            self.tasks.put((t, root + a, idx))
        self.tasks_num = self.tasks.qsize()

    def download(self, t, url, idx):
        try:
            resp=requests_get(url)
        except Exception as e:
            self.tasks.put((t, url, idx))
            return
        resp.encoding='gbk'
        html=resp.text
        tree=etree.HTML(html)
        sub_content = tree.xpath(self.chap_content_pattern)
        sub_content = '\n'.join([c.strip() for c in sub_content])
        content = f"{t}\n\n{sub_content}"

        save_file = os.path.join(self.project_folder, f"{idx:05d}.txt")
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def merge_content(self):
        print('Check...')
        all_files = os.listdir(self.project_folder)
        all_files.sort()

        mask = [i for i in range(self.tasks_num)]
        for t in all_files:
            mask[int(t[:-4])] = -1
        cnt = 0
        for x in mask:
            if x != -1:
                # print(x)
                cnt += 1
        if(cnt > 0):
            sys.exit("Lose some file!")

        print("Merge...")
        all_files = [os.path.join(self.project_folder, file) for file in all_files]
        with open(f'{self.project_folder}.txt', 'w') as f:
            for txt_file in all_files:
                with open(txt_file, 'r') as f1:
                    f.write(f1.read())
        print(f"文件保存到:{self.project_folder}.txt")
        if not self.remain_every_chap:
            shutil.rmtree(self.project_folder)

cfg1 = {
    'project_name': "我是幕后大佬",
    'menu_url':"https://www.biqooge.com/0_97/",
    'root' : "https://www.biqooge.com/",
    'menu_title_pattern':'//div[@id="list"]/dl/dd/a/text()',
    'menu_title_href_pattern':'//div[@id="list"]/dl/dd/a/@href',
    'chap_content_pattern':'//div[@id="content"]/text()'
}

cfg2 = {
    'project_name': "修真聊天群",
    'menu_url':"https://www.biqooge.com/1_1030/",
    'root' : "https://www.biqooge.com/",
    'menu_title_pattern':'//div[@id="list"]/dl/dd/a/text()',
    'menu_title_href_pattern':'//div[@id="list"]/dl/dd/a/@href',
    'chap_content_pattern':'//div[@id="content"]/text()'
}

cfg3 = {
    'project_name': "圣墟",
    'menu_url':"https://www.biqooge.com/0_6/",
    'root' : "https://www.biqooge.com/",
    'menu_title_pattern':'//div[@id="list"]/dl/dd/a/text()',
    'menu_title_href_pattern':'//div[@id="list"]/dl/dd/a/@href',
    'chap_content_pattern':'//div[@id="content"]/text()'
}

cfg4 = {
    'project_name': "问道红尘",
    'menu_url':"https://www.biqooge.com/0_75/",
    'root' : "https://www.biqooge.com/",
    'menu_title_pattern':'//div[@id="list"]/dl/dd/a/text()',
    'menu_title_href_pattern':'//div[@id="list"]/dl/dd/a/@href',
    'chap_content_pattern':'//div[@id="content"]/text()'
}

if __name__ == "__main__":
    bs = BookSpyder(
        save_folder="content",
        remain_every_chap=False,
        **cfg4
    )


