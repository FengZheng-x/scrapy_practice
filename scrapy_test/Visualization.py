import pandas as pd
import re
from pyecharts.charts import Bar
from pyecharts.charts import Line
from pyecharts.charts import Map
from pyecharts.charts import Pie
from pyecharts.charts import WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import json

ZSCORE_THRESHOLD = 3
tooltip_opts = opts.TooltipOpts(trigger='item',
                                formatter='{b}: {c}',
                                background_color='white',
                                border_color='lightskyblue',
                                border_width=0.5,
                                textstyle_opts=opts.TextStyleOpts(color='gray'))


def unified_unit(item, num):
    # 单位统一成元
    if '千' in item:
        num *= 1000
    elif '万' in item:
        num *= 10000

    # 单位统一成月
    if '年' in item:
        num /= 12
    elif '天' in item:
        num *= 30
    elif '小时' in item:
        num *= 240

    return int(num)


def ave_salary(item):
    try:
        # 数字部分是-连接的话，取平均值
        item = str(item)
        if '-' in item:
            # print(item)
            item_re = re.search(r'(\d*\.?\d*)-(\d*\.?\d*)(.?)/(.?)', str(item))
            num = (float(item_re.group(1)) + float(item_re.group(2))) / 2
            return unified_unit(item, num)
        #  不是-连接的处理方式
        elif '/' in item:
            item_re = re.search(r'(\d*\.?\d*)(.?)/(.?)', str(item))
            num = float(item_re.group(1))
            return unified_unit(item, num)

    except Exception:
        return 0


def z_score(item, mean, std):
    return abs((item - mean) / std) > ZSCORE_THRESHOLD


def edu_salary(datas):  # 学历和薪资的关系
    labelx, labely = two_group(datas, 'education', 'salary')
    bar = Bar(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title='学历与薪资关系图'),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=25))
    )
    bar.add_xaxis(labelx)
    bar.add_yaxis('学历', labely, bar_width=50)
    bar.render('学历与薪资关系图.html')


def experence_salary(datas):
    labelx, labely = two_group(datas, 'workExperence', 'salary')
    dict_y = {}
    for i in range(len(labelx)):
        dict_y[labelx[i]] = labely[i]
    line = Line(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='工作经验与薪资关系图'),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=25))
    )
    line.add_xaxis(labelx)
    line.add_yaxis('工作经验', labely)
    line.render('工作经验与薪资关系图.html')


def area_salary(datas):
    # print(datas['area'])
    labelx, labely = two_group(datas, 'area', 'salary')
    m = Map(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    m.set_global_opts(
        title_opts=opts.TitleOpts(title='工作地区与薪资关系图'),
    )
    map_data = [list(z) for z in zip(labelx, labely)]
    m.add(series_name='', data_pair=map_data)
    m.set_global_opts(
        title_opts=opts.TitleOpts(title="工作地区与薪资关系 (省份)",
                                  pos_left='center'),
        visualmap_opts=opts.VisualMapOpts(min_=10000, max_=18000,
                                          pos_left='45',
                                          range_text=['high', 'low'],
                                          range_color=['lightskyblue', 'yellow', 'orangered']),
        tooltip_opts=tooltip_opts)
    m.render('工作地区与薪资关系图.html')


def area_num(datas):
    labelx, labely = two_group(datas, 'area', 'salary', 'count')
    m = Map(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    map_data = [list(z) for z in zip(labelx, labely)]
    m.add(series_name='', data_pair=map_data)
    m.set_global_opts(
        title_opts=opts.TitleOpts(title="工作地区分布 (省份)",
                                  pos_left='center'),
        visualmap_opts=opts.VisualMapOpts(min_=0, max_=8500,
                                          pos_left='45',
                                          range_text=['high', 'low'],
                                          range_color=['lightskyblue', 'yellow', 'orangered']),
        tooltip_opts=tooltip_opts)
    m.render('工作地区分布图.html')


def company_type(datas):
    labelx, labely = two_group(datas, 'companytype_text', 'salary', 'count')
    pie = Pie(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    pieData = [list(z) for z in zip(labelx, labely)]
    pie.add(series_name='', data_pair=pieData)
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="公司性质分布图",

                                  pos_left='center'),
        tooltip_opts=tooltip_opts,
        legend_opts=opts.LegendOpts(
            pos_left=20,
            orient='vertical'
        )

    )
    pie.render('公司性质分布图.html')


def two_group(datas, gro, num, polymerization='mean'):
    edu_salary = datas[[gro, num]].groupby(gro).agg(polymerization).sort_values(num)
    # print(list(edu_salary.mean().index))
    edu_salary_x = edu_salary.index
    edu_salary_y = edu_salary.values
    labelx = []
    labely = []
    for x in range(len(edu_salary_x)):
        # print(str(edu_salary_x[x]) + ':' + str(int(edu_salary_y[x])))
        if str(edu_salary_x[x]) != '-1':
            labelx.append(edu_salary_x[x])
            labely.append(int(edu_salary_y[x]))
    # print(labelx)
    # print(labely)
    return labelx, labely


def word_cloud(datas):
    word_dict = {}
    for kind in datas['companyind_text']:
        for word in str(kind).split('/'):
            if not word_dict.__contains__(word):
                word_dict[word] = 1
            else:
                word_dict[word] += 1
    # print(word_dict)
    wordCould = [list(z) for z in zip(word_dict.keys(), word_dict.values())]
    # print(wordCould)
    wordcloud = WordCloud(init_opts=opts.InitOpts(
        theme=ThemeType.LIGHT
    ))
    wordcloud.add(series_name='', data_pair=wordCould)
    wordcloud.set_global_opts(
        title_opts=opts.TitleOpts(title="企业类型词云图",
                                  pos_left='center'),
        tooltip_opts=tooltip_opts
    )
    wordcloud.render('企业类型词云图.html')


if __name__ == '__main__':
    '''
    处理薪资数据的离异值
    '''
    datas = pd.read_csv('C:\\learning\\python\\scrapy_practice\\scrapy_test\\result.csv')
    # print(datas.info())
    # salary = datas['providesalary_text']
    datas['salary'] = datas['providesalary_text'].map(lambda x: ave_salary(x))
    # print(datas['avg_salary'])
    mean = datas['salary'].mean()
    std = datas['salary'].std()
    # 使用z_score算法来判断离异值
    datas.drop(datas[z_score(datas['salary'], mean, std) == True].index, inplace=True)
    # print(datas)

    datas['workarea_text'] = [str(i).split('-')[0] for i in datas['workarea_text']]
    # print(datas['workarea_text'])

    with open('city_province.json', 'r', encoding='utf-8') as f:
        area_map = dict(json.load(f))
        # print(area_map)
        datas['area'] = datas['workarea_text'].map(lambda x: area_map.get(x))

    '''
    可视化部分
    学历和薪资的关系
    工作经验和薪资的关系
    地区跟薪资的关系
    地区和人数的关系
    企业性质（饼图）
    行业做成词云
    '''

    # 学历和薪资的关系bar图
    edu_salary(datas)
    # 工作经验和薪资的关系
    experence_salary(datas)
    # 地区与薪资的关系
    area_salary(datas)
    # 地区和人数的关系
    area_num(datas)
    # 企业性质（饼图）
    company_type(datas)
    # 行业做成词云
    word_cloud(datas)
