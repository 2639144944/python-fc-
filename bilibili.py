# -*- codeing = utf-8 -*-
#@Time: 2021/2/22 19:33
#@Name: 凡诚
#@File：bilibili
#@Software PyCharm
import urllib.request,urllib.parse
import re
from bs4 import BeautifulSoup
import xlwt
import sqlite3

#爬取网页地址
url = "https://www.bilibili.com/v/popular/rank/all"
#获得排名
findpm = re.compile(r'data-rank="(\d*)"><div')
#获得名字
findName = re.compile(r'href=".*" target="_blank">(.*)</a> <!-- --> ')
#获得番号
findfh = re.compile(r'li class="rank-item" data-id="(.*)" data-rank')
#获得播放地址
finddz = re.compile(r'a href="//(.*)" target="_blank"><img')
#获得播放量
findbfl = re.compile(r'<i class="b-icon play"></i>\n(.*)</span> <span class="data-box">',re.S)
#获得弹幕数
finddms = re.compile(r'</span> <span class="data-box"><i class="b-icon view"></i>(.*)</span> <a',re.S)
#获得制作方
findzzf = re.compile(r'<span class="data-box up-name"><i class="b-icon author"></i>(.*)</span></a></div> <div class="pts">',re.S)
#获得综合分数
findfs = re.compile(r'<div>(\d*)</div>综合得分')



#获得指定标签内的内容
def getText(html):

    #返回内容的列表
    list_s = []
    # 使用BeautifulSoup解析源码
    bs = BeautifulSoup(html, "html.parser")

    #依次解析获得内容
    for item in bs.find_all('li',class_='rank-item'):
        data = []
        item = str(item)

        #获得排名
        pm = re.findall(findpm, item)[0]
        data.append(pm)
        # 获得名字
        name = re.findall(findName,item)[0]
        name = name.replace("\'",'\"')
        data.append(name)

        # 获得番号
        fh = re.findall(findfh, item)[0]
        data.append(fh)

        #获得播放地址
        dz = re.findall(finddz, item)[0]
        data.append(dz)

        # 获得播放量
        bfl = re.findall(findbfl, item)[0]
        bfl = re.sub(r"\n","",bfl)
        bfl = re.sub(" ", "", bfl)
        data.append(bfl)

        # 获得弹幕数
        dms = re.findall(finddms, item)[0]
        dms = re.sub(" ","",dms)
        dms = re.sub(r"\n", "",dms)
        data.append(dms)

        # 获得制作方
        zzf = re.findall(findzzf, item)[0]
        zzf = re.sub(" ", "", zzf)
        zzf = re.sub(r"\n", "", zzf)
        data.append(zzf)

        # 获得综合分数
        fs = re.findall(findfs, item)[0]
        data.append(fs)
        list_s.append(data)
    print("已经获得指定标签内容！")
    return list_s



#获取指定网页源码
def getHtml(url):
    try:

        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}

        # 封装二进制对象
        data = bytes(urllib.parse.urlencode({"awsl": "awsl"}), encoding="utf-8")

        # 封装url对象
        re = urllib.request.Request(url=url, headers=header)

        # 获取网页源码
        res = urllib.request.urlopen(re, timeout=1)

        # 打印源码
        # print(res.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print("访问超时")
    print("已经获得指定网站源码！")
    return res.read().decode("utf-8")



#将爬取内容保存到excel表格中
def getExcel(list):
    list_b = ['排名','视频名称','视频番号','播放地址','观看次数','弹幕数量','制作者','综合分数']
    list_n = list
    #创建一个表格
    workbook = xlwt.Workbook(encoding="utf-8")
    #创建一个工作表
    worksheet = workbook.add_sheet("哔哩哔哩排行榜")
    #写入数据
    for i in range(0,8):
        #写入表头
        worksheet.write(0,i,list_b[i])

    for i in range(0, 100):
        for j in range(0, 8):
            #写入内容
            worksheet.write(i+1,j, list_n[i][j])

    #关闭并保存
    workbook.save("bilibili每日排行.xls")
    print("已经将指定内容保存于excel表格中！")




#将获得数据保存到sql数据库
def getSql(dbpath,table_name,list):

    #创建表，并添加表头
    createsql(dbpath,table_name)

    #将爬取 的数据列表放入数据库
    for item in list:
        sql = '''
            insert into %s values ('%s','%s','%s','%s','%s','%s','%s','%s')
        '''%(table_name,item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7])

        intosql(dbpath,sql)

    print("已经获得数据保存到sql数据库")



#选定数据库，执行sql语句
def intosql(dbpath,sql):

    #创建或者打开数据库
    conn = sqlite3.connect(dbpath)

    #创建游标
    c = conn.cursor()

    try:
        #使用游标执行语句
        c.execute(sql)

        #提交数据库操作
        conn.commit()
    except Exception:
        print("执行sql语句失败")
    finally:
        #关闭数据库
        conn.close()
    print("已经执行sql语句！")


#创建数据库，添加表头
def createsql(dbpath,table_name):
    list_id = ['list','name','id','location','number','barrage','maker','mark']
    sql = '''
        create table %s(
            %s varchar ,
            %s varchar,
            %s varchar,
            %s varchar,
            %s varchar ,
            %s varchar,
            %s varchar,
            %s varchar 
        )
    '''%(table_name,list_id[0],list_id[1],list_id[2],list_id[3],list_id[4],list_id[5],list_id[6],list_id[7])
    # 创建或者打开数据库
    conn = sqlite3.connect(dbpath)
    # 创建游标
    c = conn.cursor()
    try:
        # 使用游标执行语句
        c.execute(sql)

        # 提交数据库操作
        conn.commit()
    except Exception:
        print("执行sql语句失败")
    finally:
        # 关闭数据库
        conn.close()
    print("已经创建指定数据库，添加表头！")


if __name__ == "__main__":

    list = []
    dbpath = "bilibiliTop"
    table_name = "bilibiliTop100"
    #获取网页源码
    html = getHtml(url)

    #获取标签内容
    list = getText(html)

    #将获取数据写入excel表格
    #getExcel(list)

    #将获取数据写入sql数据库
    getSql(dbpath,table_name,list)


