
from tkinter import *
import numpy as np
from PIL import Image
from PIL import ImageDraw
import socket 

import _thread
import pickle
import threading
# Multithreaded Python server : TCP Server Socket Thread Pool
#
import time
from time import sleep

from tkinter import *
import random
import sys
 
 

global connectionIsOK
connectionISOK = True

window = Tk()
window.title("Divide and Conquer")
global rows
rows = 4
squareSize = 50
global canvasList 
global CurrentGameBoard
global AreaList
global countNumber
global SquareState
global myUserID
global ConnectionList
global IPList
global tcpClientA
global firstConnection
global reconnectLock
global serverLock
global lock
global IPList
notConnected = True

firstConnection = True
myUserID = ""
canvasList = []
CurrentGameBoard = []
AreaList = []
lock = threading.BoundedSemaphore(value=1)
IPList = []
socketUseList = []
colors = ["red","green","blue","black"]


#IPList.append ('192.168.0.17')
ConnectionList = []
serverLock = threading.BoundedSemaphore(value=1)
reconnectLock = threading.BoundedSemaphore(value=1)

syncLock = threading.BoundedSemaphore(value=1)
 # try to connect to the new server here 
				# if success close the previous, 
				# reset a socket to anotehr ip.
				# close the preious                     

				# check the top of the list
				# if its me set me to it. 
				# if not ping that list guy. 
				# then update your list status to that guy as the server
				# 
				# if unreachable delete him
				# try with the next guy in the list. 

class GameStateObj:
	color = ""
	name = ""
	canvasNumber = 0
	percentageComplete = 0
	rowIndex = 0
	columnIndex = 0
	state ="Normal"
	UserID = ""

  
SquareState = GameStateObj()


	 
def HandleReconnectToAnotherServer():
	global tcpClientA
	global IPList
	global notConnected
	while (True):
		print("tryng to connect to ",IPList)
		reconnectLock.acquire()
	
		if(notConnected):
			if(IPList[0]!= (socket.gethostbyname(socket.gethostname()))):
				try:
					print("checking for old socket")
					if(socketUseList):
						print("oldSocket found and pop")
						oldSocket = socketUseList.pop()
						oldSocket.shutdown(socket.SHUT_RDWR)
						oldSocket.close()

					time.sleep(4.0)
					print("tryng to connect to ",IPList)
					print("first value is ", IPList[0])
					host = IPList[0]
					IPList.remove(host)
					port = 2008
					print ("host is",host) 
					print("connecting to server")
					syncLock.acquire()
					print("inside syncLock creating socket")
					tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
					tcpClientA.settimeout(5)

					tcpClientA.connect((host, port))
					print("after connect client")
					socketUseList.append(tcpClientA)
					syncLock.release()
					print("should be connect")
					notConnected = False
				
				except Exception as e:  
					print("unable to connect",e)
					notConnected = True
			else:
				print("starting new server session as Server")
				global isServer
				isServer= True
				print("isServer",isServer)
				#global serverLock
				serverLock.release()
				print("serverLock released, isServer set to true")
				#_thread.start_new_thread(TurnClientIntoServer,(isServer,))
		
				
	 

def sendConstantUpdatesToClient(conn,ip,port): 
		while True :
			global CurrentGameBoard
			gameStateMessage = {"gameBoard":CurrentGameBoard}
			#sleep the same as client send to send to all clients. 
			time.sleep(0.2)
			data = pickle.dumps(gameStateMessage)
			conn.send(data)
			#print("size of server data", str(sys.getsizeof(pickle.dumps(gameStateMessage))))
			


 
def ReceiveUpdatesFromClient(conn,ip,port): 
	while True : 
			try:
				data = conn.recv(20000) 
				#check that field other wise.
				data = pickle.loads(data)
				print("serverRecievedData",data)
				if ("gameState" in data):
					message = GameStateObj()
					Message = data["gameState"]
					print ("Server received data:",Message.color, Message.canvasNumber)
					lock.acquire()
					CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
					CurrentGameBoard[int(Message.canvasNumber)-1].UserID = Message.UserID
					canvasList[int(Message.canvasNumber)-1].config(background = Message.color,state = Message.state)
					# if not user update
					lock.release()
			
			except Exception as e: 
				print(e)

			
			
