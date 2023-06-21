from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os

import math

from src.followPonyPos import *

class menuBubble(QWidget, followPonyPos):
	# 定义信号
	functionActive = pyqtSignal()	# 触发按钮功能(连接到实现功能的函数)
	closeSubclass = pyqtSignal()	# 关闭同级菜单的子菜单

	def __init__(self, info, icon, function, parent=None, **kwargs):
		super(menuBubble, self).__init__(parent)

		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.info = info
		self.icon = icon
		self.function = function

	def paintEvent(self, event):	# 绘制窗口
		if self.info.showBubble:
			self.moveToPos()
		
			paint = QPainter(self)
			self.resize(self.icon.size())	# 获取图片大小
			self.setMask(self.icon.mask())   # 设置蒙版
			paint.drawPixmap(0, 0, self.icon.width(), self.icon.height(), self.icon)

	def moveToPos(self):
		x = 0
		y = 0

		if self.running_action == '':	# 对齐中心
			if self.actualAction == 0:
				x = (self.textPix[''][0][0] + self.textPix[''][0][2]) / 2
				y = (self.textPix[''][0][1] + self.textPix[''][0][3]) / 2
			elif self.actualAction == -1:
				x = (self.textPix['lieDown'][0][0] + self.textPix['lieDown'][0][2]) / 2
				y = (self.textPix['lieDown'][0][1] + self.textPix['lieDown'][0][3]) / 2
			elif self.actualAction == -2:
				x = (self.textPix['getUp'][0][0] + self.textPix['getUp'][0][2]) / 2
				y = (self.textPix['getUp'][0][1] + self.textPix['getUp'][0][3]) / 2
		else:
			x = (self.textPix[self.running_action][self.picNum][0] + self.textPix[self.running_action][self.picNum][2]) / 2
			y = (self.textPix[self.running_action][self.picNum][1] + self.textPix[self.running_action][self.picNum][3]) / 2
		x -= self.icon.width() / 2
		y -= self.icon.height() / 2
		x += self.posX
		y += self.posY

		x += self.info.r * math.cos(math.radians(-self.info.angle))	# 偏移量计算, 因为math的度数居然是顺时针旋转的, 所以加上负号变为逆时针旋转
		y += self.info.r * math.sin(math.radians(-self.info.angle))

		self.move(int(x), int(y))	# 调用move移动到指定位置

	'''事件处理'''
	def mousePressEvent(self, event):		# 鼠标左键按下时, 打开对话框
		if event.button() == Qt.LeftButton:
			if self.function == 'menuLayer':
				for i in self.info.son:
					self.info.son[i].info.showBubble = True
			elif self.function == 'functionButton':
				self.functionActive.emit()
		self.closeSubclass.emit()
	''''''

	'''信号处理'''
	def getData(self, posX, posY, running_action, actualAction, picNum):
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
		self.running_action = running_action
		self.actualAction = actualAction
		self.picNum = picNum

	def menuClose(self):	# 关闭子菜单
		self.update()
		for i in self.info.son:
			self.info.son[i].info.showBubble = False
			self.info.son[i].menuClose()
	''''''