import pymysql
import pandas as pd
import numpy as np
import sklearn as sk
__author__ = 'winkEmoji'
"""
一个小工具用于生成MySQL实体类

A tool for generating MySQL entity classes

"""
# 连接mysql数据库
db = pymysql.connect(
    host='localhost',                # 你的数据库地址
    port=3306,                       # 端口号
    user='root',                     # 用户名
    password='root',                 # 密码
    database='shp-lite',             # 数据库名
    charset='utf8mb4',               # 编码方式
    cursorclass=pymysql.cursors.DictCursor  # 游标返回方式为字典
)
cursor = db.cursor()


class generator(object):

    def __init__(self):
        # 是否详细输出
        self.__verbose = False
        # 数据类型字典
        self.__dataType = {'TINYINT': 'INT', 'SMALLINT': 'INT', 'MEDIUMINT': 'INT', 'INTEGER': 'INT', 'INT': 'INT',
                           'BIGINT': 'INT',
                           'FLOAT': 'FLOAT', 'DOUBLE': 'FLOAT', 'DECIMAL': 'FLOAT',
                           'VARCHAR': 'STR'}

        cursor.execute('show tables')

        res = cursor.fetchall()

        # 初始化 _table_list 用于存放数据库中表名
        self.__table_list = {}
        for i in range(len(res)):
            self.__table_list[i] = res[i]['Tables_in_shp-lite']

    def generate(self, verbose=True):
        self.__verbose = verbose
        # 遍历table list
        for tableName in self.__table_list.values():
            cursor.execute('show columns from %s' % tableName)
            res = cursor.fetchall()
            # 读取每张表的详细信息 table details
            tableDetails = pd.DataFrame(res)
            fields = tableDetails[['Field', 'Type']]
            self.__writer(tableName, fields)

        print('INFO: GENERATE SUCCESS!')
        pass

    def __writer(self, tableName, fields):
        paper: str
        paper = 'class {tableName}:\n\tdef __init__(self):\n\t\t'.format(tableName=tableName)
        appendPaper = str('')
        if self.__verbose:
            print('INFO:  {tableName}'.format(tableName=tableName))
        for index, row in fields.iterrows():
            for key in self.__dataType.keys():
                if row['Type'].find(key.lower()) != -1:
                    if self.__verbose:
                        print(
                            'INFO:  {tableName}.{Field} : {Type} --> {dataType}'.format(tableName=tableName,
                                                                                        Field=row['Field']
                                                                                        , Type=row['Type'],
                                                                                        dataType=self.__dataType[
                                                                                            key].lower()))
                    appendWrite = 'self.{Field}: {dataType}\n\t\t'.format(Field=row['Field'],
                                                                          dataType=self.__dataType[key].lower())
            appendPaper += appendWrite
        # 去掉最后一行的两个tab缩进 :)
        appendPaper = appendPaper[:-2]
        paper += appendPaper
        if self.__verbose:
            print()
        self.write2py(tableName=tableName, paper=paper)

    pass

    def write2py(self, tableName, paper):
        try:
            f = open('{tableName}.py'.format(tableName=tableName), 'w+')
            f.write(paper)
        except Exception as e:
            print(e)


# 开始生成实体类
generator().generate(verbose=True)
