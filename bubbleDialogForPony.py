from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL import Image, ImageDraw, ImageFont, ImageQt

import os
import sys

import cfg

from src.bubbleDialogBox import *

class bubbleDialogForPony(QWidget):
	bubbleDialogUpdate = pyqtSignal(int, int, str, int, bool, int)

	def __init__(self, parent=None, **kwargs):
		super(bubbleDialogForPony, self).__init__(parent)

		self.posX = 0
		self.posY = 0
		self.running_action = ''
		self.actualAction = 0
		self.mirrored = False
		self.picNum = 0

		self.bubbleDialog = BubbleDialogBox('')
		self.bubbleDialogText = ''

		self.showBubbleDialog = False

		self.animationTimer = QTimer()
		self.animationTimer.start(int(1000/cfg.FPS)) # 动画更新速度同步屏幕帧率
		self.animationTimer.timeout.connect(self.update)
		self.animationTimer.timeout.connect(self.openBubbleDialogText)	# 读取弹幕文本信息
		self.animationTimer.timeout.connect(self.bubbleDialogUpdate_)

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		size = self.geometry()
		x = screen.width() - size.width()
		y = screen.height() - size.height()
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		paint = QPainter(self)
		self.resize(self.actionPic.size())	# 获取图片大小
		self.setMask(self.actionPic.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.actionPic.width(), self.actionPic.height(), self.actionPic)

	def readText(self, path):	# 读取txt文件, 返回一个str数组
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(line)

		f.close()
		return temp

	def openBubbleDialogText(self):	# 打开对应文件夹
		text = self.readText(os.path.join('./headBubble.txt'))
		if text != self.bubbleDialogText and text != []:
			self.bubbleDialogText = text
			self.bubbleDialog = BubbleDialogBox(text)
			self.showBubbleDialog = True
			self.bubbleDialogUpdate.connect(self.bubbleDialog.getData)	# 每次创建新对象都要重新连接信号槽
		
	def bubbleDialogUpdate_(self):
		self.updatePos()
		self.bubbleDialogUpdate.emit(self.posX, self.posY, self.running_action, self.actualAction, self.mirrored, self.picNum)
		self.bubbleDialog.update()
		if self.showBubbleDialog:	# 如果无新内容, 则不更新头顶气泡
			self.bubbleDialog.show()
			self.showBubbleDialog = False

	def updatePos(self):	# 从数据输入文件读取信息
		data = open('./ponyPos.txt', 'r').readlines()
		if data != []:
			self.posX = int(data[0])
			self.posY = int(data[1])
			self.running_action = str(data[2][:-1])	# 字符串有\n结尾
			self.actualAction = int(data[3])
			self.mirrored = True if str(data[4][:-1]) == 'True' else False	# str无法直接转bool, 要用判断式
			self.picNum = int(data[5])

'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = bubbleDialogForPony()
	sys.exit(app.exec_())