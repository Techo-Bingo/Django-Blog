==============  HATOOL.py
#-*- coding: UTF-8 -*-

import my_main as main
from my_handler import EnvUtil
from my_common import Cache

__author__ = 'libin'


def start():
	# 初始化环境 
	EnvUtil.init()
	
	# 登录界面 
	main.LoginInit()

	if Cache.exit_signal():
		return

	# 主界面 
	main.MainInit()
	

if __name__ == '__main__':
	start()

================== my_view.py 
#-*- coding: UTF-8 -*-

import tkinter as tk
from my_message import WinMsg
from my_common import Globals,Cache
from my_setting import Settings
from my_handler import LoginDealer,PageDealer,EnvUtil
from my_module import SubLogin,LabelButton,InfoWindow


class GuiLogin(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.font = Globals.font()
		self.login_instance = {}
		self.bg_color = 'Snow'
		self.width = 600
		self.height = 480
		self.head_height = 160
		self.foot_height = 70
		self.login_count = 1
		self.login_limit = 4
		self.setting = Settings()

	def init_frame(self):
		self.set_title()
		self.headwin = tk.Frame(self, width=self.width, height=self.head_height,\
			bg=self.bg_color)
		self.funcwin = tk.Frame(self,width=self.width, height=self.height - \
			(self.head_height + self.foot_height), bg=self.bg_color)
		self.btnwin = tk.Frame(self,width=self.width, height=self.foot_height,\
			bg=self.bg_color)
		self.loginwin = tk.LabelFrame(self.funcwin)

	def set_title(self):
		self.title(Globals.title())
		screen_width, screen_height = self.maxsize()
		self.geometry('+%d+%d' % \
			((screen_width - self.width) / 2,\
			(screen_height - self.height) / 2))
		self.resizable(False, False)
		#ico = Cache.get_image_instance('ICO')
		#if ico:
		#	self.iconbitmap(ico)

	def pack_frame(self):
		self.headwin.pack()
		self.funcwin.pack()
		tk.Label(self.funcwin, bg=self.bg_color, text='用户登录',\
			font=('-*-%s-*-*-*--*-160-*') % (self.font)).pack()
		self.loginwin.pack()
		self.btnwin.pack()
		'''固定Frame的长和宽，不会随其中的控件多少改变'''
		#self.loginwin.pack_propagate(0)	
		self.funcwin.pack_propagate(0)
		self.headwin.pack_propagate(0)
		self.btnwin.pack_propagate(0)
		# 子控件布局 
		self.init_sub_win()

	def init_sub_win(self):
		head = Cache.get_image_instance('HEAD')
		if head:
			tk.Label(self.headwin, image=head).pack()
		tk.Label(self.loginwin,text='').grid(row=0,column=0)
		tk.Label(self.loginwin,text='').grid(row=1,column=0)
		tk.Label(self.loginwin,text='IP',font=('-*-%s-*-*-*--*-140-*')\
			%(self.font)).grid(row=1,column=1)
		tk.Label(self.loginwin,text='用户名',font=('-*-%s-*-*-*--*-140-*')\
			%(self.font)).grid(row=1,column=2)
		tk.Label(self.loginwin,text='用户密码',font=('-*-%s-*-*-*--*-140-*')\
			%(self.font)).grid(row=1,column=3)
		tk.Label(self.loginwin,text='root密码',font=('-*-%s-*-*-*--*-140-*')\
			%(self.font)).grid(row=1,column=4)
		sub = SubLogin(self.loginwin, 1, self.login_instance)
		sub.set_defaults(self.setting.get_passwd_info())
		sub.pack()
		eye = Cache.get_image_instance('EYE')
		if eye:
			eyebtn = tk.Button(self.loginwin, image=eye, bd=0)
			eyebtn.grid(row=2, column=5, padx=3)
			eyebtn.bind("<Button-1>",self.see_password_on)
			eyebtn.bind("<ButtonRelease-1>",self.see_password_off)
		add = Cache.get_image_instance('ADD')
		if add:
			tk.Button(self.btnwin, image=add, bd=0, bg=self.bg_color,\
				command=self.add_sublogin).pack(side=tk.LEFT, padx=80)
		tk.Button(self.btnwin, text=' 一键登录 ', font=('-*-%s-*-*-*--*-150-*')%(self.font),\
			relief='solid', compound='top', fg='Gold', bg=Globals.color(), command=\
			self.click_login).pack(side=tk.LEFT, padx=10, ipadx=40)

	def click_login(self, event=None):
		deal = LoginDealer(self.login_instance)
		deal.handler()
		if deal.result():
			WinMsg.info("登录成功")
			Cache.exit_signal(exit=False)
			del self.login_instance
			self.destroy()

	def close_window(self, event=None):
		Cache.exit_signal(exit=True)
		del self.login_instance
		self.destroy()

	def add_sublogin(self):
		if len(self.login_instance) >= self.login_limit:
			WinMsg.info('最多支持%s个登录' % (self.login_limit))
			return
		self.login_count += 1
		sub = SubLogin(self.loginwin, self.login_count, self.login_instance)
		sub.set_defaults(self.setting.get_passwd_info())
		sub.pack()

	def see_password_on(self, event=None):
		for seq, inst in self.login_instance.items():
			inst.see_passwd('ON')

	def see_password_off(self, event=None):
		for seq, inst in self.login_instance.items():
			inst.see_passwd('OFF')


class GuiMain(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.width = 1200
		self.height = 500
		self.left_width = 130
		self.middle_width = 720
		self.right_width = self.width - self.left_width - self.middle_width
		self.rightwin = None
		self.lab_list = {	1: '主备状态', 
							2: '主备日志', 
							3: 'Binlog日志', 
							4: '日志巡检', 
							5: '其他日志',
							6: '主备配置',
							7: '预留',
					}

	def init_frame(self):
		self.set_title()	
		self.leftwin = tk.Frame(self, width=self.left_width, height=self.height)
		self.middlewin = tk.Frame(self, width=self.middle_width, height=self.height)
		self.info_fm = tk.Frame(self.middlewin, width=self.middle_width, height=150)
		self.view_fm = tk.Frame(self.middlewin, width=self.middle_width, height=350, bg='Snow')
		
	def set_title(self):
		self.title(Globals.title())
		screen_width, screen_height = self.maxsize()
		self.geometry('+%d+%d' % ((screen_width - self.width) / 2, 
								(screen_height - self.height) / 2))
		self.resizable(False, False)

	def pack_frame(self):
		self.leftwin.pack(side=tk.LEFT)
		self.middlewin.pack(side=tk.LEFT)
		self.leftwin.pack_propagate(0)
		self.middlewin.pack_propagate(0)
		self.init_sub_win()

	def init_sub_win(self):
		intvar = tk.IntVar()
		intvar.set(1)
		for seq, text in self.lab_list.items():
			LabelButton(self.leftwin, seq=seq, intvar=intvar, text=text, \
				command=self.click).pack()
		self.view_fm.grid(row=1, column=1)
		self.info_fm.grid(row=2, column=1)
		self.view_fm.pack_propagate(0)
		self.info_fm.pack_propagate(0)
		# 初始化info信息栏
		Cache.infowin_inst(InfoWindow(self.info_fm))
		# 初始化page处理类 
		self.pager = PageDealer(self.view_fm, self.view_rightwin)
		# 登录成功后的处理
		self.pager.after_login_deal()

	def click(self, index):
		self.pager.init_page(index)
	
	def close_window(self):
		if WinMsg.ask("你确定要退出吗？"):
			Cache.exit_signal(exit=True)
			self.destroy()

	def view_rightwin(self, show=False):
		if show:
			if self.rightwin:
				return
			self.rightwin = tk.Frame(self, width=self.right_width, height=self.height, bg='Gray70')
			self.rightwin.pack(side=tk.LEFT)
			self.rightwin.pack_propagate(0)
		else:
			if not self.rightwin:
				return
			self.rightwin.destroy()
			self.rightwin = None
		
================ my_page.py
#-*- coding: UTF-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
#from tkinter.ttk import Combobox, Notebook, Style
from my_common import Globals,Common
from my_base import Pager
from my_module import ProgressBar


class StatePage(Pager):
	def __init__(self, master, iplist):
		self.master = master
		self.ip_list = iplist
		self.lab_width = 20
		self.ip_width = 16
		self.font = Globals.font()
		self.ip_state_dict = {}
		self.opt_dict = {	1: "项目  \  IP地址",
							2: "主备模式",
							3: "运行状态",
							4: "MRS容灾模式",
							5: "灾备对端IP",
							6: "keepalived状态",
							7: "MySQL运行状态",
							8: "MySQL同步状态",
							9: "文件同步状态",
							10: "与对端SSH互信状态",
							11: "浮动IP状态",
							12: "主备容灾告警"
						}

	def stepper(self):
		self.pack_frame()

	def pack_frame(self):
		# 占位用 
		#tk.Label(self.frame, height=5, bg='Gray90').grid(row=0, column=0)
		column, row = len(self.ip_list), len(self.opt_dict)
		for seq, name in self.opt_dict.items():
			tk.Label(self.frame, text=name, width=self.lab_width, \
				font=('-*-%s-*-*-*--*-140-*') % (self.font), bg='Gray80'\
				).grid(row=seq, column=0, padx=1, pady=1)
		for ip in self.ip_list:
			tk.Label(self.frame, text=ip, width=self.ip_width, \
				font=('-*-%s-*-*-*--*-140-*') % (self.font), bg='Gray80'\
				).grid(row=1, column=self.ip_list.index(ip)+1, padx=1, pady=1)
		for y in range(1, column+1):
			sub_list = []
			for x in range(2, row+1):	
				lab = tk.Label(self.frame, width=self.ip_width, \
					font=('-*-%s-*-*-*--*-120-*') % (self.font), bg='Snow')
				lab.grid(row=x, column=y)
				sub_list.append(lab)
			self.ip_state_dict[self.ip_list[y-1]] = sub_list
		#print(self.ip_state_dict)

	def fill_data(self, ip_dict):
		''' 单个IP填充，不影响其他IP '''
		ip, = ip_dict
		state_list, = ip_dict.values()
		if ip not in self.ip_state_dict:
			return 
		index = 0
		for lab in self.ip_state_dict[ip]:
			state = state_list[index]
			if state == 'NA':
				lab['fg'] = 'Black'
			elif state == 'Fail':
				lab['fg'] = 'Red'
			else:
				lab['fg'] = 'MediumBlue'
			lab['text'] = state
			index += 1

	@classmethod
	def parse_state_data(cls, data_str):
		out_list = []
		for key in ['HA_MODE', 'HA_STATUS', 'MRS_HA_MODE', 'REMOTE_IP',\
		'KEEPALIVED_STATUS', 'MYSQL_STATUS', 'MYSQL_SYNC', 'FILE_SYNC',\
		'SSH_TRUST', 'VIP_STATUS', 'HA_ALARM']:
			out_list.append(Common.find_val_in_str(data_str, key))
		return tuple(out_list)



class BinlogPage(Pager):
	def __init__(self, master, iplist, start_cmd):
		self.master = master
		self.ip_list = iplist
		self.start_cmd = start_cmd

	def stepper(self):
		self.pack_frame()

	def start_cmd_wrapper(self, index, combo, prog):
		day_str = combo.get()
		if day_str == '一天':
			days = 1
		elif day_str == '三天':
			days = 3
		elif day_str == '七天':
			days = 7
		else:
			days = 1
		self.start_cmd(index, days, prog)

	def pack_frame(self):
		for x in range(len(self.ip_list)):
			# 进度条 
			prog = ProgressBar(self.frame, self.ip_list[x],width=40, row=x)
			prog.update(0.0)
			# 下拉框 (选择天数)
			combo = ttk.Combobox(self.frame, width=6)
			combo['values'] = ('一天', '三天', '七天')
			combo.current(0)
			combo['state'] = 'readonly'
			combo.grid(row=x, column=2, padx=5)
			# 开始按钮
			tk.Button(self.frame, text='开始获取', command= \
				lambda index=x, combo=combo, prog=prog: \
				self.start_cmd_wrapper(index, combo, prog)).\
				grid(row=x, column=3, padx=5, pady=8)


class HAlogPage(Pager):
	def __init__(self, master, iplist, start_cmd):
		self.master = master
		self.ip_list = iplist
		self.start_cmd = start_cmd

	def stepper(self):
		self.pack_frame()

	def start_cmd_wrapper(self, index, prog):
		self.start_cmd(index, prog)

	def pack_frame(self):
		for x in range(len(self.ip_list)):
			# 进度条 
			prog = ProgressBar(self.frame, self.ip_list[x],width=40, row=x)
			prog.update(0.0)
			# 开始按钮
			tk.Button(self.frame, text='开始获取', command= \
				lambda index=x, prog=prog: self.start_cmd_wrapper\
				(index, prog)).grid(row=x, column=3, padx=5, pady=8)


class OtherLogPage(Pager):
	def __init__(self, master, iplist):
		self.master = master
		self.ip_list = iplist
		self.font = Globals.font()
		self.log_type = (	'== 以下所有 ==',
							'数据库日志    (eappmysql.err)',
							'操作系统日志  (messages)',
							'eApp操作日志  (TBL_UserLog)',
							'deploy文件    (deploy_proxy_4.0.xml)',
							'版本信息文件  (version.mdc.ini)'
						)

	def pack_frame(self):
		path_fm = tk.LabelFrame(self.frame)
		oper_fm = tk.LabelFrame(self.frame)
		path_fm.pack()
		oper_fm.pack()
		tk.Label(path_fm, text=' 日志路径： ', font=('-*-%s-*-*-*--*-160-*') %\
			(self.font)).grid(row=0, column=0)
		self.path_en = tk.Entry(path_fm, font=('-*-%s-*-*-*--*-160-*') %\
			(self.font), width=68)
		self.path_en.grid(row=0, column=1, pady=10)
		tk.Label(path_fm, text=' 其他日志： ', font=('-*-%s-*-*-*--*-160-*') %\
			(self.font)).grid(row=1, column=0)
		self.type_en = ttk.Combobox(path_fm, font=('-*-%s-*-*-*--*-160-*') %\
			(self.font), width=66, state='readonly', values=self.log_type)
		self.type_en.grid(row=1, column=1, pady=10)
		self.progress = ProgressBar(oper_fm, '进度:', width=40)
		choose_ip = tuple(['--- 请选择IP ---'] + self.ip_list)
		self.ipchoo_en = ttk.Combobox(oper_fm, font=('-*-%s-*-*-*--*-160-*') %\
			(self.font), width=16, state='readonly', values=choose_ip)
		self.ipchoo_en.current(0)
		self.ipchoo_en.grid(row=1, column=2, padx=13)
		self.start_btn = tk.Button(oper_fm, font=('-*-%s-*-*-*--*-160-*') %\
		(self.font), text=' 开始采集 ', width=18, command=self.collect_start)
		self.start_btn.grid(row=1, column=3, pady=10)

	def stepper(self):
		self.pack_frame()

	def collect_start(self, event=None):
		pass
		#Common.test_func()

	def destroy(self):
		self.frame.destroy()


if __name__ == '__main__':
	class ROOT(tk.Tk):
		@classmethod
		def callback(cls, x, y):
			print('callback:', x, y)

		def __init__(self):
			tk.Tk.__init__(self)

			fm = tk.Frame(self, width=700, height=400, bg='Gray')
			fm.pack()
			fm1 = tk.Frame(self, width=700, height=100, bg='Gray70')
			fm1.pack()
			fm2 = tk.Frame(self, width=700, height=100, bg='Gray70')
			fm2.pack()
			fm3 = tk.Frame(self, width=700, height=100, bg='Gray70')
			fm3.pack()

			ip_list = ['10.160.154.23','10.160.155.68','10.160.151.141']
			page = StatePage(fm, ip_list)
			page.pack()
			prog = ProgressBar(fm1, '进度: ', width=40)
			prog.update(0.50, color=True)
			binlog = BinlogPage(fm2, ip_list, self.callback)
			binlog.pack()
			log = OtherLogPage(fm3, ip_list)
			log.pack()

	def main():
		root = ROOT()
		root.mainloop()

	main()

================= my_handler.py
#-*- coding: UTF-8 -*-

import os
import sys
import base64
from my_images import Images,Shells
from my_logger import Logger
from my_base import Handler,ExecError
from my_common import Globals,Common,Cache
from my_message import WinMsg,GuiTig,Checker,Tell
from my_ssh import SSH,SSHUtil
from my_page import StatePage,BinlogPage,HAlogPage


class EnvUtil:
	@classmethod
	def init(cls):
		basedir = Globals.get_basedir()
		cls.dir_init(basedir)
		cls.image_init(basedir)
		cls.pack_init(basedir)
		cls.log_init(basedir)

	@classmethod
	def log_init(cls, basedir):
		return  Logger('\\'.join([basedir, 'get_binlog.log']))

	@classmethod
	def dir_init(cls, basedir):
		if not os.path.exists(basedir):
			os.makedirs(basedir)
		if not os.path.exists('\\'.join([basedir, 'image'])):
			os.makedirs('\\'.join([basedir, 'image']))
		if not os.path.exists('\\'.join([basedir, 'cmds'])):
			os.makedirs('\\'.join([basedir, 'cmds']))
		Cache.execute_dir(dir=os.path.split(sys.argv[0])[0])

	@classmethod
	def image_init(cls, basedir):
		imgdir = '\\'.join([basedir, 'image'])
		if not os.path.exists('\\'.join([imgdir, 'item.ico'])):
			file_str = open('\\'.join([imgdir, 'item.ico']), 'wb')
			file_str.write(base64.b64decode(Images.item_str))
			file_str.close()
		if not os.path.exists('\\'.join([imgdir, 'eye.png'])):
			file_str = open('\\'.join([imgdir, 'eye.png']), 'wb')
			file_str.write(base64.b64decode(Images.eye_str))
			file_str.close()
		if not os.path.exists('\\'.join([imgdir, 'add.png'])):
			file_str = open('\\'.join([imgdir, 'add.png']), 'wb')
			file_str.write(base64.b64decode(Images.add_str))
			file_str.close()
		if not os.path.exists('\\'.join([imgdir, 'set.png'])):
			file_str = open('\\'.join([imgdir, 'set.png']), 'wb')
			file_str.write(base64.b64decode(Images.set_str))
			file_str.close()
		if not os.path.exists('\\'.join([imgdir, 'head.jpg'])):
			file_str = open('\\'.join([imgdir, 'head.jpg']), 'wb')
			file_str.write(base64.b64decode(Images.head_str))
			file_str.close()

	@classmethod
	def pack_init(cls, basedir):
		cmddir = '\\'.join([basedir, 'cmds'])
		if not os.path.exists('\\'.join([cmddir, Globals.package()])):
			file_str = open('\\'.join([cmddir, Globals.package()]), 'wb')
			file_str.write(base64.b64decode(Shells.pack_str))
			file_str.close()

	@classmethod
	def upload_package(cls):
		Tell.tell_info('正在上传必要文件到服务器...')
		for ip in Cache.get_logon_info():
			ssh_inst = Cache.get_ssh_instance(ip)
			pack_path = '\\cmds\\'.join([Globals.get_basedir(), Globals.package()])
			remote_path = '/'.join([Globals.server_dir(), Globals.package()])
			# 上传package并解压
			cls.upload_and_uncompress(ip, ssh_inst, pack_path, remote_path)

	@classmethod
	def upload_and_uncompress(cls, ip, ssh_inst, pack_path, remote_path):
		try:
			# 如果上次登录用户跟这次不一致，会导致后面解压失败 
			# 这里刚登录时，每次清空目录
			SSHUtil.exec_ret(ssh_inst, 'rm -rf %s/*' % (Globals.server_dir()))

			if not SSHUtil.upload_file(ssh_inst, pack_path, remote_path):
				raise ExecError('上传package.7z失败')
			cmd = 'cd %s && /usr/local/bin/7za x %s -aoa' % \
			(Globals.server_dir(), remote_path)
			# 成功返回0
			if SSHUtil.exec_ret(ssh_inst, cmd):
				raise ExecError('解压package.7z失败')
			Tell.tell_info('%s 必要文件准备成功' % (ip))
			Cache.add_prepare_ip(ip)
		except ExecError as e:
			Tell.tell_info('%s 必要文件准备失败: %s' % (ip, e))
			Cache.del_prepare_ip(ip)

	@classmethod
	def collect_state_thread(cls, callback_fill_data):
		period = 5
		while not Cache.exit_signal():
			Common.sleep(period)
			period = 30
			cls.collect_server_state()
			callback_fill_data()

	@classmethod
	def collect_server_state(cls):
		for ip in Cache.get_prepare_ip():
			data_str = SSHUtil.exec_info(Cache.get_ssh_instance(ip),
								'/'.join([Globals.server_dir(), 
								Globals.collect_state_sh()]), 
								root=True
							)
			state_tuple = StatePage.parse_state_data(data_str)
			Cache.set_ip_state_dict({ip: state_tuple})
		#print(Cache.get_ip_state_dict())


class LoginDealer(Handler):
	def __init__(self, login_instance):
		self.login_instance = login_instance
		self.server_infos = {}

	def try_login(self):
		for seq, inst in self.login_instance.items():
			ip = inst.ip_en.get()
			user = inst.user_en.get()
			upwd = inst.upwd_en.get()
			rpwd = inst.rpwd_en.get()
			if not Checker.check_input_ip(ip, inst.ip_en):
				return False
			if not Checker.check_input_user(user, inst.user_en):
				return False
			if not Checker.check_input_upwd(upwd, inst.upwd_en):
				return False
			if not Checker.check_input_rpwd(rpwd, inst.rpwd_en):
				return False

			inst.tig_login('LGING')
			ssh = SSH(ip, user, upwd, rpwd)
			if not SSHUtil.user_login(ssh, inst):
				return False
			if not SSHUtil.root_login(ssh, inst):
				return False

			# 登录成功，记录IP信息及ssh实例
			Cache.add_ssh_instance(ip, ssh)

			Cache.add_logon_info(ip, [user, upwd, rpwd])

			inst.tig_login('SUCC')
		return True

	def stepper(self):
		if not self.try_login():
			Cache.del_ssh_instance('all')
			Cache.del_logon_info('all')
			return False
		return True


class PageDealer(object):
	def __init__(self, master, view_rightwin):
		self.master = master
		self.view_rightwin = view_rightwin
		self.current_index = 0
		self.current_view = None
		self.ip_list = list(Cache.get_logon_info().keys())

	def init_page(self, index):
		self.current_index = index
		if self.current_view:
			self.current_view.destroy()
		if index == 1:
			page = StatePage(self.master, self.ip_list)
			page.pack()
			self.current_view = page
			# 数据填充在pack之后，且在后台进行
			Common.create_thread(func=self.fill_state_data)
		elif index == 2:
			page = HAlogPage(self.master, self.ip_list, self.halog_start)
			page.pack()
		elif index == 3:
			page = BinlogPage(self.master, self.ip_list, self.binlog_start)
			page.pack()
		elif index == 4:
			WinMsg.info("敬请期待")
			return
		elif index == 5:
			WinMsg.info("敬请期待")
			return
		elif index == 6:
			WinMsg.info("敬请期待")
			return
		elif index == 7:
			WinMsg.info("敬请期待")
			return
		else:
			WinMsg.info("敬请期待")
			return
		self.current_view = page

	def halog_start(self, index, prog):
		Common.create_thread(func=self.get_halog, args=(index, prog))

	def get_halog(self, index, prog):
		prog.update(0.2)
		Tell.tell_info('%s 正在获取主备日志...' % (self.ip_list[index]))
		if not SSHUtil.template_shell_and_download(
							Cache.get_ssh_instance(self.ip_list[index]),
							prog,
							'%s/%s' % (Globals.server_dir(), Globals.halog_sh()),
							Cache.execute_dir(),
							root=True):
			Tell.tell_info('%s 获取主备日志失败，请确认是否为非单机模式' % \
				(self.ip_list[index]), level='ERROR')
		else: 
			Tell.tell_info('%s 获取主备日志成功，文件在可执行程序目录下' % \
				(self.ip_list[index]), level='TIG')

	def binlog_start(self, index, days, prog):
		Common.create_thread(func=self.get_binlog, args=(index, days, prog))

	def get_binlog(self, index, days, prog):
		prog.update(0.2)
		Tell.tell_info('%s 正在获取%s天的Bin-log...' % (self.ip_list[index], days))
		if not SSHUtil.template_shell_and_download(
							Cache.get_ssh_instance(self.ip_list[index]),
							prog,
							'%s/%s %s' % (Globals.server_dir(), Globals.binlog_sh(), days),
							Cache.execute_dir(),
							root=True):
			Tell.tell_info('%s 获取Bin-log失败，请确认是否为非单机模式' % \
				(self.ip_list[index]), level='ERROR')
		else: 
			Tell.tell_info('%s 获取Bin-log成功，文件在可执行程序目录下' % \
				(self.ip_list[index]), level='TIG')

	def close_window(self):
		self.destory()
		
	def fill_state_data(self):
		if self.current_index != 2:
			return
		for ip, state_tuple in Cache.get_ip_state_dict().items():
			self.current_view.fill_data({ip: state_tuple})

	def after_login_deal(self):
		Common.sleep(1)
		# 上传必要文件
		Common.create_thread(func=EnvUtil.upload_package)
		# 定时收集服务器状态并显示 
		Common.create_thread(func=EnvUtil.collect_state_thread, args=(self.fill_state_data,))

============== my_message.py
#-*- coding: UTF-8 -*-

import time
import tkinter.messagebox
from my_common import Common,Cache


class Tell:
	@classmethod
	def tell_info(cls, info, level='INFO'):
		infowin_inst = Cache.infowin_inst()
		if not infowin_inst:
			return
		if level == 'WARN':
			color = 'DarkOrange'
		elif level == 'INFO':
			color = 'MediumSeaGreen'
		elif level == 'ERROR':
			color = 'red'
		elif level == 'TIG':
			color = 'Purple'
		else:
			color = 'Blue'
		info = "\n%s [%s]: %s" % (Common.get_time(), level.upper(), str(info))
		infowin_inst.tell(info, color)


class WinMsg:
	@classmethod
	def info(cls, info):
		tkinter.messagebox.showinfo('Information', info)

	@classmethod
	def error(cls, info):
		tkinter.messagebox.showerror('Error', info)

	@classmethod
	def ask(cls, info):
		return tkinter.messagebox.askokcancel('Ask', info)

	@classmethod
	def warn(cls, info):
		tkinter.messagebox.showwarning('Warn', info)


class GuiTig:
	@classmethod
	def change_color_tig(cls, instance, which='bg', backcolor='White'):
		Common.create_thread(cls.update_color, args=(instance, which, backcolor))

	@classmethod
	def update_color(cls,instance, who='bg', backcolor='White'):
		sleep = 0.4
		instance[who] = 'red'
		time.sleep(sleep)
		instance[who] = 'Gold'
		time.sleep(sleep)
		instance[who] = 'red'
		time.sleep(sleep)
		instance[who] = 'Gold'
		time.sleep(sleep)
		instance[who] = 'red'
		time.sleep(sleep)
		instance[who] = 'Gold'
		time.sleep(sleep)
		instance[who] = backcolor


class Checker:
	@classmethod
	def check_input_ip(cls, ip=None, instance=None):
		if not ip:
			WinMsg.warn('请输入服务器IP地址')
			GuiTig.change_color_tig(instance)
			return False
		elif not Common.is_ip(ip):
			WinMsg.warn('请输入正确的IP地址')
			GuiTig.change_color_tig(instance)
			return False
		elif ip in Cache.get_logon_info():
			WinMsg.warn('%s已经登录，不能重复登录')
			GuiTig.change_color_tig(instance)
			return False
		return True

	@classmethod
	def check_input_user(cls, user=None, instance=None):
		if not user:
			WinMsg.warn('请输入用户名')
			GuiTig.change_color_tig(instance)
			return False
		return True

	@classmethod
	def check_input_upwd(cls, upwd=None, instance=None):
		if not upwd:
			WinMsg.warn('请输入用户密码')
			GuiTig.change_color_tig(instance)
			return False
		return True

	@classmethod
	def check_input_rpwd(cls, rpwd=None, instance=None):
		if not rpwd:
			WinMsg.warn('请输入root密码')
			GuiTig.change_color_tig(instance)
			return False
		return True

======= my_images.py
#-*- coding: UTF-8 -*-

class Images:
	item_str = '''AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAABMLAAATCwAAAAAAAAAAAAD+/v4A/v7+AP7+/gD+/v4A9PjtALvYkgCSwE4AfbUtAIC2MQCWw1UAw9yfAPn79QD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A1+i/AH61LwB0rx7/dK8e/3SvHv90rx7/dK8e/3SvHv+FuTr/4+7SAP7+/gD+/v4A/v7+AP7+/gD+/v4A2unDAHixJAB0rx7/da8f/5XCU/+z04T/sNKA/42+R/90rx7/dK8e/3y0K//n8dkA/v7+AP7+/gD+/v4A+fv3AIS4OAB0rx7/erMo/9bnvf/+/v7//v7+//7+/v/+/v7/x96k/3awIf90rx7/ksBP//7+/gD+/v4A/v7+AMzhrAB0rx7/dK8e/8vhq//+/v7/+/z5/9PluP/c68f//v7+//7+/v+11Ij/dK8e/3SvHv/g7czX/v7+AP7+/gCqznUAdK8e/3y0LP/8/fv//v7+/57HYv90rx7/dK8e/8Dbmf/+/v7/7/bm/3SvHv90rx7/vdmU//7+/gD+/v4AnMZfAHSvHv+Ovkf//v7+//3+/f92sCH/dK8e/3SvHv+Xw1f//v7+//7+/v94siX/dK8e/7HSgP/+/v4A/v7+AKnNcwB0rx7/jr5I//7+/v/+/v7/ospp/3SvHv90rx7/xN2g//7+/v/x9+n/dK8e/3SvHv+72JH//v7+AP7+/gDK4KkAdK8e/46+SP/+/v7//v7+//z9+//Z6cL/4u7R//7+/v/+/v7/uNaM/3SvHv90rx7/3evJ//7+/gD+/v4A+Pv0AIG3M/+Ovkj//v7+//7+/v/+/v7//v7+//7+/v/+/v7/zeKu/3exI/90rx7/j79K//7+/eH+/v4A/v7+AP7+/gDW57wAkL9L//7+/v/+/v7/qs52/7vYkv+92ZX/k8FR/3SvHv90rx7/erMo/+Tv0//+/v4A/v7+AP7+/gD+/v4A/v7+AN/szAD+/v7//v7+/4+/Sf90rx7/dK8e/3SvHv90rx7/eLIl/9rpw//+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/v+Pvkn/dK8e/3SvHv90rx7/drAi/9Llt//+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4Aj75J/3SvHv90rx7/dbAf/8ngp//+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AK/RfQp0rx7/da8f/8Xeov/+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4As9OEUr7Zl//+/v4A/v7+AP7+/gD+/v4A/v7+AP7+/gD+/v4A//8AAPgPAADwBwAA4AMAAMADAADAAQAAwAEAAMABAADAAQAAwAMAAOADAADwBwAA+A8AAPwfAAD+PwAA/38AAA=='''
	eye_str = '''iVBORw0KGgoAAAANSUhEUgAAABQAAAAKCAMAAACDi47UAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMDY3IDc5LjE1Nzc0NywgMjAxNS8wMy8zMC0yMzo0MDo0MiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTUgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkM0RjY0RUEyNDIxNjExRTlBQzQ2OUYwRkY1QUIzNTk4IiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkM0RjY0RUEzNDIxNjExRTlBQzQ2OUYwRkY1QUIzNTk4Ij4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6QzRGNjRFQTA0MjE2MTFFOUFDNDY5RjBGRjVBQjM1OTgiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6QzRGNjRFQTE0MjE2MTFFOUFDNDY5RjBGRjVBQjM1OTgiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7JYXkQAAAAGFBMVEWysrJycnLc3NxVVVX39/f///8AAAD////GbIv4AAAACHRSTlP/////////AN6DvVkAAABmSURBVHjaTI5ZDsQwCEO9kdz/xuOW+ailCMVgeLiPIp6KyPtF35A+SnRMzJoywlxl4jZUc+Bc4PocT2vIwRtgJyqFXQajjZrKx+TG9Y/ridfaQ95DDKwPEiLYS4qFxwNva+F/AgwAVt0DOaKwoiYAAAAASUVORK5CYII='''
	add_str = '''iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAACjElEQVRIicXXy4vOURgH8M+Ml3JLgxkLkiFKzWp2bDQoUrOgJtnJP4Ale7ciZWlLSmLNYrYsCEW55TbkGtMQRY3X4jwvx9v7u5hGvvWr0znf5/v9ndM5z3lOl2p0YRHWYgvWYy5Wx/gjfMFVXME9fECzhnYhlmIfXoRQne9FxCytmk0nzMAIDqM/63+Pt/iOp9HXj1lYgt6M+xQHcQGTlVPEPBxtm8VtnMJQSdxQcG63xR4NzVLMxJksaDwC59f548D8iBnPdM6GdiGOZ+QnGC7gbcfu+LYXcIZDo6V3vMh0JCO9wWDJD37LuN9KeIOh1eKOtBN6MRaDn7GpRAweZGIPKrgb8Sm4Y7IN2I29mdDJCqG/NRaaLf7e8NSDl9H5CIv/gfHi0G6GVw9pEzTxA8dqiEzFGI5I57mJ4QY2x8B7XKwpMhVcwh70YXMDAzHwDjdqijQL2mW4GR59GGhgZQy8kZYbdkhLU4QVWbtf+XIfkGY7GR4DWNnAgiCMZ+SFWFM1hcCsCu7CrN3yWNCoKT7taGBC2t49Wf9HPCyJWyHNlHRTPSvhfszaLY8JGJU2yB3pOqyD+34fp/s1Y2aERxOjDdyV0lqflFuv1xDpKmiXYTA8hOevBDKpfCfnmEoCOSxLIKR1f+U/pMxu7M+ETvwD4xM6XBKkq+p5DExgwzQabwjNZnj0thN2ZWKvTV8h8Drj7upE6sbpjPQE2woE65Q+2/xZ+pyWLXE7ZuNcRv6AQ1IBXxdzI6ZV1DdDc3ZVYKtKzEvUW+qXt7faYjtWqWUF/U7pXC/P+vOC/nH0rdK5oB+Tbqbzahb0OZaZ+hNmWZlwnXTXerQNYCvWYY7fV+FDfMU1XJbSYeWj7ScAEvc9hCf9DgAAAABJRU5ErkJggg=='''
	set_str = '''iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAMAAAAM7l6QAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6REE0MUU4NTFBMTc4MTFFOUE5MDlDM0NDQzYzNjc3MUQiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6REE0MUU4NTJBMTc4MTFFOUE5MDlDM0NDQzYzNjc3MUQiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpEQTQxRTg0RkExNzgxMUU5QTkwOUMzQ0NDNjM2NzcxRCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpEQTQxRTg1MEExNzgxMUU5QTkwOUMzQ0NDNjM2NzcxRCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PlmYI3oAAAAMUExURQAAAOrq7Hh4gv///yXctSkAAAAEdFJOU////wBAKqn0AAAAu0lEQVR42oRT0RbFIAgC+v9/vkuy3D21fFkTMTRFW0ZBgFhcqDDCNjC77yGThPJ/ws4ZxCdFj4mgATur7AoBGDhC0UNQ3tpjFXwatp95nw/2LvjPJtw4dLzMStAqnesGtwejW6NryK4lvDT3g7KrqV+ToPi+UgWTRWpRQtYnmPo161xS9vA1+UVaKQwuDLUwB/LUFivcNBUJ6/NJLg96GAcl/D1MMajnUTQjCPtBnmvA/Rrclui0gj8BBgB3zQba5Vka7QAAAABJRU5ErkJggg=='''
	head_str = '''/9j/4QAYRXhpZgAASUkqAAgAAAAAAAAAAAAAAP/sABFEdWNreQABAAQAAAAAAAD/4QOFaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA1LjMtYzAxMSA2Ni4xNDU2NjEsIDIwMTIvMDIvMDYtMTQ6NTY6MjcgICAgICAgICI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6NjQwMjAzNTMtODBkNS1lNTRmLWFkNjQtYWNiMWQ4NTI1MmFhIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkU1Q0ZGQjM2QTE3OTExRTlCRTczRjQyMkZGNDE2NkVDIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkU1Q0ZGQjM1QTE3OTExRTlCRTczRjQyMkZGNDE2NkVDIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCBDUzYgKFdpbmRvd3MpIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6QzBCMzEwMzgzNzI0RTkxMTk2MkRFRTUzQkUzNkM2RDEiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDoyNWM2ZGQ3ZS0yM2U3LTExZTktOTJkOS1hYmU2Y2M1OTM0MTIiLz4gPC9yZGY6RGVzY3Jp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'''

class Shells:
	pack_str = '''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'''

============== my_base.py
#-*- coding: UTF-8 -*-

import time
import tkinter as tk


class SSHError(Exception):
	''' SSH登录失败异常 '''
	pass

class ExecError(Exception):
	''' SSH 执行失败异常 '''
	pass


class Handler(object):
	""" 作为线程处理的基类 """
	""" 使用__new__实现抽象单例 """
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, '_instance'):
			cls._instance = super(Handler, cls).__new__(cls)
		return cls._instance

	def _enter(self):
		self.__s_time = time.time()

	def _exit(self):
		self.__e_time = time.time()
		self.__u_time = '%.3f' % (self.__e_time - self.__s_time)

	def counter(self):
		return self.__u_time

	def stepper(self):
		pass

	def handler(self):
		self._enter()
		self.__result = self.stepper()
		self._exit()

	def result(self):
		return self.__result


class Pager(object):
	frame = None
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, '_instance'):
			cls._instance = super(Pager, cls).__new__(cls)
		return cls._instance
	
	def _init(self):
		self.frame = tk.LabelFrame(self.master, bg='Gray90')
		self.frame.pack()

	def pack(self):
		self._init()
		self.stepper()

	def stepper(self):
		pass

	def destroy(self):
		try:
			self.frame.destroy()
		except:
			pass

