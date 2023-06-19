import cv2
import os
import numpy

def generater(filename):
	img = cv2.imdecode(numpy.fromfile(os.path.join('./' + filename), dtype = numpy.uint8), cv2.IMREAD_UNCHANGED)	# OpenCV读取中文路径
	height = img.shape[0]
	width = img.shape[1]
#	depth = img.shape[2]	# 图像通道数

	minX = width
	minY = height
	maxX = 0
	maxY = 0

	for y in range(0, height):
		for x in range(0, width):
			if img[y][x][3] != 0:
				if x < minX:
					minX = x
				if y < minY:
					minY = y
				if x > maxX:
					maxX = x
				if y > maxY:
					maxY = y

	for y in range(minY, maxY):
		for x in range(minX, maxX):
			if img[y][x][3] == 0:
				for i in range(0, 3):
					img[y][x][i] = 255
				img[y][x][3] = 1	# Alpah通道赋值

	cv2.imencode(".png", img)[1].tofile(os.path.join('./' + filename))

if __name__ == '__main__':
	path_list = os.listdir('./')
	for filename in path_list:
		if os.path.splitext(filename)[1] == '.png':  #打开.png文件
			generater(filename)