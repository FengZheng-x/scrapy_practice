import re
import json
import scrapy
from ..items import ScrapyTestItem
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Job51Spider(scrapy.Spider):
    name = 'Job51'

    keyWord_list = ['大数据', '人工智能']

    options = webdriver.ChromeOptions()

    # 无头模式，无UI
    options.add_argument('-headless')

    browser = webdriver.Chrome(options=options)

    def start_requests(self):
        """
        首先保存所有所需要搜索的关键字
        使用selenium获取所有关键字搜索后的第一个目标网页url，并存入列表
        通过selenium获取他们的总页数
        将每个第一位的url通过替换页数的方式
        """

        firstUrl_keyword = {}
        first_url_list = self.get_first_url()
        for i in range(len(self.keyWord_list)):
            firstUrl_keyword[first_url_list[i]] = self.keyWord_list[i]

        for first_url in first_url_list:
            page = 1
            max_page = self.get_pages(first_url)
            while page < max_page:
                lurl = first_url[0:int(first_url.index('.html')) - 1]
                rurl = first_url[int(first_url.index('.html')):]
                url = lurl + str(page) + rurl

                '''
                而此请求获取cookie，避免js加密
                '''
                # 第一次请求获取js代码

                # r = requests.get(url, headers=headers)
                # print(r.text)

                '''
                最终方案
                由于莫名原因在此处通过二次请求计算生成的
                反js加密cookie的注入动作无效
                最终选择添加下载器中间件，在中间件里进行注入动作
                无语，在源码里添加各种检查动作都能输出cookie，这应该是注入成功的啊，为什么呢？
                难道是此框架默认会用自己第一次访问网页生成的cookie或者某种情况下自己生成的cookie进行覆盖？
                有待考究，这是个问题
                '''
                # url = str(url).replace("https", "http")
                # print(url)
                yield scrapy.Request(url, self.parse)
                print(f'\033[4;35m正在爬取{firstUrl_keyword.get(first_url)}的第{page}页\033[0m')
                page += 1

        self.browser.quit()

    def parse(self, response, **kwargs):
        # print(response.text)
        # print(response.status)
        # print(response.body)
        # print(response.xpath('/html/body/script[2]/text()'))
        script = response.xpath('/html/body/script[2]/text()').get()

        # !!!问题：script为空导致程序错误,是因为部分页面加了js加密，需要二次请求获取cookie什么的，详情看代码最下方
        # print(str(script))
        js = re.search('window.__SEARCH_RESULT__ = (.*)', str(script)).group(1)
        js = json.loads(js)
        datas = js['engine_jds']
        # 生命变量

        for data in datas:
            item = ScrapyTestItem()
            item['workExperence'], item['education'], item['jobNum'] = '-1', '-1', '-1'
            for temp in data['attribute_text']:
                if temp == data['workarea_text']:
                    pass
                elif '年' in temp or '经验' in temp:
                    item['workExperence'] = temp
                elif '人' in temp:
                    item['jobNum'] = temp
                else:
                    item['education'] = temp
            try:
                for key in item.fields.keys():
                    if not item.get(key):
                        item[key] = data[key]
            except Exception:
                pass
            yield item

    def get_pages(self, url):
        '''使用selenium获取该关键字搜索结果的总页数'''
        browser = webdriver.Chrome(options=self.options)
        # browser = self.browser

        browser.get(url)

        wait = ui.WebDriverWait(browser, 10)
        wait.until(lambda browser: browser.find_element(By.XPATH,
                                                        "/html/body/div[2]/div[3]/div/div[1]/div[2]/div[1]"))

        html = browser.find_element(By.XPATH, "/html/body/div[2]/div[3]/div/div[1]/div[2]/div[1]").text

        pages = re.search('1 / (.*)', html).group(1)
        return int(pages)

    def get_first_url(self):
        first_url_list = []
        browser = webdriver.Chrome(options=self.options)
        # browser = self.browser
        browser.get('https://www.51job.com/')

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="kwdselectid"]')
                                           ))
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[1]/div/button')
                                           ))

        for keyWord in self.keyWord_list:
            input = browser.find_element(By.XPATH, '//*[@id="kwdselectid"]')
            click = browser.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/button')

            input.clear()

            input.send_keys(keyWord)
            click.click()
            # 等待新窗口加载完毕

            first_url_list.append(browser.current_url)
            print(browser.current_url)
            # handles = browser.window_handles
            # browser.switch_to_window(handles[0])
            browser.back()
        browser.quit()
        return first_url_list

    '''
    网站的反爬虫机制是在部分网页有js混淆
    网站隔一段就会变更二次请求的cookie
    需要二次请求获取cookie
    以下是对应的方法
    代码参考 http://www.4k8k.xyz/article/weixin_40352715/107965137
    '''
