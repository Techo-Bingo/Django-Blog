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
		



