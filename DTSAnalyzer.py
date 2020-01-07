# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import pandas as pd
from decimal import Decimal

__author__ = 'lwx382598'
__version__ = '1.0'

g_in_excel = 'DTS-IN.xlsx'
g_out_excel = 'DTS-OUT.xlsx'
g_member_cnf = 'member.json'
g_version_cnf = 'version.json'
g_settings_cnf = 'settings.json'
# 团队所有成员
g_member_dict = {}
# 所有支持的版本
g_version_list = []
# DTS url根路径
g_root_url = ''
g_di_level = ['致命', '严重', '一般', '提示']
g_level_map = {'致命': '10', '严重': '3', '一般': '1', '提示': '0.1'}
# 归档过程
g_filing_list = ['CMO归档']
# 测试回归过程
g_regress_list = ['测试经理组织测试', '测试人员回归测试', '确认问题单']
# debug开关
g_debug_switch = False


def exit_delay(t=3):
    Logger.info("即将在%s秒后退出程序..." % t)
    time.sleep(t)
    sys.exit(0)


def about_info():
    about = """
    \tDTS分析工具 v%s
    \t\t——%s
    """ % (__version__, __author__)
    print(about)


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
    def debug(cls, info):
        if not g_debug_switch:
            return
        print("[DEBUG] %s: %s" % (cls.get_time(), str(info)))

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
    if not os.path.isfile(g_in_excel):
        Logger.error("Excel文件不存在: %s" % g_in_excel)
        exit_delay()

    if not os.path.isfile(g_member_cnf):
        Logger.error("成员列表文件不存在: %s" % g_member_cnf)
        exit_delay()

    if not os.path.isfile(g_version_cnf):
        Logger.error("版本列表文件不存在: %s" % g_version_cnf)
        exit_delay()

    if not os.path.isfile(g_settings_cnf):
        Logger.error("设置项配置文件不存在: %s" % g_settings_cnf)
        exit_delay()

    Logger.info("环境检查完成......成功")


def member_parse():
    global g_member_dict
    g_member_dict = JSONParser.parser(g_member_cnf)
    if not g_member_dict:
        Logger.error("解析成员列表文件失败！")
        exit_delay()
    Logger.info("成员配置解析完成......成功")
    Logger.debug("成员信息: %s" % json.dumps(g_member_dict, ensure_ascii=False, indent=4))


def version_parse():
    version_dict = JSONParser.parser(g_version_cnf)
    if not version_dict:
        Logger.error("解析版本列表文件失败！")
        exit_delay()
    for _, version_list in version_dict.items():
        for version in version_list:
            if version not in g_version_list:
                g_version_list.append(version)
    Logger.info("版本配置解析完成......成功")
    Logger.debug("版本信息: %s" % json.dumps(version_dict, indent=4))


def settings_parse():
    global g_root_url
    global g_debug_switch
    settings = JSONParser.parser(g_settings_cnf)
    if not settings:
        Logger.error("解析设置项配置文件失败！")
        exit_delay()
    try:
        g_root_url = settings['URL']
        g_debug_switch = settings['DEBUG']
    except:
        Logger.error("设置项配置文件缺失数据！")
        exit_delay()
    Logger.info("URL配置解析完成......成功")


def group_counter(group_dts):
    # python 浮点运算有损，不准确，使用Decimal计算
    filing_di = Decimal(0)
    group_di = Decimal(0)
    count_list = []
    # 归档中的DTS
    filing_dts = group_dts[group_dts['当前状态'].isin(g_filing_list)]
    for level in g_di_level:
        count_f = len(filing_dts[filing_dts['严重程度'] == level])
        count_g = len(group_dts[group_dts['严重程度'] == level])
        _lvl_di = Decimal(g_level_map[level])
        filing_di += Decimal(count_f) * _lvl_di
        group_di += Decimal(count_g) * _lvl_di
        count_list.append(count_g)
    return count_list + [filing_di, group_di]  # 致命、严重、一般、提示、归档、总共


def count_di():
    dts_data = pd.read_excel(g_in_excel)
    # 获取指定版本号对应的数据帧
    dts_data = dts_data[dts_data['产品B版本'].isin(g_version_list)]
    Logger.info("过滤版本号完成......成功")
    # 用于统计汇总界面信息的数据
    total_data = {'-': g_di_level + ['归档DI', '小组总DI']}
    # 用于统计测试回归阶段的数据帧
    all_regress_dts = None
    # 临时保存各个小组的dts数据帧
    dts_dict = {}
    writer = pd.ExcelWriter(g_out_excel)
    for group, members in g_member_dict.items():
        group_dts = None
        for en, ch in members.items():
            # 替换中文名字
            dts_data['当前处理人'] = dts_data['当前处理人'].str.replace(en, ch)
            dts_data['问题修改人'] = dts_data['问题修改人'].str.replace(en, ch)
            # 获取成员处理中的DTS(开发DTS)
            member_dts = dts_data.loc[((dts_data['当前处理人'] == ch) |
                                      (dts_data['当前处理人'].str.contains('%s,' % ch))) &
                                      (~dts_data['当前状态'].isin(g_regress_list))]
            # 处理中的追加到组DTS
            group_dts = member_dts if group_dts is None else pd.concat([group_dts, member_dts])
            # 获取测试回归阶段的DTS
            regress_dts = dts_data.loc[((dts_data['问题修改人'] == ch) |
                                        (dts_data['问题修改人'].str.contains('%s,' % ch))) &
                                       (dts_data['当前状态'].isin(g_regress_list))]
            all_regress_dts = regress_dts if all_regress_dts is None else pd.concat([all_regress_dts, regress_dts])
        # 计算小组DI数据
        total_data[group] = group_counter(group_dts)
        dts_dict[group] = group_dts
        Logger.info("统计%s组DTS......成功" % group)
    # 计算测试回归DI数据
    total_data['测试回归'] = group_counter(all_regress_dts)
    dts_dict['测试回归'] = all_regress_dts
    Logger.info("统计测试回归DTS......成功")

    def color_map(val):
        return 'color: blue'

    # 小组DTS数据格式等整理
    for group in dts_dict:
        # 对DTS排序
        group_dts = dts_dict[group].sort_values(by=['当前处理人', '严重程度', '当前状态'])
        # 创建链接
        for _, row in group_dts.iterrows():
            dts_num = row['问题单号']
            row.loc['链接'] = '=HYPERLINK("%s%s", "打开")' % (g_root_url, dts_num)
        # pytinstaller打包会有问题，注释掉
        # 修改链接颜色
        # group_dts = group_dts.style.applymap(color_map, subset=['链接'])
        # 写入Excel
        group_dts.to_excel(writer, sheet_name=group, index=False)
    # 汇总界面数据帧
    total_data_df = pd.DataFrame(total_data)
    total_data_df.to_excel(writer, sheet_name='汇总', index=False)
    writer.save()
    writer.close()
    Logger.info("写入%s......成功" % g_out_excel)


def main():
    about_info()

    check_env()

    settings_parse()

    member_parse()

    version_parse()

    count_di()


if __name__ == '__main__':
    main()
    exit_delay(5)