================ my_common.py
#-*- coding: UTF-8 -*-

import re
import time
import threading


class Globals:
	'''
	静态全局变量
	'''
	@classmethod
	def get_basedir(cls):
		return 'C:\\Bingo\\Binlog'

	@classmethod
	def server_dir(cls):
		return '/home/Bingo'

	@classmethod
	def title(cls):
		return "主备工具 V1.0"

	@classmethod
	def font(cls):
		return '微软雅黑'

	@classmethod
	def welcome(cls):
		return ' ' * 60 + '【 欢迎使用主备工具 】'

	@classmethod
	def big_font(cls):
		return '楷体'

	@classmethod
	def color(cls):
		return 'SlateGray'

	@classmethod
	def bg_color(cls):
		return 'Gray'

	@classmethod
	def package(cls):
		return 'package.7z'

	@classmethod
	def binlog_sh(cls):
		return 'get_binlog.sh'

	@classmethod
	def halog_sh(cls):
		return 'get_halogs.sh'

	@classmethod
	def collect_state_sh(cls):
		return 'collect_state.sh'

	@classmethod
	def label_bg(cls):
		return 'Snow'

	@classmethod
	def enter_bg(cls):
		return 'Gray70'

	@classmethod
	def enter_fg(cls):
		return 'DarkGreen'

	@classmethod
	def leave_fg(cls):
		return 'Black'

	@classmethod
	def leave_bg(cls):
		return 'Gray'

	@classmethod
	def title(cls):
		return '主备工具'


