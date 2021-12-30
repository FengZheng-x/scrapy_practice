import scrapy
import re
import json
from ..items import CrawlDataItem
from selenium import webdriver
from selenium.webdriver import ActionChains, ChromeOptions


class Get51JobSpider(scrapy.Spider):
    name = '51job'
    isStart = False
    count = 0
    
    def __init__(self, keyword=None, **kwargs):
        """
        :param keyword: 搜索的关键词
        """
        super().__init__(**kwargs)
        self.keyword = keyword
    
    def start_requests(self):
        """
        构造需爬取的链接
        """
        i = 1
        end = 500
        while i <= end:
            url = f'https://search.51job.com/list/000000,000000,0000,00,9,99,{self.keyword},2,{i}.html'
            print(url)
            yield scrapy.Request(url, self.parse)
            print(f"\033[34m正在爬取{i}页...\033[0m")
            i += 1
    
    def parse(self, response, **kwargs):
        """
        爬取一级页面, 获得页面的 json 数据, 解析并赋值给 Item
        """
        search_result = response.xpath('//script[@type="text/javascript"]/text()').get()
        # 获取 ajax 传回的 json 数据
        jobs = re.search(r'\w* = (.*)', search_result).group(1)
        job_json = json.loads(jobs)
        for engine_jd in job_json['engine_jds']:
            items = CrawlDataItem()
            items['jobwelf_list'] = '|'.join(engine_jd['jobwelf_list'])
            # 处理属性 attribute_text 值格式不同的问题, 如下
            # 'attribute_text' ': ['上海-浦东新区', '3-4年经验', '本科', '招2人']
            # 'attribute_text': ['南京-江宁区', '3-4年经验', '招10人']
            items['req_experience'], items['req_num'], items['req_academic_bg'] = '', '', ''
            for i in engine_jd['attribute_text']:
                if i == engine_jd['workarea_text']:
                    pass
                elif '经验' in i or '年' in i:
                    items['req_experience'] = i
                elif '招' in i:
                    items['req_num'] = i
                else:
                    items['req_academic_bg'] = i
            # 对其他字段赋值
            for i in items.fields.keys():
                if not items.get(i):
                    try:
                        items[i] = engine_jd[i]
                    except KeyError:
                        items[i] = ''
            url = engine_jd['job_href']
            # self.get_detail(url, items)
            
    def get_detail(self, url, items):
        """
        爬取二级页面, 即每个工作的页面
        """
        option = ChromeOptions()
        option.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=option)
        driver.get(url)
        btn = ActionChains(driver)
        ele = driver.find_element_by_id('nc_1_n1z')
        btn.click_and_hold(ele)
        # move_to_gap(driver, ele, get_track(258))
        btn.move_by_offset(258, 0)
        btn.release()
        btn.perform()
        box = driver.find_element_by_class_name('bmsg job_msg inbox')
        print(box.text)
    
    
