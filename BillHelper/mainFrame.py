import wx
import pymysql

class MainFrame(wx.Frame):
	"""
	"""
	def __init__(self, parent=None, id=-1, pos=(-1,-1), next_frame_id=None, callback_function=None, cache=None):
		"""
		"""
		wx.Frame.__init__(self, parent, id, title='BillHelper', size=(700,300), pos=pos, style=wx.CAPTION | wx.CLOSE_BOX)
		self.frame_id = id
		self.next_frame_id = next_frame_id
		self.callback_function = callback_function	

		isInitDB = cache.get('initDB',True)
		if isInitDB:
			self.initDatabase(cache)

		self.QueryPanel_id = 1
		self.MangaeBillPanel_id = 2
		self.AddListPanel_id = 3
		self.LogoutPanel_id = 4
		
		cur_panel = cache.get('panel',-1)
		if cur_panel == -1:
			cur_panel = self.QueryPanel_id
		
		
		self.nb = wx.Notebook(self)
		self.nb.AddPage(QueryPanel(self.nb, cache, self.frame_id, self.callback_function), " Start a query ", cur_panel == self.QueryPanel_id)
		self.nb.AddPage(MangaeBillPanel(self.nb, cache, self.frame_id, self.callback_function), "  Mangae bill  ", cur_panel == self.MangaeBillPanel_id)
		self.nb.AddPage(AddListPanel(self.nb, cache, self.frame_id, self.callback_function), " Add new list ", cur_panel == self.AddListPanel_id)
		self.nb.AddPage(LogoutPanel(self.nb, cache, self.next_frame_id, self.callback_function), "    Log out    ", cur_panel == self.LogoutPanel_id)

	def initDatabase(self, cache):
		"""
		"""
		connection = pymysql.connect(host=cache['host'], port=cache['port'],
									user=cache['user'], password=cache['password'],
									charset=cache['charset'], cursorclass=cache['cursorclass'])
		cursor = connection.cursor()							
		cursor.execute("CREATE DATABASE IF NOT EXISTS " + cache['db'])
		cursor.execute("USE " + cache['db'])
		cursor.execute("CREATE TABLE IF NOT EXISTS details (\
								id int unique not null,\
								year int not null check(year >= 0),\
								month int not null check(month >= 1 and month <=12),\
								day int not null check(day >= 1 and day <= 31),\
								food float check(food >= 0),\
								clothes float check(clothes >= 0),\
								entertainment float check(entertainment>= 0),\
								others float check(others >= 0),\
								primary key (id)\
								)")
		cursor.execute("CREATE TABLE IF NOT EXISTS days (\
								id int unique not null,\
								year int not null check(year >= 0),\
								month int not null check(month >= 1 and month <=12),\
								day int not null check(day >= 1 and day <= 31),\
								total float,\
								primary key (id)\
								)")
		cursor.execute("CREATE TABLE IF NOT EXISTS months (\
								id int unique not null,\
								year int not null check(year >= 0),\
								month int not null check(month >= 1 and month <=12),\
								total float,\
								primary key (id)\
								)")
		cursor.execute("CREATE TABLE IF NOT EXISTS years (\
								year int primary key unique not null check(year >= 0), \
								total float\
								)")
		cursor.execute("DROP TRIGGER IF EXISTS tri_detailsDelete")
		cursor.execute("create trigger tri_detailsDelete\
						before delete on details\
						for each row\
						begin\
							declare c int;\
							set c = old.food + old.clothes + old.entertainment + old.others;\
							update days set total=total-c where year=old.year and month=old.month and day=old.day;\
							update months set total=total-c where year=old.year and month=old.month;\
							update years set total=total-c where year=old.year;\
						end")								
		cursor.execute("DROP TRIGGER IF EXISTS tri_detailsInsert")
		cursor.execute("create trigger tri_detailsInsert\
						after insert on details\
						for each row\
						begin\
							declare c int;\
							set c = new.food + new.clothes + new.entertainment + new.others;\
							update days set total=total+c where year=new.year and month=new.month and day=new.day;\
							update months set total=total+c where year=new.year and month=new.month;\
							update years set total=total+c where year=new.year;\
						end")
		cursor.close()
		connection.commit()
		connection.close()
		