class Common:
	'''
	公共方法
	'''
	@classmethod
	def get_time(cls):
		ct = time.time()
		msec = (ct - int(ct)) * 1000
		return '%s.%03d' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),msec)

	@classmethod
	def write_to_file(cls, filename, info):
		try:
			with open(filename, 'w') as f:
				f.write(info)
				return True
		except:
			return False

	@classmethod
	def create_thread(cls, func, args=()):
		th=threading.Thread(target=func, args=args)
		th.setDaemon(True)
		th.start()

	@classmethod
	def is_ip(cls, ip):
		p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
		if p.match(ip):
			return True
		else:
			return False

	@classmethod
	def sleep(cls, sec):
		time.sleep(sec)

	@classmethod
	def find_val_in_str(cls, in_str, key):
		return re.findall(r'%s:.*' % (key), in_str)[0].split(':')[-1]


class Cache:
	'''
	全局变量(动态内存)
	'''
	# exe文件路径
	_localbasedir = None
	# 图片image实例
	_imginsdict = {}
	# 登录成功的IP
	_logon_dict = {}
	# 登录IP对应的SSH和实例
	_ssh_inst_dict = {}
	# IP对应的SubLogin实例
	_login_inst_dict = {}
	# 屏幕大小
	_screen_size = []
	# 是否退出
	_is_exit = False
	# 信息栏实例 
	_info_inst = None
	# 成功上传完毕package的IP列表
	_prepare_ip = []
	# 各个IP的巡检状态结果
	_ip_state = {}

	@classmethod
	def windows_size(cls, size=None):
		if size:
			cls._screen_size = size
		else:
			return cls._screen_size

	@classmethod
	def execute_dir(cls, dir=None):
		if dir:
			cls._localbasedir = dir
		else:
			return cls._localbasedir

	@classmethod
	def exit_signal(cls, exit=None):
		if exit in [True, False]:
			cls._is_exit = exit
		else:
			return cls._is_exit
			
	@classmethod
	def image_instance(cls, **keyv):
		for key in keyv:
			cls._imginsdict[key] = keyv[key]

	@classmethod
	def get_image_instance(cls, key):
		return cls._imginsdict[key]

	@classmethod
	def get_logon_info(cls):
		return cls._logon_dict

	@classmethod
	def del_logon_info(cls, ip):
		if ip == 'all':
			cls._logon_dict = {}
		elif ip in cls._logon_dict:
			del cls._logon_dict[ip]

	@classmethod
	def add_logon_info(cls, ip, auth_list):
		if ip not in cls._logon_dict:
			cls._logon_dict[ip] = auth_list

	@classmethod
	def get_ssh_instance(cls, ip):
		return cls._ssh_inst_dict[ip]

	@classmethod
	def add_ssh_instance(cls, ip, ssh_inst):
		if ip not in cls._ssh_inst_dict:
			cls._ssh_inst_dict[ip] = ssh_inst

	@classmethod
	def del_ssh_instance(cls, ip):
		if ip == 'all':
			cls._ssh_inst_dict = {}
		elif ip in cls._ssh_inst_dict:
			del cls._ssh_inst_dict[ip]

	@classmethod
	def infowin_inst(cls, info_inst=None):
		if info_inst:
			cls._info_inst = info_inst
		else:
			return cls._info_inst

	@classmethod
	def get_prepare_ip(cls):
		return cls._prepare_ip


	@classmethod
	def add_prepare_ip(cls, ip):
		if ip not in cls._prepare_ip:
			cls._prepare_ip.append(ip)

	@classmethod
	def del_prepare_ip(cls, ip):
		if ip == 'all':
			cls._prepare_ip = []
		elif ip in cls._prepare_ip:
			cls._prepare_ip.remove(ip)

	@classmethod
	def get_ip_state_dict(cls):
		return cls._ip_state

	@classmethod
	def set_ip_state_dict(cls, in_dict):
		ip, = in_dict
		value, = in_dict.values()
		cls._ip_state[ip] = value

