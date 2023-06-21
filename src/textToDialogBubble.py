from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL import Image, ImageDraw, ImageFont, ImageQt

import time

import cfg

class textToDialogBubble(QWidget):
	'需要显示文本的窗口的基类'

	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		'参数 s 即使只有一行, 也必须写为字符串数组格式([""])'

		super(textToDialogBubble, self).__init__(parent)

		# 窗口初始化
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.SubWindow)
		self.setAutoFillBackground(False)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.update()

		# 文本框图片, 需要继承重载
		self.textBox_LastPage = Image.open(textBox_LastPage_Path)	# 最后一页的文本框图片
		self.textBox_NormalPage = Image.open(textBox_NormalPage_Path)	# 非最后一页的文本框图片(如果只有一页, 可以和上一项填一样的地址)
		self.textBox = QPixmap(textBox_LastPage_Path)	# 用于初始化计算

		self.textRaw = s	# 未处理文本
		self.textSliced = []
		self.textPic = []
		self.textPages = []
		self.currentPage = 0
		self.size = self.textBox.size()	# 获取文本框图片的大小

		self.charPerLine = int((self.size.width() - cfg.INITIAL_OFFSET[1]) / (cfg.FONT_SIZE + cfg.HORIZONTAL_SPACING)) - 1	# 每行字符数
		self.linePerPage = int((self.size.height() - cfg.INITIAL_OFFSET[0]) / (cfg.FONT_SIZE + cfg.VERTICAL_SPACING))	# 每页行数

		self.oneRowSlicer()
		for line in self.textSliced:
			self.oneRowGenerater(line, cfg.FONT_SIZE)
		self.pageGenerater()

	def paintTextBox(self):	# 绘制文本框
		paint = QPainter(self)
		self.textBox = self.textPages[self.currentPage]	# 播放当前页数对应的图片

		self.resize(self.textBox.size())	# 获取图片大小
		self.setMask(self.textBox.mask())   # 设置蒙版
		paint.drawPixmap(0, 0, self.textBox.width(), self.textBox.height(), self.textBox)

	def paintEvent(self, event):	# 绘制窗口
		self.paintTextBox()

	'''文本生成'''
	def oneRowGenerater(self, text, font_size = 24):	# 单行文本图片生成器	# (内容, 字体大小)
		font = ImageFont.truetype('./img/parchment/font/方正像素12.ttf', font_size)   # 字体路径及文本大小
		text_width, text_height = font.getsize(text)	# 字体框大小
		image = Image.new(mode = 'RGBA', size = (text_width, text_height))  # 生成空白底片
		draw_table = ImageDraw.Draw(im = image)
		draw_table.text(xy = (0, 0), text = text, fill = cfg.FONT_COLOR, font = font)	# 生成文本为白色
 
		self.textPic.append(image)	# 将生成的单行文本图片保存到 textPic

	def oneRowSlicer(self):
		for s in self.textRaw:	# 为了处理 str 数组
			self.Slicer(s)

	def Slicer(self, s):	# 单行文本切割
		textLen = 0	# 文本占位长度
		counter = 0	# 扫描到的下标位置
		needSlice = False
		for word in s:	# 扫描textRaw中的每个字符, 并记录占位长度
			if '\u4e00' <= word <= '\u9fff':	# 中文字符占两位, 英文字符占一位
				textLen += 2
			else:
				textLen += 1
			counter += 1
			if textLen > self.charPerLine*2:
				needSlice = True
				break
		if needSlice:	# 递归剪切过长的片段
			self.textSliced.append(s[:counter])
			self.oneRowSlicer(s[counter:])
		else:
			self.textSliced.append(s)

	def pageGenerater(self):
		if len(self.textPic) > self.linePerPage:	# 检测是否为最后一页
			temp = self.textBox_NormalPage
		else:
			temp = self.textBox_LastPage

		target = Image.new(mode = 'RGBA', size = (temp.width, temp.height))	# 根据文本框大小创建画布
		for i in range(0, self.linePerPage):	# 将 包含文本的透明图片(一行行地) 与 文本框图片 贴在一起, 生成用于显示的图片
			if i >= len(self.textPic):
				break
			target.paste(self.textPic[i], (cfg.INITIAL_OFFSET[0], cfg.INITIAL_OFFSET[1] + (cfg.FONT_SIZE + cfg.VERTICAL_SPACING)*i))	# 左上角坐标, 初始偏移量(y, x)	# 不是(x, y)?
		temp = Image.alpha_composite(temp, target)	# 带Alpha通道的粘贴
		temp = ImageQt.toqpixmap(temp)	# QImage => QPixmap

		self.textPages.append(temp)

		if len(self.textPic) > self.linePerPage:	# 还有未生成的文本行, 则递归调用生成下一页
			self.textPic = self.textPic[self.linePerPage:]
			self.pageGenerater()

''''''

class textToDialogBubble_WithFadeOut(textToDialogBubble):
	'关闭事件淡出效果'
	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		textToDialogBubble.__init__(self, s, textBox_NormalPage_Path, textBox_LastPage_Path)

		self.startTime = time.time()
		self.fadeOutAnimation = None

		self.timer = QTimer()	# 初始化一个定时器
		self.timer.start(int(1000/cfg.FPS))	# 设置时间间隔并启动定时器
		self.timer.timeout.connect(self.checkTimer)

	def closeEvent(self, event):	# 关闭窗口时淡出
		if self.fadeOutAnimation == None:
			self.fadeOutAnimation = QPropertyAnimation(self, b"windowOpacity") # 设置动画对象
			self.fadeOutAnimation.setDuration(1000)	# 设置动画时长(毫秒)
			self.fadeOutAnimation.setStartValue(1)	# 设置初始属性，1.0为不透明
			self.fadeOutAnimation.setEndValue(0)	# 设置结束属性，0为完全透明
			self.fadeOutAnimation.finished.connect(self.close)	# 动画结束时，关闭窗口
			self.fadeOutAnimation.start()	# 开始动画
			event.ignore()	# 忽略事件

'''
	def closeEvent(self, event):	# 意外发现的闪烁效果, 不过这样写窗口是彻底关不掉了
		self.fadeOutAnimation = QPropertyAnimation(self, b"windowOpacity") # 设置动画对象
		self.fadeOutAnimation.setDuration(1000)	# 设置动画时长(毫秒)
		self.fadeOutAnimation.setStartValue(1)	# 设置初始属性，1.0为不透明
		self.fadeOutAnimation.setEndValue(0)	# 设置结束属性，0为完全透明
		self.fadeOutAnimation.finished.connect(self.close)	# 动画结束时，关闭窗口
		self.fadeOutAnimation.start()	# 开始动画
		event.ignore()	# 忽略事件
'''

	def checkTimer(self):	# 对话框显示时间
		if time.time() - self.startTime > cfg.displayTime:
			self.timer.stop()	# 停止计时器, 防止反复调用
			self.close()