class BasePanel(wx.Panel):
	"""
	"""
	def __init__(self, parent, cache, id, callback_function):
		"""
		"""
		wx.Panel.__init__(self, parent)
	
		self.id = id
		self.cache = cache
		self.callback_function = callback_function
		
		self.QueryPanel_id = 1
		self.MangaeBillPanel_id = 2
		self.AddListPanel_id = 3
		self.LogoutPanel_id = 4
		
		self.host = cache.get('host', '127.0.0.1')
		self.port = cache.get('port', 3306)
		self.user = cache.get('user', '')
		self.password = cache.get('password', '')
		self.db = cache.get('db', 'bill')
		self.charset = cache.get('charset', 'utf8mb4')
		self.cursorclass = cache.get('cursorclass', pymysql.cursors.DictCursor)
		
		self.connection = None
		self.cursor = None
		
		self.yearlist = [' - ']
		self.monthlist = [' - ']		
		
	def get_connection(self):
		"""
		"""
		self.connection = pymysql.connect(host=self.host,port=self.port,
											user=self.user,password=self.password,
											db=self.db,charset=self.charset,
											cursorclass=self.cursorclass)
		self.cursor = self.connection.cursor()
		
	def get_base_info(self):
		"""
		"""
		self.cursor.execute("select year from years")      			  
		results = [str(i['year']) for i in self.cursor.fetchall()]
		self.yearlist += results

	def callbcak(self, id, cur_panel):
		"""
		"""
		config = {}
		config['host'] = self.host
		config['port'] = self.port
		config['user'] = self.user
		config['password'] = self.password
		config['db'] = self.db
		config['charset'] = self.charset
		config['cursorclass'] = self.cursorclass
		config['panel'] = cur_panel
		config['initDB'] = False

		self.callback_function(id, config)
		
	def __del__(self):
		"""
		"""
		if self.cursor is not None:
			self.cursor.close()
		if self.connection is not None:
			self.connection.commit()
			self.connection.close()	
	
