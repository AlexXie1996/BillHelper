import wx
import pymysql

class LoginFrame(wx.Frame):
	"""
	"""
	def __init__(self, parent=None, id=-1, pos=(-1,-1), next_frame_id=None, callback_function=None, cache=None):
		"""
		"""
		wx.Frame.__init__(self, parent, id, title='Login', size=(280,280), pos=pos, style=wx.CAPTION | wx.CLOSE_BOX)
		
		self.frame_id = id
		self.next_frame_id = next_frame_id
		self.callback_function = callback_function
		
		self.host = cache.get('host', '127.0.0.1')
		self.port = cache.get('port', 3306)
		self.db = cache.get('db', 'bill')
		self.charset = cache.get('charset', 'utf8mb4')
		self.cursorclass = cache.get('cursorclass', pymysql.cursors.DictCursor)
		self.account = ''
		self.password = ''
		self.connection = None
		
		panel = wx.Panel(self)
		
		self.lbStart = wx.StaticText(panel, -1, 'login to mysql :', pos=(30,20))
		
		self.lbAccount = wx.StaticText(panel, -1, 'Account', pos=(30, 60))
		self.Account = wx.TextCtrl(panel, -1, u'', pos=(110,60))
		self.Bind(wx.EVT_TEXT, self.EvtAccount, self.Account)
		
		self.lbPassword = wx.StaticText(panel, -1, 'Password', pos=(30,100))
		self.Password = wx.TextCtrl(panel, -1, u'', pos=(110, 100),style=wx.TE_PASSWORD)
		self.Bind(wx.EVT_TEXT, self.EvtPassword, self.Password)
		
		self.btExecute = wx.Button(panel, -1, u'Login', pos=(90, 150))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonExecute, self.btExecute)
		
		self.lbWrong = wx.StaticText(panel, -1, '', pos=(30,190))
	
		
	def EvtAccount(self, event):
		"""
		"""
		self.account = event.GetString()
		
	def EvtPassword(self, event):
		"""
		"""
		self.password = event.GetString()
		
	def OnclickButtonExecute(self, event):
		"""
		"""
		if self.account is None:
			self.lbWrong.SetLabel('Account is None')
		elif self.password is None:
			self.lbWrong.SetLabel('Password is None')
		elif self.db is None:
			self.lbWrong.SetLabel('DateBase is None')
		else:
			try:
				self.connection = pymysql.connect(host=self.host,port=self.port,
											user=self.account,password=self.password,
											charset=self.charset,cursorclass=self.cursorclass)
			except pymysql.err.OperationalError:
				self.lbWrong.SetLabel('Account or password is incorrect')
				return
			except:
				self.lbWrong.SetLabel('Something wrong')
				return
				
			config = {}
			config['host'] = self.host
			config['port'] = self.port
			config['user'] = self.account
			config['password'] = self.password
			config['db'] = self.db
			config['charset'] = self.charset
			config['cursorclass'] = self.cursorclass
			config['panel'] = -1
			config['initDB'] = True
			self.callback_function(self.next_frame_id, config)
	
	def __def__(self):
		"""
		"""
		if self.connection is not None:
			self.connection.close()
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		