========== my_setting.py
#-*- coding: UTF-8 -*-

class Settings():
	def __init__(self):
		self.default_user_info = ['ubp', 'eLTE@com123', 'eLTE@com']

	def get_passwd_info(self):
		return self.default_user_info

============ my_module.py
#-*- coding: UTF-8 -*-

import tkinter as tk
from my_common import Globals


class ProgressBar:
	'''比例条'''
	def __init__(self, master, name, width=32, row=1, column=0):
		self.master = master
		self.name = name
		self.width = width
		self.row = row
		self.column = column
		self.namelab = None
		self.bglab = None
		self.fglab = None
		self.value = 0
		self.pack()

	def pack(self):
		self.namelab = tk.Label(self.master, text=self.name)
		self.namelab.grid(row=self.row, column=self.column, padx=5, pady=5)
		self.bglab = tk.Label(self.master, relief='solid', bd=1, \
			width=self.width, bg='snow', anchor=tk.E)
		self.fglab = tk.Label(self.master, relief='solid', bd=1)
		self.bglab.grid(row=self.row, column=self.column + 1, sticky=tk.W)
		self.fglab.grid(row=self.row, column=self.column + 1, sticky=tk.W)

	def update(self, value, color=False):
		if self.value == value:
			return
		self.value = value
		sub = int(self.width * value)
		percent = '%s%%' % (value * 100)
		fg_color = 'PaleTurquoise'
		if value > 0.5:
			self.bglab['text'] = ''
			self.fglab['text'] = percent
		else:
			self.bglab['text'] = ''.join([str(percent), ' ' * 6])
			self.fglab['text'] = ''
		if color:
			if 0.0 <= value < 0.3:
				fg_color = 'PaleTurquoise'
			elif 0.3 <= value < 0.5:
				fg_color = 'Turquoise'
			elif 0.5 <= value < 0.7:
				fg_color = 'Gold'
			elif 0.7 <= value < 0.85:
				fg_color = 'Coral'
			elif 0.85 <= value < 0.95:
				fg_color = 'OrangeRed'
			elif 0.95 <= value <= 1.0:
				fg_color = 'Red3'
		self.fglab['width'] = sub
		self.fglab['bg'] = fg_color

	def destroy(self):
		self.namelab.destroy()
		self.bglab.destroy()
		self.fglab.destroy()


