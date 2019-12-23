import argparse
import os

parser = argparse.ArgumentParser(description='Compare folders')
parser.add_argument('--userpath', help='Add user path')
parser.add_argument('rec', help='Recursive? default is true')
parser.add_argument('--dir1', help='Add dir1')
parser.add_argument('--dir2', help='Add dir2')
args = vars(parser.parse_args())

dir1 = args['dir1']
dir2 = args['dir2']
userPath = args['userpath'] or os.getcwd()
recursive = args['rec'] or True
dir1AbsPath = os.path.join(userPath, dir1)
dir2AbsPath = os.path.join(userPath, dir2)

def getFileList(rootpath):
    filelist=[]
    for root, dirs, files in os.walk(rootpath):
        filelist.append()


if recursive:
    

else:
    listFile1 = os.listdir(dir1AbsPath)
    listFile2 = os.listdir(dir2AbsPath)
    retD = list(set(listFile1).difference(set(listFile2)))

print(retD)