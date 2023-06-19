from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os

class TrayIcon(QSystemTrayIcon):
	trayQuit = pyqtSignal()

	def __init__(self, parent=None):
		super(TrayIcon, self).__init__(parent)

		self.setIcon(QIcon("./img/favIcon256.ico"))	# 设置图标
		self.icon = self.MessageIcon()
		self.showMenu()
		self.show()

	def showMenu(self):
		self.menu = QMenu()

		self.openMemoFolderAction = QAction("备忘录文件夹", self, triggered = self.openMemoFolder)
		self.quitAction = QAction("退出", self, triggered = self.quit)

		self.menu.addAction(self.openMemoFolderAction)
		self.menu.addAction(self.quitAction)

		self.setContextMenu(self.menu)

	'''其他函数'''
	def quit(self):
		self.trayQuit.emit()

	def openMemoFolder(self):	# 打开对应文件夹
		os.startfile(os.path.abspath('./'))