import pandas as pd
import re
from pyecharts.charts import Bar
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType

ZSCORE_THRESHOLD = 3


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


def two_group(datas, gro, num):
    edu_salary = datas[[gro, num]].groupby(gro).agg('mean').sort_values(num)
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
    print(labelx)
    print(labely)
    return labelx, labely


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
