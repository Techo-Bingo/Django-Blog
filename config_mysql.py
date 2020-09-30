#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import subprocess
import os
import sys
import json
import fcntl
import logging
import itertools
import traceback
from select import select

extral_dir = r'/opt/UBP/bin/ha'
sys.path.append(extral_dir)
from ha_common import HACommon
from ha_filesync import Interface

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class Env:
    """ 环境信息类 """
    log_file = '/home/ubp/sh_log/config_mysql.log'
    lock_file = '/opt/UBP/bin/ha/config_mysql.lock'
    my_cnf = '/etc/eapp3307/my.cnf'
    exec_sql = '/opt/UBP/bin/exec_sql'
    ha_util = '/opt/UBP/bin/ha/ha_util.pyc'
    ssh_trust_tool = '/opt/UBP/bin/distribute/ssh-trust.ex'
    dbwhitename = '/opt/UBP/bin/dbproc/dbwhitename.sh'
    get_deploy = '/opt/UBP/bin/get_deploy_hostcfg_field.pyc'
    set_deploy = '/opt/UBP/bin/mod_deploy_hostcfg_field.pyc'
    cfg_sync_result = '/opt/add-ons/keepalived/etc/ha_cfg_sync.result'
    isp_ha_status_conf = '/opt/UBP/conf/ha/isp_ha_status_conf.json'
    sync_db_data_sh = '/opt/add-ons/keepalived/bin/sync_db_data.sh'
    sync_db_data_local_sh = '/opt/add-ons/keepalived/bin/sync_db_data_local.sh'
    config_mysql_repl = '/opt/add-ons/keepalived/bin/config_mysql_repl.sh'
    mysql_client = '/usr/local/eappmysql/bin/mysql --defaults-file=/etc/eapp3307/my.cnf'
    isp_ha_daem_mysql = '/opt/UBP/conf/rulingservice/ha_daem/isp_ha_daem_mysql.json'


class DbInstance(object):
    """ 数据库数据类 """

    def __init__(self, param_list):
        self.ha_mode_ex = param_list[0]
        if self.ha_mode_ex.find('ACTIVE') != -1:
            self.ha_mode = 'MASTER'
        elif self.ha_mode_ex.find('STANDBY') != -1:
            self.ha_mode = 'SLAVE'
        else:
            self.ha_mode = 'STANDALONE'
        self.host_ip = param_list[1]
        self.db_ip = param_list[1]
        self.host_pwd = param_list[2]
        self.db_pwd = param_list[3]
        self.increment = param_list[4]
        self.offset = param_list[5]
        self.serverid = param_list[6]
        self.host_user = 'ubp'
        self.db_user = 'odb_user'
        self.db_port = '3307'
        self.old_host_ip = '127.0.0.1'
        self.old_db_ip = '127.0.0.1'


class Scene:
    """ 配置场景类 """
    standalone_mode = 'STANDALONE'
    # 生产（主备）主
    local_active = 'LOCAL_ACTIVE'
    # 生产备
    local_standby = 'LOCAL_STANDBY'
    # 容灾主
    remote_active = 'REMOTE_ACTIVE'
    # 容灾备
    remote_standby = 'REMOTE_STANDBY'

    @classmethod
    def is_set_standalone(cls, dbs):
        return len(dbs) == 1 and dbs[0].ha_mode_ex == cls.standalone_mode

    @classmethod
    def is_set_active(cls, dbs):
        # 主备+容灾场景主机
        if len(dbs) == 4 and dbs[0].ha_mode_ex == cls.local_active:
            return True
        # 单主备场景主机/单容灾场景主机
        if len(dbs) == 2 and dbs[0].ha_mode_ex in [cls.local_active, cls.remote_active]:
            return True
        return False

    @classmethod
    def is_set_standby(cls, dbs):
        # 主备+容灾场景容灾主
        if len(dbs) == 4 and dbs[0].ha_mode_ex == cls.remote_active:
            return True
        # 单主备场景备机/单容灾场景备机/主备+容灾场景备机
        if len(dbs) in [2, 4] and dbs[0].ha_mode_ex in [cls.local_standby, cls.remote_standby]:
            return True
        return False