class QueryPanel(BasePanel):
	"""
	"""
	def __init__(self, parent, cache, id, callback_function):
		"""
		"""
		BasePanel.__init__(self, parent, cache, id, callback_function)
		
		self.get_connection()
		self.get_base_info()

		# Start a query
		self.lbStart = wx.StaticText(self, label="Hi {0}, start a query:".format(self.user), pos=(20, 10))

		# year comboBox
		self.lblselyear = wx.StaticText(self, label="Select the year to query:", pos=(30, 45))    
		self.boxselyear = wx.ComboBox(self, pos=(190, 40), size=(95, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxselyear.SetSelection(0)
		self.year = self.yearlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtYearComboBox, self.boxselyear)  

		# month comboBox   
		self.lblselmonth = wx.StaticText(self, label="Select the month to query:", pos=(30, 85))    
		self.boxselmonth = wx.ComboBox(self, pos=(190, 80), size=(95, -1),choices=self.monthlist,style=wx.CB_DROPDOWN)
		self.boxselmonth.SetSelection(0)
		self.month = self.monthlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtMonthComboBox, self.boxselmonth) 
		
		# save button
		self.save_button = wx.Button(self, label="Save", pos=(15, 125))  
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonSave, self.save_button)  		

		# refresh button
		self.refresh_button = wx.Button(self, label="Refresh", pos=(110, 125))  
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonRefresh, self.refresh_button) 
		
		# execute button
		self.execute_button = wx.Button(self, label="Execute", pos=(205, 125))  
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonExecute, self.execute_button)

		# result
		self.lbresult = wx.StaticText(self, label="Result :", pos=(340, 10))
		self.result = wx.TextCtrl(self, pos=(310, 30), size=(350, 175), style=wx.TE_MULTILINE | wx.TE_READONLY)

	def EvtYearComboBox(self, event):
		"""
		"""
		self.year = event.GetString()
		if self.year == self.yearlist:
			return
		
		try:
			self.cursor.execute("select month from months where year=%s", (self.year))      			  
			results = [str(i['month']) for i in self.cursor.fetchall()]
			self.boxselmonth.SetItems(self.monthlist + results)
		except:
			pass
	
	def EvtMonthComboBox(self, event):
		"""
		"""
		self.month = event.GetString()
		
	def OnclickButtonSave(self, event):
		"""
		"""
		if self.year == self.yearlist[0]:
			return
		if self.month == self.monthlist[0]:
			return
			
		with open('bill_'+self.year+self.month, 'w') as f:
			self.cursor.execute("select total from years where year=%s", (self.year))      			  
			yearTotal = [str(i['total']) for i in self.cursor.fetchall()]
			f.write("{0}\t{1}\n".format(self.year, yearTotal[0])) 
			
			self.cursor.execute("select total from months where year=%s and month=%s", (self.year, self.month))      			  
			monthTotal = [str(i['total']) for i in self.cursor.fetchall()]
			f.write("{0}\t{1}\n\n".format(self.month, monthTotal[0]))
			
			self.cursor.execute("select * from details where year=%s and month=%s", (self.year, self.month))
			for i in self.cursor.fetchall():
				f.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(i['day'], i['food'], i['clothes'], i['entertainment'], i['others']))

		self.callbcak(self.id, self.QueryPanel_id)
		
	def OnclickButtonRefresh(self, event):
		"""
		"""
		self.callbcak(self.id, self.QueryPanel_id)
		
	def OnclickButtonExecute(self, event):
		"""
		"""
		if self.year == self.yearlist[0]:
			return
		if self.month == self.monthlist[0]:
			return

		self.result.Clear()
		
		self.cursor.execute("select total from years where year=%s", (self.year))      			  
		yearTotal = [str(i['total']) for i in self.cursor.fetchall()]
		self.result.AppendText("Year\t: {0}\tcurTotal\t: {1:.6}\n".format(self.year, yearTotal[0])) 
		
		self.cursor.execute("select total from months where year=%s and month=%s", (self.year, self.month))      			  
		monthTotal = [str(i['total']) for i in self.cursor.fetchall()]
		self.result.AppendText("Month\t: {0}\tcurTotal\t: {1:.6}\n\n".format(self.month, monthTotal[0]))

		self.result.AppendText("===================================\n")
		self.result.AppendText("date\tfood\tclothes\tentertainment\tothers\n".format(self.month, monthTotal[0]))
		self.result.AppendText("===================================\n")
		
		self.cursor.execute("select * from details where year=%s and month=%s", (self.year, self.month))
		for i in self.cursor.fetchall():
			self.result.AppendText("{0}\t{1:.4}\t{2:.4}\t      {3:.4}\t\t{4:.4}\n".format(i['day'], i['food'], i['clothes'], i['entertainment'], i['others']))
		self.result.AppendText("===================================\n")
		