class UpdateClientFromServer(threading.Thread): 
 
	def __init__(self): 
		threading.Thread.__init__(self) 
	   
	
	def run(self): 
		
		global firstConnection 
		global tcpClientA
		global CurrentGameBoard
		while True :  
			try:
				if(firstConnection):
					sleep(5)
					print("firstConnection")
					firstConnection = False
				data = tcpClientA.recv(10000)
				data = pickle.loads(data)
			
				if("gameBoard" in data):
					CurrentGameBoard = data["gameBoard"]
					for i in range(len(CurrentGameBoard)):
						if (CurrentGameBoard[i-1].UserID == myUserID and CurrentGameBoard[i-1].color=="yellow" and CurrentGameBoard[i-1].state=="disabled"):
							continue
						else:
							print(i,CurrentGameBoard[i-1].state)
							canvasList[i-1].config(background = CurrentGameBoard[i-1].color, state = CurrentGameBoard[i-1].state)#, state = CurrentGameBoard[i-1].state)
				elif( "IPList" in data):
					print("IpListRecieved",data["IPList"])
					global IPList
					IPList = data["IPList"]
					print(IPList)

			except socket.timeout:
			 
				global notConnected
				global reconnectLock
				reconnectLock.release()
				notConnected = True
				print("reconnecting to next Server")
				pass

			except Exception as e:
				#print(e)
				pass
					

			   

		

def TurnClientIntoServer():
	print("entering while loops")
	global isServer
	while(True):
		serverLock.acquire()
		print("in while lock aquired")
		print("isServer",isServer)
		if(isServer):
			print("isServer is true in if statement")
			print("checking for old socket")
			if(socketUseList):
				print("oldSocket found and pop")
				oldSocket = socketUseList.pop()
				oldSocket.shutdown(socket.SHUT_RDWR)
				oldSocket.close()

			TCP_IP = '0.0.0.0' 
			TCP_PORT = 2008
			BUFFER_SIZE = 20  # Usually 1024, but we need quick response 
			tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
			tcpServer.bind((socket.gethostname(), TCP_PORT))    
			print("binded waiting for players")
			global number
			players = 0 
			number = 2
			
			global firstConnection
			if (not firstConnection):
				print("not first connection")
				#len of the IP list now for that many clients. 
				number = 1

			if(isServer):
				while players<number: 
					tcpServer.listen(4) 
					print ("Multithreaded Python server : Waiting for connections from TCP clients..." )
					(conn,(ip,port)) = tcpServer.accept() 
					try:
						_thread.start_new_thread(ReceiveUpdatesFromClient,(conn,ip,port,))
						_thread.start_new_thread(sendConstantUpdatesToClient,(conn,ip,port,))
						print("newConnection")
						IPList.append(ip)
						ConnectionList.append(conn)
					except:
						print ("Error: unable to start thread")
					players = players+1


		if(isServer):
			ownIP = socket.gethostbyname(socket.gethostname())
			disctIpList = {"IPList":IPList}
			for i in range (len(ConnectionList)):#len(IPList):
				ConnectionList[i].send(pickle.dumps(disctIpList))
			break

		 
	   
		#threads.append(newthread)
		
 
def PositionIntoIndex(position):
	columnNumber = position %rows
	rowNumber = position//rows
	return (rowNumber,columnNumber)

def xy(event):
	global lastx, lasty  
	lastx, lasty = event.x, event.y
	if event.widget.cget('state') != 'disabled':   
		id = str(event.widget)
		position =0
		if(len(id)==9):
			position = int(id[8])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
		print("Position", position)
		if (isServer):
			lock.acquire()

			CurrentGameBoard[int(position)-1].color = "yellow" 
			CurrentGameBoard[int(position)-1].state = "disabled"
			CurrentGameBoard[int(position)-1].UserID = myUserID
			# add user
			lock.release()

		elif (not isServer):
			SquareState.color = "yellow"
			SquareState.state = "disabled"
			SquareState.canvasNumber = position
			SquareState.UserID = myUserID
			message = {"gameState":SquareState}
			data = pickle.dumps(message)
   
			tcpClientA.send(data) 

		  
