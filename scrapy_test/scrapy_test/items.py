# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyTestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    jobid = scrapy.Field()
    job_href = scrapy.Field()
    issuedate = scrapy.Field()       #发布日期
    job_name = scrapy.Field()            #工作名称
    providesalary_text = scrapy.Field()             #工资
    workarea_text = scrapy.Field()       #工作地点
    workExperence = scrapy.Field()      #工作经验
    education = scrapy.Field()          #学历
    jobNum = scrapy.Field()             #招聘人数
    jobwelf_list = scrapy.Field()          #待遇
    company_href = scrapy.Field()
    company_name = scrapy.Field()        #公司名称
    companytype_text = scrapy.Field()    #公司类别
    companysize_text = scrapy.Field()       #公司人数
    companyind_text = scrapy.Field()   #公司方向
    pass
