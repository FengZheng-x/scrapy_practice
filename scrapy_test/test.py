import json
import re
import json
import time

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://jobs.51job.com/shenzhen-ftq/137026976.html?s=sou_sou_soulb&t=0_0'

# options = webdriver.ChromeOptions()
options = webdriver.ChromeOptions()
# 无头模式，无UI
# options.add_argument('-headless')

browser = webdriver.Chrome(options=options)

browser.get(url)
# time.sleep(100)
# browser.quit()
