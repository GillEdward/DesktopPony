import multiprocessing
import os

#  根据需要填写需要运行的命令
def clearUp():
	open('./temp/headBubble.txt', 'w', encoding = 'utf-8').write('')
	open('./temp/liveDM.txt', 'w', encoding = 'utf-8').write('')

def readingDM():
    os.system('python ./readingDM.py')

def liveSprite():
    os.system('python ./liveSprite.py')

def DesktopPet():
    os.system('python ./DesktopPet.py')

def bubbleDialogForPony():
    os.system('python ./bubbleDialogForPony.py')

if __name__ == '__main__': 
    p0 = multiprocessing.Process(target=clearUp)
    p1 = multiprocessing.Process(target=readingDM)
    p2 = multiprocessing.Process(target=liveSprite)
    p3 = multiprocessing.Process(target=DesktopPet)
    p4 = multiprocessing.Process(target=bubbleDialogForPony)
 
    # 启动子进程
    p0.start()
    p1.start()
    p2.start()
    p3.start()
    p4.start()
 
    # 等待fork的子进程终止再继续往下执行，可选填一个timeout参数
    p0.join()
    p1.join()
    p2.join()
    p3.join()
    p4.join()