class MangaeBillPanel(BasePanel):
	"""
	"""
	def __init__(self, parent, cache, id, callback_function):
		"""
		"""
		BasePanel.__init__(self, parent, cache, id, callback_function)
			
		self.get_connection()
		self.get_base_info()	
		
		# add new year
		self.lbAddYearText = wx.StaticText(self, -1, 'Add new year here, interger only:', pos=(30,10))

		self.AddYear = wx.TextCtrl(self, -1, u'', pos=(60,40))
		self.Bind(wx.EVT_TEXT, self.EvtAddYear, self.AddYear)
	
		self.btAddYear = wx.Button(self, -1, u'Add', pos=(180, 37))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonAddYear, self.btAddYear)
		
		self.lbAddYearWrong = wx.StaticText(self, -1, '', pos=(30,70))
		
		# del a year
		self.lbAddYearText = wx.StaticText(self, -1, 'Delete a year here:', pos=(340,10))
		
		self.boxAddYear = wx.ComboBox(self, pos=(370, 40), size=(110, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxAddYear.SetSelection(0)
		self.delyear = self.yearlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtDelYear, self.boxAddYear)
		
		self.btDelYear = wx.Button(self, -1, u'Del', pos=(490, 37))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonDelYear, self.btDelYear)
		
		self.lbDelYearWrong = wx.StaticText(self, -1, '', pos=(340,70))
		
		# add new month
		self.lbAddMonthText = wx.StaticText(self, -1, 'Add new month here, select a year first:', pos=(30,100))

		self.boxAddMSelY = wx.ComboBox(self, pos=(60, 130), size=(110, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxAddMSelY.SetSelection(0)
		self.addmsely = self.yearlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtAddMSelY, self.boxAddMSelY)
		
		self.boxAddMonth = wx.ComboBox(self, pos=(60, 165), size=(110, -1),choices=self.monthlist,style=wx.CB_DROPDOWN)
		self.boxAddMonth.SetSelection(0)
		self.addmonth = self.monthlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtAddMonth, self.boxAddMonth)
	
		self.btRefresh1 = wx.Button(self, -1, u'Refresh', pos=(180, 127))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonRefresh, self.btRefresh1)
		
		self.btAddMonth = wx.Button(self, -1, u'Add', pos=(180, 163))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonAddMonth, self.btAddMonth)
		
		self.lbAddMonthWrong = wx.StaticText(self, -1, '', pos=(30,193))
		
		# del a month
		self.lbDelMonthText = wx.StaticText(self, -1, 'Delete a month here, select a year first:', pos=(340,100))

		self.boxDelMSelY = wx.ComboBox(self, pos=(370, 130), size=(110, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxDelMSelY.SetSelection(0)
		self.delmsely = self.yearlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtDelMSelY, self.boxDelMSelY)
		
		self.boxDelMonth = wx.ComboBox(self, pos=(370, 165), size=(110, -1),choices=self.monthlist,style=wx.CB_DROPDOWN)
		self.boxDelMonth.SetSelection(0)
		self.delmonth = self.monthlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtDelMonth, self.boxDelMonth)
	
		self.btRefresh2 = wx.Button(self, -1, u'Refresh', pos=(490, 127))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonRefresh, self.btRefresh2)
		
		self.btDelMonth = wx.Button(self, -1, u'Del', pos=(490, 163))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonDelMonth, self.btDelMonth)
		
		self.lbDelMonthWrong = wx.StaticText(self, -1, '', pos=(340,193))
		
	def EvtAddYear(self, event):
		"""
		"""
		self.addyear = event.GetString()
		
	def OnclickButtonAddYear(self, event):
		"""
		"""
		try:
			int(self.addyear)
		except:
			self.lbAddYearWrong.SetLabel('Ohhhs...! not a number .')
			return
		
		self.addyear = int(self.addyear)
		if self.addyear < 0:
			self.lbAddYearWrong.SetLabel('Ohhhs...! is a negative .')
			return
		
		try:		
			self.cursor.execute("insert into years values(%s, %s)", (self.addyear, '0'))
		except:
			self.lbAddYearWrong.SetLabel('Ohhhs...! Something wrong with database .')
			return

		self.callbcak(self.id, self.MangaeBillPanel_id)
		
	def EvtDelYear(self, event):
		"""
		"""
		self.delyear = event.GetString()
		
	def OnclickButtonDelYear(self, event):
		"""
		"""
		if self.delyear == self.yearlist[0]:
			self.lbDelYearWrong.SetLabel('Ohhhs...! select a year first .')
			return
			
		try:		
			self.cursor.execute("delete from years where year=%s", (self.delyear))
			self.cursor.execute("delete from months where year=%s", (self.delyear))
			self.cursor.execute("delete from days where year=%s", (self.delyear))
			self.cursor.execute("delete from details where year=%s", (self.delyear))
		except:
			self.lbDelYearWrong.SetLabel('Ohhhs...! Something wrong with database .')
			return

		self.callbcak(self.id, self.MangaeBillPanel_id)
		
	def EvtAddMSelY(self, event):
		"""
		"""
		self.addmsely = event.GetString()
		if self.addmsely == self.yearlist[0]:
			return
		
		try:
			self.cursor.execute("select month from months where year=%s",(self.addmsely))      			  
			results = [str(i['month']) for i in self.cursor.fetchall()]
			results = [i for i in ['1','2','3','4','5','6','7','8','9','10','11','12'] if i not in results]
		except:
			self.lbAddMonthWrong.SetLabel('Ohhhs...! Something wrong with database .')
			return
			
		self.boxAddMonth.SetItems(results)
		
	def EvtAddMonth(self, event):
		"""
		"""
		self.addmonth = event.GetString()
	
	def OnclickButtonRefresh(self, event):
		"""
		"""
		self.callbcak(self.id, self.MangaeBillPanel_id)
		
	def OnclickButtonAddMonth(self, event):
		"""
		"""
		if self.addmsely == self.yearlist[0]:
			self.lbAddMonthWrong.SetLabel('Ohhhs...! select a year first .')
			return

		if self.addmonth == self.monthlist[0]:
			self.lbAddMonthWrong.SetLabel('Ohhhs...! select a month first .')
			return
		
		try:		
			self.cursor.execute("insert into months values(%s, %s, %s, %s)", (self.addmsely+self.addmonth, self.addmsely, self.addmonth, '0'))
		except:
			self.lbAddMonthWrong.SetLabel('Ohhhs...! Something wrong with database .')
			return

		self.callbcak(self.id, self.MangaeBillPanel_id)
		
	def EvtDelMSelY(self, event):
		"""
		"""
		self.delmsely = event.GetString()
		if self.delmsely == self.yearlist[0]:
			return  
		try:
			self.cursor.execute("select month from months where year=%s", (self.delmsely))      			  
			results = [str(i['month']) for i in self.cursor.fetchall()]
			self.boxDelMonth.SetItems(self.monthlist + results)
		except:
			self.lbDelMonthWrong.SetLabel('Ohhhs...! Something wrong with database .')
			
	def EvtDelMonth(self, event):
		"""
		"""
		self.delmonth = event.GetString()
		
	def OnclickButtonDelMonth(self, event):
		"""
		"""
		if self.delmsely == self.yearlist[0]:
			self.lbDelMonthWrong.SetLabel('Ohhhs...! select a year first .')
			return

		if self.delmonth == self.monthlist[0]:
			self.lbDelMonthWrong.SetLabel('Ohhhs...! select a month first .')
			return
			
		try:
			self.cursor.execute("delete from months where year=%s and month=%s", (self.delmsely, self.delmonth))
			self.cursor.execute("delete from days where year=%s and month=%s", (self.delmsely, self.delmonth))
			self.cursor.execute("delete from details where year=%s and month=%s", (self.delmsely, self.delmonth))
		except:
			self.lbDelMonthWrong.SetLabel('Ohhhs...! Something wrong with database .')

		self.callbcak(self.id, self.MangaeBillPanel_id)
		
