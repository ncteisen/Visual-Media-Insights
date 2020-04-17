import logging

class LoggerConfig:
	def __init__(self):
		logging.basicConfig(format='%(asctime)s - %(filename)20s: %(message)s');
		self.root = logging.getLogger()
		self.root.setLevel(logging.INFO)