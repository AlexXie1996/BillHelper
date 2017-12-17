from loginFrame import LoginFrame
from mainFrame import MainFrame

class UIManager():
	"""
	"""
	def __init__(self, callback_function):
		"""
		"""
		self.callback_function = callback_function
		
		self.login_frame_id = 1
		self.main_frame_id = 2
		
	def loadFrame(self, frame_id, pos, cache):
		"""
		"""
		if frame_id == self.login_frame_id:
			return LoginFrame(None, frame_id, pos, self.main_frame_id, self.callback_function, cache)
		elif frame_id == self.main_frame_id:
			return MainFrame(None, frame_id, pos, self.login_frame_id, self.callback_function, cache)