class InfoWindow(object):
	''' 消息提示栏 '''
	def __init__(self, master):
		self.master = master
		self.font = Globals.font()
		self.tag_i = 0
		self.init()

	def init(self):
		self.infotext = tk.Text(self.master, font=('-*-%s-*-*-*--*-120-*')%(self.font),\
			bd=2, relief='ridge', fg='Blue', bg='AliceBlue', height=9, width=110)
		self.infotext.insert(tk.END, Globals.welcome())
		self.infotext['stat'] = 'disabled'
		self.infotext.pack()

	def tell(self, info, color):
		self.tag_i += 1
		self.infotext['stat'] = 'normal'
		self.infotext.insert(tk.END, info)
		line = self.infotext.index(tk.END)
		line = int(line.split('.')[0]) - 1
		self.infotext.tag_add('BINGO%s' % (self.tag_i),'%s.0' % (line),'%s.end' % (line))
		self.infotext.tag_config('BINGO%s' % (self.tag_i), foreground=color)
		self.infotext.see(tk.END)
		self.infotext['stat'] = 'disabled'


class LabelButton():
	''' Radiobutton实现的侧边菜单栏 '''
	def __init__(self, master, seq, intvar, text, command):
		self.btn_seq = seq
		self.btn_text = text
		self.command = command
		self.font = Globals.big_font()
		self.font_size = 22
		self.button = tk.Radiobutton(master, selectcolor=Globals.label_bg(), 
			fg='Black', bg='PaleTurquoise4', variable=intvar, width=20, bd=0, \
			indicatoron=0, value=seq, text=text, font=('-*-%s-*-*-*--*-%s0-*') % \
			(self.font, self.font_size), command=self.click)
		self.button.bind("<Enter>", self.enter)
		self.button.bind("<Leave>", self.leave)

	def enter(self, event=None):
		self.button['fg'] = 'Brown1' #'Gray90'
		self.button['bg'] = 'PaleTurquoise3'

	def leave(self, event=None):
		self.button['fg'] = 'Black'
		self.button['bg'] = 'PaleTurquoise4'

	def pack(self):
		self.button.pack(ipady=21)

	def click(self, event=None):
		self.command(self.btn_seq)


