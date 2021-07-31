import cv2
import os

def scanFile(path):
	img = cv2.imread(path, -1)
	out = open(os.path.join(path[ :-4] + '.txt'), 'w')
	height = img.shape[0]
	width = img.shape[1]

	minX = width
	minY = height
	maxX = 0
	maxY = 0

	for x in range(0, width):
		for y in range(0, height):
			if img[y][x][3] != 0:
				if x < minX:
					minX = x
				if y < minY:
					minY = y
				if x > maxX:
					maxX = x
				if y > maxY:
					maxY = y

	out.write(str(minX) + '\n' + str(minY) + '\n' + str(maxX) + '\n' + str(maxY))
	print(minX, minY, maxX, maxY)
	out.close()

def scanThisDir(path):  #扫描文件夹，通过递归遍历
    path_list = os.listdir(path)
    for filename in path_list:
        filesrc = os.path.join(path, filename)
        if os.path.isdir(filesrc):  #打开文件夹，下一层递归
            scanThisDir(filesrc)
        if os.path.splitext(filename)[1] == '.png':  #打开.png文件
            scanFile(filesrc)

### main ###
path = os.getcwd()  #获得当前目录
scanThisDir(path)   #从当前目录开始扫描