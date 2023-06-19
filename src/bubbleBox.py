from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os

class BubbleBox(QWidget):
	showParchment = pyqtSignal()

	def __init__(self, parent=None, **kwargs):
		super(BubbleBox, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.BUBBLE_OFFSET = [20, -60]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素
		self.IMG_WIDTH = 80*4

		self.textPix = {}
		self.loadPos()

		# 从信号槽读取
		self.emojiPic = None
		self.posX = 0	# 主窗口坐标
		self.posY = 0	# 主窗口坐标
		self.running_action = ''
		self.actualAction = 0
		self.mirrored = False
		self.picNum = 0

	def paintEvent(self, event):	# 绘制窗口
		self.moveToPos()
		
		paint = QPainter(self)
		self.resize(self.emojiPic.size())	# 获取图片大小
		self.setMask(self.emojiPic.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.emojiPic.width(), self.emojiPic.height(), self.emojiPic)

	def moveToPos(self):
		x = 0
		y = 0

		if self.running_action == '':
			if self.actualAction == 0:
				x = self.textPix[''][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix[''][0][1] + self.BUBBLE_OFFSET[1]
			elif self.actualAction == -1:
				x = self.textPix['lieDown'][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix['lieDown'][0][1] + self.BUBBLE_OFFSET[1]
			elif self.actualAction == -2:
				x = self.textPix['getUp'][0][0] + self.BUBBLE_OFFSET[0]
				y = self.textPix['getUp'][0][1] + self.BUBBLE_OFFSET[1]
		else:
			x = self.textPix[self.running_action][self.picNum][0] + self.BUBBLE_OFFSET[0]
			y = self.textPix[self.running_action][self.picNum][1] + self.BUBBLE_OFFSET[1]
		if self.mirrored:
			x = self.IMG_WIDTH - (x + self.emojiPic.width())
		x += self.posX
		y += self.posY
		#print(x, y, self.posX, self.posY)

		self.move(int(x), int(y))	# 调用move移动到指定位置

	def loadPos(self):	# 载入相对位移数据
		self.textPix.update({'' : [self.loadText(os.path.join('./img/stand', str(0) + '.txt'))]})

		temp = []
		for i in range(0, 16):
			temp.append(self.loadText(os.path.join('./img/trot', str(i) + '.txt')))
		self.textPix.update({'trot' : temp})

		temp = []
		for i in range(0, 9):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'sitDown' : temp})

		temp = []
		for i in range(9, 16):
			temp.append(self.loadText(os.path.join('./img/sit', str(i) +'.txt')))
		self.textPix.update({'standUp' : temp})

		temp = []
		for i in range(0, 7):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'lieDown' : temp})

		temp = []
		for i in range(7, 13):
			temp.append(self.loadText(os.path.join('./img/lie', str(i) +'.txt')))
		self.textPix.update({'getUp' : temp})

#		temp = []
#		for i in range(0, 10):
#			temp.append(self.loadText(os.path.join('./img/fly', str(i) +'.txt')))
#		self.textPix.update({'fly' : temp})

		temp = []
		for i in range(0, 18):
			temp.append(self.loadText(os.path.join('./img/boop', str(i) +'.txt')))
		self.textPix.update({'standBoop' : temp})

	def loadText(self, path):
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(int(line))

		return temp

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 打开对话框
		if event.button() == Qt.LeftButton:
			self.showParchment.emit()
			event.accept()
	''''''

	'''信号处理'''
	def getData(self, emojiPic, posX, posY, running_action, actualAction, mirrored, picNum):
		self.emojiPic = emojiPic
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
		self.running_action = running_action
		self.actualAction = actualAction
		self.mirrored = mirrored
		self.picNum = picNum
	''''''