class SubLogin():
	''' 登录子界面 '''
	def __init__(self, gui, sequence, login_instance):
		self.gui = gui
		self.sequence = sequence
		self.login_instance = login_instance
		self.var_user = tk.StringVar()
		self.var_upwd = tk.StringVar()
		self.var_rpwd = tk.StringVar()
		self.tig_color = ['Snow', 'Green', 'DimGray', 'Red']
		self.font = Globals.font()
		self.init()

	def init(self):
		self.taglab = tk.Label(self.gui, text='●', font=('-*-%s-*-*-*--*-180-*')\
			%(self.font), fg=self.tig_color[0])
		self.ip_en = tk.Entry(self.gui, relief='groove', width=15, bg='white',\
			font=('-*-%s-*-*-*--*-140-*')%(self.font))
		self.user_en = tk.Entry(self.gui, relief='groove', width=10, bg='white',\
			font=('-*-%s-*-*-*--*-140-*')%(self.font), textvariable=self.var_user)
		self.upwd_en = tk.Entry(self.gui, relief='groove', show='*', width=15,bg='white',\
			font=('-*-%s-*-*-*--*-140-*')%(self.font), textvariable=self.var_upwd)
		self.rpwd_en = tk.Entry(self.gui, relief='groove', show='*', width=15,bg='white',\
			font=('-*-%s-*-*-*--*-140-*')%(self.font), textvariable=self.var_rpwd)
		self.delbtn = tk.Button(self.gui, text='▬', font=('-*-%s-*-*-*--*-140-*')\
			% (self.font), bd=0, command=self.destroy)

	def pack(self):
		self.taglab.grid(row=self.sequence+1, column=0, padx=5, ipady=5)
		self.ip_en.grid(row=self.sequence+1, column=1, padx=8, ipady=5)
		self.user_en.grid(row=self.sequence+1, column=2, padx=8, ipady=5)
		self.upwd_en.grid(row=self.sequence+1, column=3, padx=8, ipady=5)
		self.rpwd_en.grid(row=self.sequence+1, column=4, padx=8, ipady=5)
		if self.sequence != 1:
			self.delbtn.grid(row=self.sequence+1, column=5, padx=5)
		self.login_instance[self.sequence] = self

	def destroy(self):
		self.taglab.grid_remove()
		self.ip_en.grid_remove()
		self.user_en.grid_remove()
		self.upwd_en.grid_remove()
		self.rpwd_en.grid_remove()
		if self.sequence != 1:
			self.delbtn.grid_remove()
		del self.login_instance[self.sequence]

	def see_passwd(self,onoff):
		if onoff == 'ON':
			self.upwd_en['show'] = ''
			self.rpwd_en['show'] = ''
		else:
			self.upwd_en['show'] = '*'
			self.rpwd_en['show'] = '*'

	def set_defaults(self, default_info):
		''' 设置默认用户和密码 '''
		self.var_user.set(default_info[0])
		self.var_upwd.set(default_info[1])
		self.var_rpwd.set(default_info[2])

	def tig_login(self,status):
		if status == 'DFLT':
			index = 0
		elif status == 'SUCC':
			index = 1
		elif status == 'LGING':
			index = 2
		elif status == 'FAIL':
			index = 3
		else:return
		self.taglab['fg'] = self.tig_color[index] 

