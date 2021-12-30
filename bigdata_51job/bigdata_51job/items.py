# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CrawlDataItem(Item):
    # define the fields for your item here like:
    jobid = Field()  # 职位 id
    job_name = Field()  # 职位名
    jobwelf_list = Field()  # 福利待遇
    company_name = Field()  # 公司名
    providesalary_text = Field()  # 薪水
    workarea_text = Field()  # 工作位置
    req_experience = Field()  # 需求经验
    req_academic_bg = Field()  # 学历
    req_num = Field()  # 需求人数
    issuedate = Field()  # 发布时间
    companytype_text = Field()  # 公司类型
    companysize_text = Field()  # 公司规模
    companyind_text = Field()  # 公司标签
    info = Field()  # 职位信息
