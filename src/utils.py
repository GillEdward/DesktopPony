import os

def create_txt(file_path: str)->None:
	'''
	创建txt文件

	:param file_path: txt文件路径
	'''

	dir_path = os.path.dirname(file_path)
	if not os.path.exists(dir_path):  # 如果目录不存在则创建目录
		os.makedirs(dir_path)
	if not os.path.exists(file_path): # 如果文件不存在则创建文件
		with open(file_path, "x") as file: # 保证不会覆盖原有内容
			file.close()

def txt_init()->None:
	'''
	txt文件初始化
	'''

	create_txt('./temp/ponyPos.txt')
	create_txt('./temp/headBubble.txt')
	create_txt('./temp/liveDM.txt')