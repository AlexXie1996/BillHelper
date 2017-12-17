import wx
import pymysql
from uiManager import UIManager 

class BillHelper(wx.App):
	"""
	"""
	def OnInit(self):
		"""
		"""
		self.config = {
			'host':'127.0.0.1',
			'port':3306,
			'bd':'bill',
			'charset':'utf8mb4',
			'cursorclass':pymysql.cursors.DictCursor,
		}
		self.manager = UIManager(self.ReLoadUI)
		self.frame = self.manager.loadFrame(self.manager.login_frame_id, (-1,-1), self.config)
		self.frame.Show()
		
		return True

	def ReLoadUI(self, frame_id, cache):
		"""
		"""
		pos = self.frame.GetPosition()
		self.frame.Close(True)
		self.frame = self.manager.loadFrame(frame_id, pos, cache)
		self.frame.Show(True)
		self.frame.Refresh()

def main():
	"""
	"""
	app = BillHelper()
	app.MainLoop()

if __name__ == '__main__':
	main()
	
	
	
	
	
	
	
	
	