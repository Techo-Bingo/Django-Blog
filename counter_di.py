# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import datetime
import pandas as pd
from decimal import Decimal

g_excel_name = 'DTS.xlsx'
g_group_excel = 'Group.xlsx'
g_member_cnf = 'member.json'
# 成员配置文件数据
g_member_dict = {}
# 团队所有成员
g_team_mamber = {}
g_di_level = ['致命', '严重', '一般', '提示']
g_level_map = {'致命': '10', '严重': '3', '一般': '1', '提示': '0.1'}


def exit_delay(t=3):
    time.sleep(t)
    sys.exit(0)


class Logger:

    @classmethod
    def get_time(cls):
        ct = time.time()
        return '%s.%03d' \
               % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  (ct - int(ct)) * 1000
                  )

    @classmethod
    def info(cls, info):
        print("[INFO ] %s: %s" % (cls.get_time(), str(info)))

    @classmethod
    def error(cls, info):
        print("[ERROR] %s: %s" % (cls.get_time(), str(info)))


class JSONParser:
    """ JSON解析器 """
    @classmethod
    def parser(cls, json_path):
        try:
            with open(json_path, 'r', encoding='UTF-8') as f:
                return json.load(f)
        except Exception as e:
            Logger.error(e)
            return {}


def check_env():
    if not os.path.isfile(g_excel_name):
        Logger.error("Excel文件不存在: %s" % g_excel_name)
        exit_delay()

    if not os.path.isfile(g_member_cnf):
        Logger.error("成员列表文件不存在: %s" % g_member_cnf)
        exit_delay()


def member_parse():
    global g_member_dict
    g_member_dict = JSONParser.parser(g_member_cnf)
    if not g_member_dict:
        Logger.error("解析成员列表文件失败 （成员列表文件格式不对?）")
        exit_delay()
    # Logger.info(g_member_dict)
    for _, members in g_member_dict.items():
        for en, ch in members.items():
            g_team_mamber[en] = ch
    Logger.info(g_team_mamber)


def group_counter(writer, group, members, group_dts):
    group_dts.to_excel(excel_writer=writer, sheet_name=group, index=False)
    group_di = Decimal(0)
    count_list = []
    for level in g_di_level:
        count = len(group_dts[group_dts['严重程度'] == level])
        group_di += Decimal(count) * Decimal(g_level_map[level])
        count_list.append(count)
    # print('%s  DI: %s' % (group, group_di))
    return count_list + [group_di]


def count_di():
    # python 浮点运算有损，不准确，使用Decimal计算
    total_data = {
        '-': g_di_level + ['总DI']
    }
    dts_data = pd.read_excel(g_excel_name)
    writer = pd.ExcelWriter(g_group_excel)
    for group, members in g_member_dict.items():
        # 获取成员DTS列表并排序
        group_dts = dts_data[dts_data['当前处理人'].isin(members)].sort_values(by=['当前处理人', '严重程度'])
        total_data[group] = group_counter(writer, group, members, group_dts)
    # 汇总各组DI情况
    total_data_df = pd.DataFrame(total_data)
    total_data_df.to_excel(writer, sheet_name='汇总', index=False)
    writer.save()
    writer.close()

    '''
    for member in g_team_mamber:

        member_dts = dts_data[dts_data['当前处理人'].str.contains(member)]

        print(member_dts)
    '''


def main():

    check_env()

    member_parse()

    count_di()


if __name__ == '__main__':
    main()
    exit_delay(1)


{
  "Group-A": {
      "name_a": "张三",
      "name_b": "李四"
  },
    
  "Group-B": {
    "name_c": "王五"
  }
}