========== my_ssh.py
#-*- coding: UTF-8 -*-

import os
#import traceback
import paramiko
from my_base import SSHError
from my_message import WinMsg,GuiTig


class SSH(object):
	''' paramiko ssh登录服务类 '''
	def __init__(self, ip, user, upwd, rpwd):
		self.host = ip
		self.user = user
		self.pswd = upwd
		self.rootpwd = rpwd
		self.port = 22
		self._ssh_fd = ''
		self.err_info = ''

	def get_ip(self):
		return self.ip

	def get_user(self):
		return self.user

	def get_user_passwd(self):
		return self.upwd

	def get_root_passwd(self):
		return self.rpwd

	def get_error_info(self):
		return self.err_info

	def exec_continue(self, cmd, root=False):
		if root:
			cmd = '''echo "%s" |su - -c "%s"'''%(self.rootpwd, cmd)
		#print('cmd=',cmd)
		try:
			a, b, c = self._ssh_fd.exec_command(cmd)
			return a, b, False
		except Exception as e:
			#print('[ERROR] continue exec fail: %s\n%s'%(cmd,str(e)))
			self.err_info = str(e)
			return False, False, str(e)

	def exec_cmd(self,cmd,root=False):
		if root:
			cmd = '''echo "%s" |su - -c "%s"'''%(self.rootpwd, cmd)
		try:
			self._ssh_fd = paramiko.SSHClient()
			self._ssh_fd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self._ssh_fd.connect(self.host, username=self.user, password=self.pswd)
			a, b, c = self._ssh_fd.exec_command(cmd)
			return a, b, False
		except Exception as e:
			#print('[ERROR] exec fail: %s\n%s'%(cmd,str(e)))
			self.err_info = str(e)
			return False, False, str(e)

	def close(self):
		return self._ssh_fd.close()

	def upload(self, local_path, server_path):
		try:
			t = paramiko.Transport((self.host, self.port))
			t.connect(username=self.user, password=self.pswd)
			sftp = paramiko.SFTPClient.from_transport(t)
			sftp.put(local_path, server_path)
			t.close()
			return True
		except Exception as e:
			self.err_info = str(e)
			return False

	def download(self, server_path, local_path):
		try:
			t = paramiko.Transport((self.host, self.port))
			t.connect(username=self.user, password=self.pswd)
			sftp = paramiko.SFTPClient.from_transport(t)
			sftp.get(server_path, local_path)
			t.close()
			return True
		except Exception as e:
			print(e)
			self.err_info = str(e)
			return False