class AddListPanel(BasePanel):
	"""
	"""
	def __init__(self, parent, cache, id, callback_function):
		"""
		"""
		BasePanel.__init__(self, parent, cache, id, callback_function)
		
		self.get_connection()
		self.get_base_info()			

		self.food = 0.0
		self.clothes = 0.0
		self.entertainment = 0.0
		self.others = 0.0
		self.total = 0.0
		
		self.lbHint1 = wx.StaticText(self, -1, "Add today's list here:", pos=(30,10))
		self.lbHint2 = wx.StaticText(self, -1, 'Hint  : you can only add to a month which is exist .', pos=(30,30))
		self.lbHint3 = wx.StaticText(self, -1, '         select a year and a month, then fill blanks below(default to 0) .', pos=(30,50))
		self.lbHint4 = wx.StaticText(self, -1, '         you can see the total amount spent today on the right .', pos=(30,70))
		
		# select a year
		self.lbSelYear = wx.StaticText(self, -1, 'year:', pos=(30,110))
		
		self.boxSelYear = wx.ComboBox(self, pos=(70, 107), size=(70, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxSelYear.SetSelection(0)
		self.year = self.yearlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtSelYear, self.boxSelYear)
		
		# select a month
		self.lbSelMonth = wx.StaticText(self, -1, 'month:', pos=(150,110))
		
		self.boxSelMonth = wx.ComboBox(self, pos=(200, 107), size=(70, -1),choices=self.yearlist,style=wx.CB_DROPDOWN)
		self.boxSelMonth.SetSelection(0)
		self.month = self.monthlist[0]
		self.Bind(wx.EVT_COMBOBOX, self.EvtSelMonth, self.boxSelMonth)
		
		# date
		self.lbDate = wx.StaticText(self, -1, 'Date:', pos=(280,110))
		
		self.Date = wx.TextCtrl(self, -1, u'', pos=(320,107), size=(90, -1))
		self.Bind(wx.EVT_TEXT, self.EvtDate, self.Date)
		
		# food
		self.lbFood = wx.StaticText(self, -1, 'Food:', pos=(30,150))
		
		self.Food = wx.TextCtrl(self, -1, u'', pos=(70,147))
		self.Bind(wx.EVT_TEXT, self.EvtFood, self.Food)
		
		# clothes
		self.lbClothes = wx.StaticText(self, -1, 'Clothes:', pos=(190,150))
		
		self.Clothes = wx.TextCtrl(self, -1, u'', pos=(240,147))
		self.Bind(wx.EVT_TEXT, self.EvtClothes, self.Clothes)
				
		# entertainment
		self.lbEntertainment = wx.StaticText(self, -1, 'Entertainment:', pos=(30,190))
		
		self.Entertainment = wx.TextCtrl(self, -1, u'', pos=(120,187))
		self.Bind(wx.EVT_TEXT, self.EvtEntertainment, self.Entertainment)
				
		# others
		self.lbOthers = wx.StaticText(self, -1, 'Others:', pos=(240,190))
		
		self.Others = wx.TextCtrl(self, -1, u'', pos=(290,187))
		self.Bind(wx.EVT_TEXT, self.EvtOthers, self.Others)
				
		# total
		self.lbTotal = wx.StaticText(self, -1, 'Total  : 0.00', pos=(440,120))
		
		
		# add
		self.lbHint5 = wx.StaticText(self, -1, 'Make sure all the data is correct .', pos=(440,140))
		
		self.btAdd = wx.Button(self, -1, u'Add', pos=(455, 165))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonAdd, self.btAdd)
		
		self.btRefresh = wx.Button(self, -1, u'Refresh', pos=(550, 165))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonRefresh, self.btRefresh)
		
		self.lbWrong = wx.StaticText(self, -1, u'', pos=(440,200))
		
	def EvtSelYear(self, event):
		"""
		"""
		self.year = event.GetString()
		if self.year == self.yearlist:
			return
		
		try:
			self.cursor.execute("select month from months where year=%s", (self.year))      			  
			results = [str(i['month']) for i in self.cursor.fetchall()]
			self.boxSelMonth.SetItems(self.monthlist + results)
		except:
			pass

	def EvtSelMonth(self, event):
		"""
		"""
		self.month = event.GetString()
		if self.month == self.monthlist[0]:
			return
		
		self.Date.Clear()
		self.lbWrong.SetLabel('')
		
	def EvtDate(self, event):
		"""
		"""
		self.date = event.GetString()
		if self.date == '':
			return
		
		try:
			self.date = int(self.date)
		except:
			self.lbWrong.SetLabel('Ohhhs...! Date is not number .')
			return
		
		if self.month == self.monthlist[0]:
			self.lbWrong.SetLabel('Ohhhs...! Select a month first .')
			return
		elif self.month == '1' or self.month == '3' or self.month == '5' or self.month == '7' or self.month == '8' or self.month == '10' or self.month == '12':
			if self.date <= 0 or self.date >= 32:
				self.lbWrong.SetLabel('Ohhhs...! Date is out of range .')
				return				
		elif self.month == '4' or self.month == '6' or self.month == '9' or self.month == '11':
			if self.date <= 0 or self.date >= 31:
				self.lbWrong.SetLabel('Ohhhs...! Date is out of range .')
				return
		elif self.month == '2':
			if self.date <= 0 or self.date >= 30:
				self.lbWrong.SetLabel('Ohhhs...! Date is out of range .')
				return
		
		self.lbWrong.SetLabel('')
		
	def EvtFood(self, event):
		"""
		"""		
		food = event.GetString()
	
		if food == '':
			self.lbWrong.SetLabel('')
			self.lbTotal.SetLabel('Total  : 0.0.'.format(self.total))
			return
		try:
			food = float(food)
		except:
			self.lbWrong.SetLabel('Ohhhs...! Food is not number .')
			return
		if food < 0:
			self.lbWrong.SetLabel('Ohhhs...! Food is out of range .')
			return
			
		self.lbWrong.SetLabel('')
		self.total = self.total - self.food + food
		self.lbTotal.SetLabel('Total  : {0:.6}.'.format(self.total))
		self.food = food
		
	def EvtClothes(self, event):
		"""
		"""
		clothes = event.GetString()
	
		if clothes == '':
			self.lbWrong.SetLabel('')
			self.lbTotal.SetLabel('Total  : 0.0.'.format(self.total))
			return
		try:
			clothes = float(clothes)
		except:
			self.lbWrong.SetLabel('Ohhhs...! Clothes is not number .')
			return
		if clothes < 0:
			self.lbWrong.SetLabel('Ohhhs...! Clothes is out of range .')
			return
			
		self.lbWrong.SetLabel('')
		self.total = self.total - self.clothes + clothes
		self.lbTotal.SetLabel('Total  : {0:.6}.'.format(self.total))
		self.clothes = clothes
		
	def EvtEntertainment(self, event):
		"""
		"""
		entertainment = event.GetString()
		
		if entertainment == '':
			self.lbWrong.SetLabel('')
			self.lbTotal.SetLabel('Total  : 0.0.'.format(self.total))
			return
		try:
			entertainment = float(entertainment)
		except:
			self.lbWrong.SetLabel('Ohhhs...! Entertainment is not number .')
			return
		if entertainment < 0:
			self.lbWrong.SetLabel('Ohhhs...! Entertainment is out of range .')
			return
			
		self.lbWrong.SetLabel('')
		self.total = self.total - self.entertainment + entertainment
		self.lbTotal.SetLabel('Total  : {0:.6}.'.format(self.total))
		self.entertainment = entertainment
		
	def EvtOthers(self, event):
		"""
		"""
		others = event.GetString()
	
		if others == '':
			self.lbWrong.SetLabel('')
			self.lbTotal.SetLabel('Total  : 0.0.'.format(self.total))
			return
		try:
			others = float(others)
		except:
			self.lbWrong.SetLabel('Ohhhs...! Others is not number .')
			return
		if others < 0:
			self.lbWrong.SetLabel('Ohhhs...! Others is out of range .')
			return
			
		self.lbWrong.SetLabel('')
		self.total = self.total - self.others + others
		self.lbTotal.SetLabel('Total  : {0:.6}.'.format(self.total))
		self.others = others
		
	def OnclickButtonAdd(self, event):
		"""
		"""
		if self.year == self.yearlist[0]:
			self.lbWrong.SetLabel('Ohhhs...! select a year first .')
			return
		if self.month == self.monthlist[0]:
			self.lbWrong.SetLabel('Ohhhs...! select a month first .')
			return
		
		try:
			self.cursor.execute("insert into days values(%s, %s, %s, %s, %s)", (self.year+self.month+str(self.date), str(self.year), str(self.month), str(self.date), '0'))
			self.cursor.execute("insert into details values(%s, %s, %s, %s, %s, %s, %s, %s)", (self.year+self.month+str(self.date), str(self.year), str(self.month), str(self.date), str(self.food), str(self.clothes), str(self.entertainment), str(self.others)))
		except:
			self.lbWrong.SetLabel('Ohhhs...! Something wrong with database .')
			return
		self.callbcak(self.id, self.AddListPanel_id)
		
	def OnclickButtonRefresh(self, event):
		"""
		"""
		self.callbcak(self.id, self.AddListPanel_id)
		
class LogoutPanel(wx.Panel):
	"""
	"""
	def __init__(self, parent, cache, next_frame_id, callback_function):
		"""
		"""
		wx.Panel.__init__(self, parent)
		
		self.next_frame_id = next_frame_id
		self.callback_function = callback_function
			
		self.lbSure = wx.StaticText(self, -1, 'Make sure you want to log out (ID : {0}) .'.format(cache['user']), pos=(210,70))
		
		# logout
		self.btLogout = wx.Button(self, -1, u'Log out', pos=(280, 100))
		self.Bind(wx.EVT_BUTTON, self.OnclickButtonLogout, self.btLogout)
		
	def OnclickButtonLogout(self, event):
		"""
		"""
		self.callback_function(self.next_frame_id, {})
		