def addLine(event):
	global lastx, lasty
	global isServer
	if event.widget.cget('state') != 'disabled':   
		
			 
		if event.x > squareSize:
			event.x = squareSize
		if event.x < 0:
			event.x = 0
		if event.y > squareSize:
			event.y = squareSize
		if event.y < 0:
			event.y = 0
		#Creates a line in the clicked on widget
		event.widget.create_line((lastx, lasty, event.x, event.y), width=5)
		lastx, lasty = event.x, event.y

		print( (lastx, lasty) )
		global AreaList
		AreaList.append(tuple((lastx, lasty)))
		AreaList = list(set(AreaList))






def doneStroke(event):
	if event.widget.cget('state') != 'disabled':
		#DEBUG - Picks a random color to set the BG   
		#Clears all the drawing inside the Canvas
		global SquareState
		#Sets the background color and disables the canvas
		color = "grey"
		print ("canvas List:")
		
		position = 0
		id = str(event.widget)
		position =0

		if(len(id)==9):
			position = int(id[8])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
		print("Position", position)

		if len(AreaList)>20:
			color = colors[int(myUserID)%4]
			event.widget.config(bg=color, state="disabled")
			

			if (isServer):
				lock.acquire()
				CurrentGameBoard[int(position)-1].color = color
				CurrentGameBoard[int(position)-1].state = "disabled"
				CurrentGameBoard[int(position)-1].UserID = myUserID
				lock.release()
			elif (not isServer):
				SquareState.color = color
				SquareState.state = "disabled"
				SquareState.canvasNumber = position
				SquareState.UserID = myUserID
				message = {"gameState":SquareState}
				data = pickle.dumps(message)
				tcpClientA.send(data) 

		   
		#add delay here to sync time
		else:
			print("not over 50")
			if(isServer):
				lock.acquire()
				CurrentGameBoard[int(position)-1].color = "grey" 
				CurrentGameBoard[int(position)-1].state = "normal"
				CurrentGameBoard[int(position)-1].UserID = ""

				lock.release()
				 # disbale the color for all other users
				# that user though does not get diabled

			elif (not isServer):
				print("reset press")
				SquareState.color = "grey"
				SquareState.state = "normal"
				SquareState.UserID = ""
				SquareState.canvasNumber = position
				message = {"gameState":SquareState}
				data = pickle.dumps(message)
				tcpClientA.send(data) 
		

		print (len(AreaList))
		del AreaList[:]
		print("new Listlength")
		print(len(AreaList))

		event.widget.delete("all")
		
 
print("EnterID")
myUserID = input()

print("isServer?")
Server = input()

if(Server=="yes"):
	isServer = True
else:
	isServer = False

countNumber = 0

if (not isServer):
	IPList.append(socket.gethostname())
	_thread.start_new_thread(HandleReconnectToAnotherServer,())
	UpdateBoard = UpdateClientFromServer()
	UpdateBoard.start()
	#start thread here


 
_thread.start_new_thread(TurnClientIntoServer,())


for r in range(rows):
	for c in range(rows):
		item = Canvas(window, bg="grey", height=squareSize, width=squareSize)
		item.grid(row=r, column=c)
		item.bind("<Button-1>", xy)
		item.bind("<B1-Motion>", addLine)
		item.bind("<B1-ButtonRelease>", doneStroke)
	   
		canvasList.append(item)
		countNumber =countNumber+1
		state = GameStateObj()
		state.canvasNumber = countNumber
		state.color = "grey"
		state.state = "normal"
		CurrentGameBoard.append(state)



					   
print(window.grid_size())
window.mainloop()
 
 
 







