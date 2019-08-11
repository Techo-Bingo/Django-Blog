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
class Shells:
	pack_str = '''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'''




