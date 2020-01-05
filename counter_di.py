# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import pandas as pd
from decimal import Decimal

g_excel_name = 'DTS.xlsx'
g_group_excel = 'Group.xlsx'
g_member_cnf = 'member.json'
g_version_cnf = 'version.json'
# 团队所有成员
g_member_dict = {}
# 所有支持的版本
g_version_list = []
g_di_level = ['致命', '严重', '一般', '提示']
g_level_map = {'致命': '10', '严重': '3', '一般': '1', '提示': '0.1'}
# 归档过程
g_filing_list = ['CMO归档']
# 测试回归过程
g_regress_list = ['测试经理组织测试', '测试人员回归测试']


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

    if not os.path.isfile(g_version_cnf):
        Logger.error("版本列表文件不存在: %s" % g_version_cnf)
        exit_delay()


def member_parse():
    global g_member_dict
    g_member_dict = JSONParser.parser(g_member_cnf)
    if not g_member_dict:
        Logger.error("解析成员列表文件失败！")
        exit_delay()
    Logger.info("Members: %s" % json.dumps(g_member_dict, ensure_ascii=False, indent=4))


def version_parse():
    version_dict = JSONParser.parser(g_version_cnf)
    if not version_dict:
        Logger.error("解析版本列表文件失败！")
        exit_delay()
    for _, version_list in version_dict.items():
        for version in version_list:
            if version not in g_version_list:
                g_version_list.append(version)
    Logger.info("versions: %s" % json.dumps(version_dict, indent=4))


def count_di():
    dts_data = pd.read_excel(g_excel_name)
    # 获取指定版本号对应的数据帧
    dts_data = dts_data[dts_data['产品B版本号'].isin(g_version_list)]
    # 用于统计汇总界面信息的数据
    total_data = {'-': g_di_level + ['归档DI', '小组总DI']}
    # 用于统计测试回归阶段的数据帧
    all_regress_dts = None
    writer = pd.ExcelWriter(g_group_excel)
    for group, members in g_member_dict.items():
        group_dts = None
        for en, ch in members.items():
            # 获取成员处理中的DTS
            member_dts = dts_data.loc[(dts_data['当前处理人'] == en) |
                                      (dts_data['当前处理人'].str.contains('%s,' % en))]
            # 处理中的追加到组DTS
            group_dts = member_dts if group_dts is None else pd.concat([group_dts, member_dts])
            # 获取测试回归阶段的DTS
            regress_dts = dts_data.loc[((dts_data['问题单修改人'] == en) |
                                       (dts_data['问题单修改人'].str.contains('%s,' % en))) &
                                       (dts_data['当前状态'].isin(g_regress_list))]
            all_regress_dts = regress_dts if all_regress_dts is None else pd.concat([all_regress_dts, regress_dts])
        # 对组DTS排序
        group_dts = group_dts.sort_values(by=['当前处理人', '严重程度', '当前状态'])
        # 写入Excel
        group_dts.to_excel(writer, sheet_name=group, index=False)
        total_data[group] = group_counter(group_dts)
    total_data['测试回归'] = group_counter(all_regress_dts)
    # 测试回归数据写入excel
    all_regress_dts = all_regress_dts.sort_values(by=['严重程度', '当前状态'])
    all_regress_dts.to_excel(writer, sheet_name='测试回归', index=False)
    # 汇总界面数据帧
    total_data_df = pd.DataFrame(total_data)
    total_data_df.to_excel(writer, sheet_name='汇总', index=False)
    writer.save()
    writer.close()


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


def main():
    check_env()

    member_parse()

    version_parse()

    count_di()


if __name__ == '__main__':
    main()
    exit_delay(0)

{
	"MDC": [
		"eMDC-V100C200B300",
		"eMDC-V100C200B301",
		"eMDC-V100C200B302",
		"eMDC-V100C200B303"
	],
	
	"MRS": [
		"eMRS-V100C200B300",
		"eMRS-V100C200B301",
		"eMRS-V100C200B302",
		"eMRS-V100C200B303"
	],
	
	"UDC": [
		"eUDC-V100C200B300",
		"eUDC-V100C200B301",
		"eUDC-V100C200B302"		
	]
}