class MysqlRepl(object):

    success = 0
    fail = 0
    unnormal_db_instances = []

    def __init__(self, db_instances):
        self.db_instances = db_instances
        self.operations = [
            ('end', self.reset_null, 100, 0),
            ('post_handle', self.reset_null, 95, 0),
            ('config_repl', self.reset_null, 85, -10507),
            ('restart_mysql', self.reset_null, 75, -10506),
            ('sync_db_data', self.reset_null, 70, -10507),
            ('export_mysql', self.reset_null, 40, -10507),
            ('reset_slave', self.reset_null, 30, -10507),
            ('config_dbwhitename', self.reset_null, 20, -10501),
            ('extral_config', self.reset_extral_config, 16, -10501),
            ('config_deploy', self.reset_config_deploy, 15, -10501),
            ('config_mycnf', self.reset_null, 10, -10501),
            ('pre_handle', self.post_handle, 5, -10503),
            ('back_up_config', self.reset_null, 3, -10501),
            ('check_db_connect', self.reset_null, 2, -10501),
            ('set_host_trust', self.reset_null, 1, -10501),
            ('init', self.reset_null, 0, 0)]
        self.active_actions = [
            ('set_host_trust', self.set_host_trust),
            ('check_db_connect', self.check_db_connect),
            ('back_up_config', self.back_up_config),
            ('pre_handle', self.pre_handle),
            ('config_mycnf', self.config_mycnf),
            ('config_deploy', self.config_deploy),
            ('extral_config', self.extral_config),
            ('reset_slave', self.reset_slave),
            ()

        ]

    def set_host_trust(self):
        def trust_impl(local, remote):
            # local to remote
            cmd = '''
sudo /opt/UBP/bin/pam_tally2.sh -r
{0} <<EOF
{1}/{2}@{3}
EOF
'''.format(Env.ssh_trust_tool, remote.host_user, remote.host_pwd, remote.host_ip)
            if not HACommon.execute_result(cmd):
                logging.error('set ssh trust {0} --> {1} failed !'.format(local.host_ip, remote.host_ip))
                return False
            logging.info('set ssh trust {0} --> {1} success'.format(local.host_ip, remote.host_ip))
            # remote to local
            cmd = '''
ssh ubp@{0} "sudo /opt/UBP/bin/pam_tally2.sh -r
{1} <<EOF
{2}/{3}@{4}
EOF
"
'''.format(remote.host_ip, Env.ssh_trust_tool, local.host_user, local.host_pwd, local.host_ip)
            if not HACommon.execute_result(cmd):
                logging.error('set ssh trust {0} --> {1} failed !'.format(remote.host_ip, local.host_ip))
                return False
            logging.info('set ssh trust {0} --> {1} success'.format(remote.host_ip, local.host_ip))

        for local in self.db_instances:
            for remote in self.db_instances:
                if not trust_impl(local, remote):
                    self.write_sync_result('set_host_trust', 'Failed')
                    return False
        logging.info('set_host_trust success')
        self.write_sync_result('set_host_trust', 'Succeed')
        return True

    """
    def reset_ssh_trust(self, remote):
        self.execute_result('> /home/ubp/.ssh/authorized_keys')
        if self.execute_result("ssh ubp@{0} '> /home/ubp/.ssh/authorized_keys'".format(remote.host_ip)):
            logging.error('reset ssh trust of {0} failed'.format(remote.host_ip))
    """

    def check_db_connect(self):
        for db in self.db_instances:
            cmd = "ssh ubp@{0} eappmysql -u{1} -p{2} -e 'select 1;'".format(db.host_ip, db.db_user, db.db_pwd)
            if not HACommon.execute_result(cmd):
                logging.error('{0} DB connect failed !'.format(db.host_ip))
                return False
        # 校验innodb_data_file_path值是否一致
        tmp_values = {}
        for db in self.db_instances:
            cmd = '''ssh ubp@{0} python {1} read_ini {2} mysqld innodb_data_file_path
                    '''.format(db.host_ip, Env.ha_util, Env.my_cnf)
            value = HACommon.execute_stdout(cmd).strip()
            if value == "":
                logging.error('check_my_cnf failed with {0}'.format(db.host_ip))
                return False
            tmp_values[db.host_ip] = value
        if len(set(tmp_values.values())) != 1:
            logging.error('check_my_cnf failed ! details: {0}'.format(tmp_values))
            return False
        return True

    def back_up_config(self):
        for db in self.db_instances:
            cmd = 'ssh ubp@{0} sudo {1} backup_config'.format(db.host_ip, Env.sync_db_data_local_sh)
            if not HACommon.execute_result(cmd):
                logging.error('back_up_config failed with {0}'.format(db.host_ip))
                return False
        return True

    def pre_handle(self):
        for db in self.db_instances:
            cmd = '''ssh -o ServerAliveInterval=5 ubp@{0} sudo {1} pre_handle
            '''.format(db.host_ip, Env.sync_db_data_local_sh)
            if not HACommon.execute_result(cmd):
                logging.error('pre_handle failed with {0}'.format(db.host_ip))
                return False
        return True

    def config_mycnf(self):
        for db in self.db_instances:
            cmd = '''ssh ubp@{0} sudo {1} {2} {3} {4} {5}
            '''.format(db.host_ip, Env.config_mysql_repl, db.increment, db.offset, db.serverid, db.db_ip)
            if not HACommon.execute_result(cmd):
                logging.error('config_mycnf failed with {0}'.format(db.host_ip))
                return False
        return True

    def config_deploy(self):
        # 修改本机deploy文件中的ha_mode项
        # 非生产主的ha_mode不能在配生产主的时候一并修改掉 否则备机web应用模式ip列表那里会显示异常
        cmd = 'python {0} HA_MODE {1}'.format(Env.set_deploy, self.db_instances[0].ha_mode)
        if not HACommon.execute_result(cmd):
            logging.error('config local deploy for HA_MODE failed')
        for db in self.db_instances:
            cmd = 'ssh ubp@{0} python {1} HA_LOCAL_IP {0}'.format(db.host_ip, Env.set_deploy)
            if not HACommon.execute_result(cmd):
                logging.error('config_deploy failed with {0}'.format(db.host_ip))
                return False
        return True

    def extral_config(self):
        for db in self.db_instances:
            cmd = 'ssh ubp@{0} sudo {1} excute_plugin_shells'.format(db.host_ip, Env.sync_db_data_local_sh)
            if not HACommon.execute_result(cmd):
                logging.error('extral_config failed with {0}'.format(db.host_ip))
                return False
        return True

    def reset_slave(self):
        for db in self.db_instances:
            cmd = '''ssh ubp@{0} {1} <<EOF
STOP SLAVE;
RESET SLAVE ALL;
'''.format(db.host_ip, Env.exec_sql)
            if not HACommon.execute_result(cmd):
                logging.error('reset_slave failed with {0}'.format(db.host_ip))
                return False
        return True

    def config_repl(self, local, remote):
        sql = '''
CHANGE MASTER TO
    MASTER_HOST = '{remote_db_ip}',
    MASTER_PORT = {remote_db_port},
    MASTER_USER = '{remote_db_user}',
    MASTER_PASSWORD = '{remote_db_pwd}',
    MASTER_AUTO_POSITION = 1
FOR CHANNEL '{remote_db_ip}';
START SLAVE
FOR CHANNEL '{remote_db_ip}';
'''
        cmd = self.gen_remote_cmd(r'ssh ubp@{remote_host_ip} {exec_sql}', local, remote)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        in_param = self.gen_remote_cmd(sql, remote, local)
        p.communicate(input=in_param)
        return p, local, remote

    def post_handle(self, local):
        cmd = self.gen_local_cmd(r'ssh -o ServerAliveInterval=5 ubp@{local_host_ip} sudo {sync_db_data_local_sh} post_handle', local)
        return subprocess.Popen(cmd, shell=True)

    def restart_web(self, local):
        cmd = self.gen_local_cmd(r'ssh -o ServerAliveInterval=5 ubp@{local_host_ip} sudo {sync_db_data_local_sh} restart_web', local)
        return subprocess.Popen(cmd, shell=True)

    def reset_config_mycnf(self, local):
        cmd = self.gen_local_cmd(r'ssh ubp@{local_host_ip} sudo {sync_db_data_local_sh} restore_config', local)
        return subprocess.call(cmd, shell=True)

    def restart_mysql(self, local):
        cmd = self.gen_local_cmd(r'ssh -o ServerAliveInterval=5 ubp@{local_host_ip} sudo {sync_db_data_local_sh} restart', local)
        return subprocess.Popen(cmd, shell=True), local

    def reset_restart_mysql(self, local):
        pass

    def reset_standalone(self, local):
        cmd = self.gen_local_cmd(r'ssh -o ServerAliveInterval=5 ubp@{local_host_ip} sudo {sync_db_data_local_sh} reset_standalone', local)
        return subprocess.Popen(cmd, shell=True)

    def export_mysql(self, local, remote):
        # 导出mysql基准数据(只导出一次)
        # parse_input()从标准输入读到的第一行一定是生产主 也就是db_instances[0]
        local, remote = self.db_instances[0], self.db_instances[1]
        p = self.export_mysql(local, remote)
        if p.wait():
            logging.error('export_mysql failed with {local_ip}'.format(local_ip=local.host_ip))
            self.error_handler(local, 'export_mysql')
            self.write_sync_result('export_mysql', 'Failed')
            return self.fail
        self.write_sync_result('export_mysql', 'Succeed')

        cmd = self.gen_local_cmd(r'ssh -o ServerAliveInterval=5 ubp@{local_host_ip} sudo {sync_db_data_sh} export_mysql', local)
        logging.info('export db data from {host_ip}'.format(host_ip=local.host_ip))
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        in_param = self.gen_remote_cmd('{remote_host_ip}\n{remote_db_ip}\n{remote_db_pwd}\n{local_host_ip}\n{'
                                       'local_db_ip}\n{local_db_pwd}\nSLAVE\nSYNC_YES\n1\n', remote, local)
        p.stdin.write(in_param)
        p.stdin.close()
        return p

    def reset_export_mysql(self, local):
        pass

    def sync_db_data(self, local, remote):
        cmd = self.gen_remote_cmd(r'ssh -o ServerAliveInterval=5 ubp@{remote_host_ip} sudo {sync_db_data_sh} sync_data_from_backup', local, remote)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        in_param = self.gen_remote_cmd('{remote_host_ip}\n{remote_db_ip}\n{remote_db_pwd}\n{local_host_ip}\n{'
                                       'local_db_ip}\n{local_db_pwd}\nSLAVE\nSYNC_YES\n1\n', remote, local)
        p.stdin.write(in_param)
        p.stdin.close()
        return p, local, remote

    def config_isp_ha_daem_mysql(self, local):
        cmd = self.gen_local_cmd(r'ssh ubp@{local_host_ip} python {ha_util} write_json {isp_ha_daem_mysql} "[0]['
                                 r'\'check\'][\'tcp\']" {local_host_ip}:3307', local)
        return subprocess.call(cmd, shell=True)

    def reset_config_deploy(self, local):
        cmd = self.gen_local_cmd(r'ssh ubp@{local_host_ip} sudo {sync_db_data_local_sh} restore_config', local)
        return subprocess.call(cmd, shell=True)

    def reset_extral_config(self, local):
        cmd = self.gen_local_cmd(r'ssh ubp@{local_host_ip} sudo {sync_db_data_local_sh} excute_reset_plugin_shells', local)
        p = subprocess.call(cmd, shell=True)
        return p, local

    @classmethod
    def get_output(cls, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        ret_code = p.returncode
        return out, err, ret_code

    # 获取mysql同步状态的接口 不抛出异常 返回False或True
    @classmethod
    def get_repl_status(cls):
        try:
            # 获取本机slave status
            cmd = cls.exec_sql + ''' --all "-s -N -e'start slave;show slave status'" '''
            out, err, ret_code = cls.get_output(cmd)
            if ret_code:
                return False
            repl_status = {}
            for raw_line in out.splitlines():
                line = raw_line.split('\t')
                repl_status[line[1]] = line[10] + line[11]
            # 查询各ip的同步状态
            i = 0
            ip_info = json.load(open(cls.isp_ha_status_conf, 'r'))
            for key in ['LOCAL_STANDBY', 'REMOTE_ACTIVE', 'REMOTE_STANDBY']:
                if key in ip_info and ip_info[key] != 'NULL':
                    if ip_info[key] not in repl_status or repl_status[ip_info[key]] != 'YesYes':
                        return False
                    else:
                        i += 1
            if i != len(repl_status):
                return False
            return True
        except Exception as e:
            print(traceback.print_exc())
            return False

    # 添加操作日志
    @classmethod
    def add_op_log(cls, ret_code, web_op_log):
        tmp = [''] * 10
        web_op_log_arr = web_op_log.replace('__B__', ' ').split('@')
        for index, i in enumerate(web_op_log_arr):
            if index < 10:
                tmp[index] = i

        [log_op_name, log_op_level, log_op_user, log_user_type, log_op_time, log_op_category, log_op_terminal,
         log_op_result, log_op_desc, log_op_moc] = tmp
        log_op_result = ret_code
        out_sql = "INSERT INTO TBL_UserLog (OpName,OpLevel,OpUser,OpUserType,OpTime,OpType,OpTerminal,OpResult," \
                  "OpDesc,OpMoc) values ('{log_op_name}',{log_op_level},'{log_op_user}',{log_user_type}," \
                  "'{log_op_time}','{log_op_category}','{log_op_terminal}','{log_op_result}','{log_op_desc}'," \
                  "'{log_op_moc}'); "
        out_sql = out_sql.format(
            log_op_name=log_op_name,
            log_op_level=log_op_level,
            log_op_user=log_op_user,
            log_user_type=log_user_type,
            log_op_time=log_op_time,
            log_op_category=log_op_category,
            log_op_terminal=log_op_terminal,
            log_op_result=log_op_result,
            log_op_desc=log_op_desc,
            log_op_moc=log_op_moc,
        )
        print(out_sql)
        cmd = cls.exec_sql + ' --db ubpdb'
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        p.communicate(input='set names gbk;'+out_sql)
        return p.returncode

    def reset_null(self, local):
        pass

    # 写进度条配置文件
    def write_sync_result(self, action, result):
        logging.info("{0} {1}".format(action, result))
        progress, error_code = '2', '-1'
        for i in self.operations:
            if i[0] == action:
                progress = i[2]
                error_code = i[3]
                break
        with open(Env.cfg_sync_result, 'w+') as f:
            f.write("{0} {1} {2} {3}\n".format(str(progress), action, result, str(error_code)))

    # 执行相应回滚操作
    def error_handler(self, operation):
        logging.info('{0} failed'.format(operation))
        found_flag = False
        for op in self.operations:
            if not found_flag and op[0] != operation:
                continue
            found_flag = True
            for db in self.db_instances:
                op[1](self, db)

    # 拆单
    def set_standalone(self):
        self.write_sync_result('init', 'Succeed')
        Interface.switch(['OnStandalone'])
        # 拆单时候db_instances通常只有一个元素（一次拆一台机器） 所以这里可以也换成
        # self.reset_standalone(self.db_instances[0]).wait()
        [p.wait() for p in [self.reset_standalone(db) for db in self.db_instances]]
        self.write_sync_result('end', 'Succeed')
        return self.success

    # 配置主机
    def set_active(self):
        self.write_sync_result('init', 'Succeed')

        for action_tuple in self.active_actions:
            action, func = action_tuple
            if not func():
                self.error_handler(action)
                self.write_sync_result(action, 'Failed')
                return False
            self.write_sync_result(action, 'Succeed')

        # 群组内mysql同步基准数据
        # 除了生产主之外的机器都从生产主同步数据
        local = self.db_instances[0]
        processes = [self.sync_db_data(local, db) for db in self.db_instances[1:]]
        for p in processes:
            if p[0].wait():
                logging.error('{remote_ip} sync data from {local_ip} failed'.format(remote_ip=p[2].host_ip,
                                                                                    local_ip=p[1].host_ip))
                self.error_handler(p[2], 'sync_db_data')
                self.write_sync_result('sync_db_data', 'Failed')
                return self.fail
        self.write_sync_result('sync_db_data', 'Succeed')
        # 异步重启群组内mysql实例
        processes = [self.restart_mysql(db) for db in self.db_instances]
        # 等待所有mysql重启完成
        for p in processes:
            if p[0].wait():
                logging.error('restart_mysql failed with {local_ip}'.format(local_ip=p[1].host_ip))
                self.error_handler(p[1], 'restart_mysql')
                self.write_sync_result('restart_mysql', 'Failed')
                return self.fail
        self.write_sync_result('restart_mysql', 'Succeed')
        # 建立群组内mysql的复制关系
        # 如果是4台机器，取其中2台的排列数，for循环会迭代4*3=12次
        for permutation in itertools.permutations(self.db_instances, 2):
            local, remote = permutation[0], permutation[1]
            p = self.config_repl(local, remote)
            if p[0].returncode:
                logging.error('config_repl failed between {local_ip} and {remote_ip}'.format(local_ip=local.host_ip,
                                                                                             remote_ip=remote.host_ip))
                self.error_handler(local, 'config_repl')
                self.write_sync_result('config_repl', 'Failed')
                return self.fail
        self.write_sync_result('config_repl', 'Succeed')
        # 开启文件同步
        ip_list = [None, None, None, None]
        # 目前最多4台机器
        for index, db in enumerate(self.db_instances):
            if index < 4:
                ip_list[index] = db.host_ip
        logging.info('ip_list is' + str(ip_list))
        Interface.init(ip_list)
        # 重启所有服务(备机要起服务)
        processes = []
        for db in self.db_instances:
            if db.ha_mode.find('LOCAL_ACTIVE') == -1:
                # 非生产主需要起ubp_adm各服务，为了能登web进主备容灾配置，需要起license服务
                processes.append(self.post_handle(db))
                # processes.append(self.restart_web(db))
            else:
                # 生产主不需要起ubp_adm各服务，因为接下来就是切应用模式了，不需要起license服务
                # processes.append(self.post_handle(db))
                processes.append(self.restart_web(db))
        for p in processes:
            p.communicate()
        self.write_sync_result('end', 'Succeed')
        # 输出最终结果
        for db in self.db_instances:
            logging.info('{local_ip} succeed'.format(local_ip=db.host_ip))
        # unnormal_db_instances没用到
        for db in self.unnormal_db_instances:
            logging.info('{local_ip} failed'.format(local_ip=db.host_ip))
        return self.success

    # 配置非生产主
    def set_non_local_master(self):
        # 配置非生产主的时候仅仅只修改本机deploy文件的ha_mode
        if self.set_ha_mode(self.db_instances[0]):
            logging.error('config_deploy failed with {local_ip}'.format(local_ip=self.db_instances[0].host_ip))
            self.write_sync_result('config_mycnf', 'Failed')
            return self.fail
        self.write_sync_result('end', 'Succeed')
        return self.success


def parse_input():
    if len(sys.argv) != 2:
        logging.error('invalid params: {0}'.format(sys.argv))
        sys.exit(1)

    # 防止标准输入没有东西导致脚本卡死 超时时间设置为10秒
    lines, local_dbs, timeout = [], [], 10
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        line = sys.stdin.readline()
        while line:
            lines.append(line)
            line = sys.stdin.readline()
    else:
        logging.error('No input. Exit')
        sys.exit(1)
    # 根据从标准输入读取的机器信息次序来分配my.cnf的三个参数increment, offset, serverid
    increment, offset, serverid = len(lines), 0, 0
    for line in lines:
        offset += 1
        serverid += 1
        # 每行信息初始化一个DbInstance结构体，方便后续组装shell命令字符串
        local_dbs.append(DbInstance(line.split() + [str(increment), str(offset), str(serverid)]))
    # 返回DbInstance结构体列表
    return local_dbs


def init_logger():
    f_out = open(Env.log_file, 'a+')
    # 重定向标准输出和标准错误输出
    os.dup2(f_out.fileno(), 1)
    os.dup2(f_out.fileno(), 2)
    # 初始化logging
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] (line:%(lineno)d): %(message)s')
    # 输出到标准输出
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(fmt)
    log.addHandler(std_handler)


def check_running():
    # 文件锁防重入
    lock_file = open(Env.lock_file, 'w')
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        logging.error('Cannot lock: {0}, last process is running...'.format(Env.lock_file))
        sys.exit(1)


if __name__ == '__main__':
    try:
        init_logger()
        check_running()
        dbs = parse_input()

        if Scene.is_set_standalone(dbs):
            ret_code = MysqlRepl(dbs).set_standalone()
        elif Scene.is_set_active(dbs):
            ret_code = MysqlRepl(dbs).set_active()
        elif Scene.is_set_standby(dbs):
            ret_code = MysqlRepl(dbs).set_standby()
        else:
            logging.error('unknown ha scene...')
            ret_code = 1
        MysqlRepl.add_op_log(ret_code, sys.argv[1])
        sys.exit(ret_code)
    except Exception as e:
        logging.error(traceback.print_exc())
        sys.exit(1)
