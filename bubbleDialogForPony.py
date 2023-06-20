import sys

import cfg

from src.dialogBoxes import *

class bubbleDialogForPony():
	def __init__(self, s, textBox_NormalPage_Path : str, textBox_LastPage_Path : str, parent=None, **kwargs):
		self.textBox_NormalPage_Path = textBox_NormalPage_Path
		self.textBox_LastPage_Path = textBox_LastPage_Path

		self.bubbleDialog = Pony_OverheadDialogBox(s, self.textBox_NormalPage_Path, self.textBox_LastPage_Path)
		self.bubbleDialogCurrentText = ''

		self.showBubbleDialog = False

		self.animationTimer = QTimer()
		self.animationTimer.start(int(1000/cfg.FPS)) # 动画更新速度同步屏幕帧率
		self.animationTimer.timeout.connect(self.bubbleDialog.update)
		self.animationTimer.timeout.connect(self.updateBubbleDialogText)	# 读取弹幕文本信息
		self.animationTimer.timeout.connect(self.bubbleDialogUpdate)

	def readText(self, path):	# 读取txt文件, 返回一个str数组
		temp = []

		f = open(path, encoding = 'utf-8')
		for line in f:
			temp.append(line)

		f.close()
		return temp

	def updateBubbleDialogText(self):	# 检测是否有新文本
		text = self.readText(os.path.join('./headBubble.txt'))
		if text != self.bubbleDialogCurrentText and text != []:
			self.bubbleDialog = Pony_OverheadDialogBox(text, self.textBox_NormalPage_Path, self.textBox_LastPage_Path)
			self.bubbleDialogCurrentText = text
			self.showBubbleDialog = True	# 有新文本的标记

	def bubbleDialogUpdate(self):
		self.bubbleDialog.getData()
		self.bubbleDialog.update()
		if self.showBubbleDialog:	# 有新内容, 更新头顶气泡
			self.bubbleDialog.show()
			self.showBubbleDialog = False	# 文本已更新, 将标记重置


'''run'''
if __name__ == '__main__':
	app = QApplication(sys.argv)
	pet = bubbleDialogForPony('', './img/parchment/DialogBubble.png', './img/parchment/DialogBubble.png')
	sys.exit(app.exec_())