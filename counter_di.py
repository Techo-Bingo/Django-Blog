# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import datetime
import pandas as pd
from decimal import Decimal

g_excel_name = 'DTS.xlsx'
g_member_cnf = 'member.json'
g_member_dict = {}


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


def count_di():
    # python 浮点运算有损，不准确，使用Decimal计算
    level_map = {'致命': '10', '严重': '3', '一般': '1', '提示': '0.1'}
    dts_count = 0
    total_di = 0
    di_dict = {}
    dts_data = pd.read_excel(g_excel_name)
    print('------- 小组 -------')
    for group, members in g_member_dict.items():
        group_di = 0
        for en, ch in members.items():
            # 获取组员dts列表
            member_dts = dts_data.loc[dts_data['当前处理人'] == en]
            if member_dts.empty:
                continue
            # TODO 写到另一个excel中
            di_levels = member_dts['严重程度']
            for di_lvl in di_levels:
                # Logger.info("%s %s %s" % (group, ch, di_lvl))
                _di = Decimal(level_map[di_lvl])
                if ch in di_dict:
                    _new_di = di_dict[ch] + _di
                    di_dict[ch] = _new_di
                else:
                    di_dict[ch] = _di
                group_di += _di
                total_di += _di
                dts_count += 1
        print("{:12}: {}".format(group+' DI', group_di))
    print('------- 团队 -------')
    print("{:8}: {}".format("团队总DI", total_di))
    print("{:8}: {}".format("DTS总个数", dts_count))
    sort_dict = sorted(di_dict.items(), key=lambda x: x[1], reverse=True)
    print("----- DI排行榜 -----")
    for member in sort_dict:
        print("{:6}: {}".format(member[0], member[1]))


def main():
    check_env()

    member_parse()

    count_di()


if __name__ == '__main__':
    main()
    exit_delay(5)