class SSHUtil:
	@classmethod
	def _login(cls, ssh_inst, login_inst, root=False):
		if root:
			user, tig_en = 'root', login_inst.rpwd_en
		else:
			user, tig_en = ssh_inst.get_user(), login_inst.upwd_en
		out = ssh_inst.exec_cmd('whoami', root)[1]
		try:
			out = out.read().strip()
			out = str(out, encoding='utf-8')
			if user != out:
				raise SSHError('bad passwd')
		except Exception as e:
			print(traceback.format_exc())
			ssh_inst.close()
			GuiTig.change_color_tig(tig_en)
			WinMsg.error('密码错误')
			return False
		else:
			return True

	@classmethod
	def user_login(cls, ssh_inst, login_inst):
		return cls._login(ssh_inst, login_inst)

	@classmethod
	def root_login(cls, ssh_inst, login_inst):
		return cls._login(ssh_inst, login_inst, root=True)

	@classmethod
	def upload_file(cls, ssh_inst, local, remote):
		path = os.path.split(remote)[0]
		ssh_inst.exec_continue('mkdir -p %s;chmod 777 %s' % (path, path), root=True)
		return ssh_inst.upload(local, remote)

	@classmethod
	def exec_info(cls, ssh_inst, cmd, root=False):
		try:
			out = ssh_inst.exec_continue(cmd, root)[1]
			out = out.read().strip()
			out = str(out, encoding='utf-8')
			return out
		except:
			return None

	@classmethod
	def exec_ret(cls, ssh_inst, cmd, root=False):
		try:
			out = ssh_inst.exec_continue(cmd, root)[1]
			out = out.channel.recv_exit_status()
			return out
		except:
			return -1

	@classmethod
	def template_shell_and_download(cls, ssh_inst, progress, shell_path,\
	local_dir, root=False):
		''' 
		执行脚本，获取脚本打印，
		然后下载其打印内容到本地目录 
		'''
		try:
			out = ssh_inst.exec_continue(shell_path, root)[1]
			out = out.read().strip()
			out = str(out, encoding='utf-8')
			if not out:
				return False
			#print('out=',out)
			local_path = '\\'.join([local_dir, os.path.split(out)[1]])
			progress.update(0.8)
			if ssh_inst.download(out, local_path):
				progress.update(1)
				return True
			else:
				raise SSHError('download')
		except:
			#print(traceback.format_exc())
			return False


if __name__ == '__main__':
	ssh = SSH('10.160.154.120', 'eCommon', 'eLTE@com123', 'eLTE@com')
	b = ssh.exec_cmd("whoami", root=True)[1]
	print(b.channel.recv_exit_status(), b.read().strip())

============= my_main.py
#-*- coding: UTF-8 -*-

from PIL import Image, ImageTk
from my_common import Globals,Cache
from my_view import GuiLogin,GuiMain


def LoginInit():
	login = GuiLogin()
	# 初始化屏幕大小
	#Cache.windows_size(size=list(login.maxsize()))

	imgdir = '\\'.join([Globals.get_basedir(), 'image'])
	imgpath = '\\'.join([imgdir, 'item.ico'])
	img = ImageTk.PhotoImage(image=Image.open(imgpath))
	Cache.image_instance(ICO=img)
	imgpath = '\\'.join([imgdir, 'eye.png'])
	img = ImageTk.PhotoImage(image=Image.open(imgpath))
	Cache.image_instance(EYE=img)
	imgpath = '\\'.join([imgdir, 'add.png'])
	img = ImageTk.PhotoImage(image=Image.open(imgpath))
	Cache.image_instance(ADD=img)
	imgpath = '\\'.join([imgdir, 'set.png'])
	img = ImageTk.PhotoImage(image=Image.open(imgpath))
	Cache.image_instance(SET=img)
	imgpath = '\\'.join([imgdir, 'head.jpg'])
	img = ImageTk.PhotoImage(image=Image.open(imgpath))
	Cache.image_instance(HEAD=img)

	login.init_frame()
	login.pack_frame()

	login.protocol("WM_DELETE_WINDOW", login.close_window)
	login.mainloop()


def MainInit():
	main = GuiMain()
	main.init_frame()
	main.pack_frame()
	main.protocol("WM_DELETE_WINDOW", main.close_window)
	main.mainloop()

=============== my_logger.py
# -*- coding: UTF-8 -*-
__author__ = 'libin'

import os
#import pwd
import time


class Logger(object):
	"""
	即开即写，亲测比logging性能高，
	且日志回滚裁剪不影响日志写入
	usage:  log = Logger('aaa.log')
			log.info('info.....')
	"""
	def __init__(self, filepath):
		self.log_level = 'info'
		self.log_file = filepath
		with open(filepath, 'w') as f:
			f.write('log file init\n')

	@classmethod
	def _get_time(cls):
		ct = time.time()
		msec = (ct - int(ct)) * 1000
		return '%s.%03d' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msec)

	def _write_append(self, infos):
		try:
			with open(self.log_file, 'a+') as f:
				f.write(infos + '\n')
				return True
		except:
			return False

	def modify_level(self,level='info'):
		if not level:
			self.log_level = 'info'
		elif level in ['debug','info','error']:
			self.log_level = level

	def info(self, info):
		if self.log_level == 'error': return
		self._write_append('[INFO ] %s (%s): %s' % (self._get_time(), os.getpid(), info))

	def warn(self, info):
		self._write_append('[WARN ] %s (%s): %s' % (self._get_time(), os.getpid(), info))

	def error(self, info):
		self._write_append('[ERROR] %s (%s): %s' % (self._get_time(), os.getpid(), info))

	def debug(self, info):
		if self.log_level != 'debug': return
		self._write_append('[DEBUG] %s (%s): %s' % (self._get_time(), os.getpid(), info))








