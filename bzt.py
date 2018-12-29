# encoding: utf-8
import threading
import random
import sys
from optparse import OptionParser
import time
import copy
from functools import reduce


generals = []
loyal_votes = []
MESSAGE = 50

MUTEX = threading.Lock()


def split_msg(msg) :
	path,m = msg.split(':')
	return (map(int,path.split('->')),int(m))

class general(threading.Thread):

	N = 7
	M = 2
	def __init__(self,iscommander,istraitor,id):
		threading.Thread.__init__(self)
		self.isCommander = iscommander
		self.isTraitor = istraitor
		self.ID = id
		self.queue = []
		self.messages = []
		self.mutex = threading.Lock()
		self.finish = False

	def run(self) :
	
		time.sleep(0.5)

		if self.isCommander :
			self.send_command(":%d" % (MESSAGE))
			self.finish = True
		else :
			num = reduce(lambda x,y:x+y,[reduce(lambda x,y:x*y, i) \
				for i in [[general.N-2-m1 for m1 in range(0,m+1)]  \
					for m in range(0,general.M)]])+1

			# exchange msgs
			while num > len(self.messages):
				msg = self.recv()
				self.messages.append(msg)
				self.send_command(msg)

		
			for m in self.messages :
				path,msg = split_msg(m)
				path = list(path)
				if len(path) == 1 :
					result = self.vote(path,msg,general.M)
					break

			if not self.isTraitor:
				loyal_votes.append(result)
					

	def vote(self,path,msg,m):
		# 没当过指挥官且不是当前指挥官的将军
		generals = [ x for x in range(0,general.N) if x not in path and x != self.ID]
	
		results = [msg]

		# 递归完了，返回
		if m == 0:
			return self.get_msg(path)

		# 该指挥官发送它的值，然后调用Om(m-1)	
		else:
			for g in generals :
				tmp_path = copy.copy(path)
				tmp_path.append(g)
				msg = self.get_msg(tmp_path)

				result = self.vote(tmp_path,msg,m-1)
				results.append(result)

			# MESSAGE是否出现了半数以上
			opposite = "1" if MESSAGE == "0" else "0"
			if results.count(MESSAGE) > results.count(opposite):
				return str(MESSAGE)
			else:
				return opposite


	def get_msg(self,path) :
		path = "->".join(map(str,path))
		for msg in self.messages:
			p,m = msg.split(':')
			if p == path :
				return int(m)

		assert(False)

	def send_command(self,msg) :
		path,cmd = msg.split(":")

		# 该将军已经发过消息了
		if path=='':
			path = [self.ID]
		else:
			path = map(int,path.split('->'))
			path = list(path)
			path.append(self.ID)

		if len(path) == general.M + 2 : return False

		for g in generals :
			if g.ID not in path :
				msg = '->'.join(map(str,path))
				if self.isTraitor and g.ID % 2 == 0:
					cmd = str(0) if cmd == "1" else "0"

				self.send(g,msg+':'+cmd)
		return True

	def send(self,dest,msg):
		if  dest.mutex.acquire():
			dest.queue.append(msg)
			dest.mutex.release()

	def recv(self) :
		msg = None
		while msg is None :
			if self.mutex.acquire():
				if(len(self.queue) > 0):
					msg = self.queue.pop(0)
				self.mutex.release()
			if msg is None :
				time.sleep(0.01)

		return msg

if __name__ == '__main__':
		
	parser = OptionParser()
	# 递归层数
	parser.add_option("-m", dest="M")
	# 将军是忠诚还是叛徒
	parser.add_option("-g", dest="gens")
	# 第0的将军作为指挥官的指令
	parser.add_option("-c", dest="command")
	options, _ = parser.parse_args()
	general.N = len(options.gens)
	general.M = int(options.M)
	MESSAGE = int(options.command)
	
	for i in range(general.N) :
		g = general(i==0,options.gens[i].upper() == "T",i)
		generals.append(g)
		g.start()

	for g in generals :
		g.join()

	# 检测正确性
	# 所有忠诚的下属都遵守相同的命令
	print("Votes: ", loyal_votes)
	for v in loyal_votes:	
		assert(v == loyal_votes[0])

	# 如果指挥官是忠诚的，那么每个忠诚的下属都必须遵守他发出的命令
	if options.gens[0].upper() == "L":
		print("Command: ", options.command)
		assert(loyal_votes[0] ==  options.command)
	print("success")







