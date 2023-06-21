import os
import cfg

class ponyPropertyPos():
	'载入小马位置资源'
	def __init__(self, parent=None, **kwargs):
		self.textPix = {}
		self.loadPos()

	def loadPos(self):	# 载入相对位移数据
		self.textPix.update({'' : [self.loadText(os.path.join('./img/ponyAction/stand', str(0) + '.txt'))]})

		temp = []
		for i in range(0, 16):
			temp.append(self.loadText(os.path.join('./img/ponyAction/trot', str(i) + '.txt')))
		self.textPix.update({'trot' : temp})

		temp = []
		for i in range(0, 9):
			temp.append(self.loadText(os.path.join('./img/ponyAction/sit', str(i) +'.txt')))
		self.textPix.update({'sitDown' : temp})

		temp = []
		for i in range(9, 16):
			temp.append(self.loadText(os.path.join('./img/ponyAction/sit', str(i) +'.txt')))
		self.textPix.update({'standUp' : temp})

		temp = []
		for i in range(0, 7):
			temp.append(self.loadText(os.path.join('./img/ponyAction/lie', str(i) +'.txt')))
		self.textPix.update({'lieDown' : temp})

		temp = []
		for i in range(7, 13):
			temp.append(self.loadText(os.path.join('./img/ponyAction/lie', str(i) +'.txt')))
		self.textPix.update({'getUp' : temp})

		temp = []
		for i in range(0, 15):
			temp.append(self.loadText(os.path.join('./img/ponyAction/boop', str(i) +'.txt')))
		self.textPix.update({'standBoop' : temp})

		temp = []
		for i in range(0, 17):
			temp.append(self.loadText(os.path.join('./img/ponyAction/boop-sit', str(i) +'.txt')))
		self.textPix.update({'sitBoop' : temp})

		temp = []
		for i in range(0, 15):
			temp.append(self.loadText(os.path.join('./img/ponyAction/boop-lie', str(i) +'.txt')))
		self.textPix.update({'lieBoop' : temp})

	def loadText(self, path):
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(int(line))

		return temp

class followPonyPos(ponyPropertyPos):
	'跟随小马位置'

	def __init__(self, parent=None, **kwargs):
		ponyPropertyPos.__init__(self)

		# 初始化
		self.BUBBLE_OFFSET = [0, 0]	# 对话框相对于当前姿势有效图片左上角x, y轴的偏移像素
		self.IMG_WIDTH = 50	# 这个参数我忘了意义:<

		# 从信号槽读取
		self.posX = 0	# 主窗口坐标
		self.posY = 0	# 主窗口坐标
		self.running_action = ''
		self.actualAction = 0
		self.mirrored = False
		self.picNum = 0

	'''定位至小马头顶'''
	def moveToPos(self):
		x = 0
		y = 0

		if self.running_action == '':	# 根据小马当前的姿态调整偏移量
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
			x = self.IMG_WIDTH - (x + 0)	# 这个算法我忘了推倒过程:<
		x += self.posX
		y += self.posY

		return x, y	# 返回目标坐标
	''''''

	'''信号处理'''
	def getData(self, posX, posY, running_action, actualAction, mirrored, picNum):
		self.posX = posX	# 主窗口坐标
		self.posY = posY	# 主窗口坐标
		self.running_action = running_action
		self.actualAction = actualAction
		self.mirrored = mirrored
		self.picNum = picNum
	''''''