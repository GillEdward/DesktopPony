from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL import Image, ImageDraw, ImageFont, ImageQt

import cfg

class DialogBox(QWidget):
	def __init__(self, s, parent=None, **kwargs):
		super(DialogBox, self).__init__(parent)
		# 初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		self.textBox = QPixmap('./img/parchment/Dialog.png')	# 底片
		self.textRaw = s 	# 初始文本
		self.textSlice = []	# 剪切后的文本
		self.textPic = []	# 生成带有文本的图片
		self.textPages = []	# 图片页集
		self.currentPage = 0	# 当前页数
		self.size = self.textBox.size()	# 获取textBox的大小

		self.charPerLine = int((self.size.width() - cfg.INITIAL_OFFSET[1]) / (cfg.FONT_SIZE + cfg.HORIZONTAL_SPACING)) - 1
		self.linePerPage = int((self.size.height() - cfg.INITIAL_OFFSET[0]) / (cfg.FONT_SIZE + cfg.VERTICAL_SPACING))

		self.initPos()
		self.oneRowSlicer()
		for line in self.textSlice:
			self.oneRowGenerater(line, cfg.FONT_SIZE)
		self.pageGenerater()

	def initPos(self):
		screen = QDesktopWidget().screenGeometry()  # QDesktopWidget为一个类，调用screenGeometry函数获得屏幕的尺寸
		x = screen.width()/2 - self.size.width()/2
		y = screen.height() - cfg.BUTTOM_OFFSET
		self.move(int(x), int(y)) # 调用move移动到指定位置

	def paintEvent(self, event):	# 绘制窗口
		paint = QPainter(self)
		self.textBox = self.textPages[self.currentPage]

		self.resize(self.textBox.size())	# 获取图片大小
		self.setMask(self.textBox.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.textBox.width(), self.textBox.height(), self.textBox)

	def oneRowGenerater(self, text, font_size = 24): # (内容, 大小)	# 将文字印在图片上
		font = ImageFont.truetype('./img/parchment/font/方正像素12.ttf', font_size)   # 字体路径及文本大小
		text_width, text_height = font.getsize(text)	# 字体框大小
		image = Image.new(mode = 'RGBA', size = (text_width, text_height))  # 生成图像
		draw_table = ImageDraw.Draw(im = image)
		draw_table.text(xy = (0, 0), text = text, fill = cfg.FONT_COLOR, font = font)	# 生成文本为白色
 
		self.textPic.append(image)

	def oneRowSlicer(self):	# 将文本切为若干行
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
			temp = Image.open('./img/parchment/DialogDownPointer.png')
		else:
			temp = Image.open('./img/parchment/Dialog.png')

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

	def mousePressEvent(self, event):		# 鼠标左键按下时, 换页
		if event.button() == Qt.LeftButton:
			if self.currentPage < len(self.textPages) - 1:
				self.currentPage += 1
				self.update()
			else:
				self.currentPage = 0
				self.quit()
			event.accept()

	def quit(self):
		self.close()