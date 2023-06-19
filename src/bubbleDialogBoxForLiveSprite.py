from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL import Image, ImageDraw, ImageFont, ImageQt

import os
import cfg

class BubbleDialogBox(QWidget):
	def __init__(self, s, parent=None, **kwargs):
		super(BubbleDialogBox, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.textPix = {}

		self.BUBBLE_OFFSET = [-80, -80]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素

		self.textBox = QPixmap('./img/parchment/DialogBubble.png')
		self.textRaw = s
		self.textSlice = []
		self.textPic = []
		self.textPages = []
		self.currentPage = 0
		self.size = self.textBox.size()	# 获取textBox的大小

		self.charPerLine = int((self.size.width() - cfg.INITIAL_OFFSET[1]) / (cfg.FONT_SIZE + cfg.HORIZONTAL_SPACING)) - 1
		self.linePerPage = int((self.size.height() - cfg.INITIAL_OFFSET[0]) / (cfg.FONT_SIZE + cfg.VERTICAL_SPACING))

		# 从信号槽读取
		self.posX = 0	# 主窗口坐标
		self.posY = 0	# 主窗口坐标

		self.oneRowSlicer()
		for line in self.textSlice:
			self.oneRowGenerater(line, cfg.FONT_SIZE)
		self.pageGenerater()

	def paintEvent(self, event):	# 绘制窗口
		self.moveToPos()

		paint = QPainter(self)
		self.textBox = self.textPages[self.currentPage]

		self.resize(self.textBox.size())	# 获取图片大小
		self.setMask(self.textBox.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.textBox.width(), self.textBox.height(), self.textBox)

	'''定位至头顶'''
	def moveToPos(self):
		x = self.BUBBLE_OFFSET[0]
		y = self.BUBBLE_OFFSET[1]

		x += self.posX
		y += self.posY
		#print(x, y, self.posX, self.posY)

		self.move(int(x), int(y))	# 调用move移动到指定位置

	def loadText(self, path):
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(int(line))

		return temp
	''''''

	'''文本图片生成器'''
	def oneRowGenerater(self, text, font_size = 24): # (内容, 大小)
		font = ImageFont.truetype('./img/parchment/font/方正像素12.ttf', font_size)   # 字体路径及文本大小
		text_width, text_height = font.getsize(text)	# 字体框大小
		image = Image.new(mode = 'RGBA', size = (text_width, text_height))  # 生成图像
		draw_table = ImageDraw.Draw(im = image)
		draw_table.text(xy = (0, 0), text = text, fill = cfg.FONT_COLOR, font = font)	# 生成文本为白色
 
		self.textPic.append(image)

	def oneRowSlicer(self):
		for s in self.textRaw:
			textLen = 0
			counter = 0
			needSlice = False
			for word in s:
				if '\u4e00' <= word <= '\u9fff':	# 中文字符占两位, 英文字符占一位
					textLen += 2
				else:
					textLen += 1
				counter += 1
				if textLen > self.charPerLine*2:
					needSlice = True
					break
			if needSlice:	# 递归剪切过长的片段
				self.textSlice.append(s[:counter])
				self.Slicer(s[counter:])
			else:
				self.textSlice.append(s)

	def Slicer(self, s):	# 递归函数
		textLen = 0
		counter = 0
		for word in s:
			if '\u4e00' <= word <= '\u9fff':	# 中文字符占两位, 英文字符占一位
				textLen += 2
			else:
				textLen += 1
			counter += 1
		if textLen > self.charPerLine*2:
			self.textSlice.append(s[:counter])
			self.Slicer(s[counter:])
		else:
			self.textSlice.append(s)

	def pageGenerater(self):
		if len(self.textPic) > self.linePerPage:
			temp = Image.open('./img/parchment/DialogBubble.png')
		else:
			temp = Image.open('./img/parchment/DialogBubble.png')

		target = Image.new(mode = 'RGBA', size = (temp.width, temp.height))
		for i in range(0, self.linePerPage):
			if i >= len(self.textPic):
				break
			target.paste(self.textPic[i], (cfg.INITIAL_OFFSET[0], cfg.INITIAL_OFFSET[1] + (cfg.FONT_SIZE + cfg.VERTICAL_SPACING)*i))	# 左上角坐标, 初始偏移量(y, x)
		temp = Image.alpha_composite(temp, target)	# 带Alpha通道的粘贴
		temp = ImageQt.toqpixmap(temp)	# QImage => QPixmap

		self.textPages.append(temp)

		if len(self.textPic) > self.linePerPage:
			self.textPic = self.textPic[self.linePerPage:]
			self.pageGenerater()
	''''''

	def quit(self):
		self.close()

	'''信号处理'''
	def getData(self, posX, posY):
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
	''''''