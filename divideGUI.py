import socket 
from tkinter import *
import numpy as np
from PIL import Image
from PIL import ImageDraw
import _thread
import pickle
import threading
import os
# Multithreaded Python server : TCP Server Socket Thread Pool
import time
from time import sleep

import random
import sys
 
#Global variables used throughout the program
squareSize = 50
penWidth = 0
rows = 10
img = Image.new('1', (squareSize, squareSize), 0)  
percentFilledChecker = ImageDraw.Draw(img)
filledThreshold = 0.5
canvasList = []
mouseEventList = []
pixels = squareSize*squareSize
lastx = 0
lasty = 0

window = Tk()
window.title("Divide and Conquer")

end = False

global connectionIsOK
connectionISOK = True




global CurrentGameBoard
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
global startLock
global ReceiveQueue
global genesis
global rtt 
ReceiveQueue = []
notConnected = True
firstConnection = True
myUserID = ""
CurrentGameBoard = []
lock = threading.BoundedSemaphore(value=1)
IPList = []
socketUseList = []
colors = ["red","green","blue","black"]

#IPList.append ('192.168.0.17')
ConnectionList = []
serverLock = threading.BoundedSemaphore(value=1)
reconnectLock = threading.BoundedSemaphore(value=1)

syncLock = threading.BoundedSemaphore(value=1)
startLock = threading.BoundedSemaphore(value=1)



 
def getFastestUser(queue):
	fastest = 0
	for i in range(len(queue)):
		if(queue[i]["Time"]< queue[fastest]["Time"]):
			fastest = i
	return queue[fastest]


class GameStateObj:
	color = ""
	canvasNumber = 0
	state ="Normal"
	UserID = ""

  
SquareState = GameStateObj()
ServerSquareState =  GameStateObj()

def PriorityServerUpdate(gameStateDict):
	global ReceiveQueue,CurrentGameBoard
	if ("gameState" in gameStateDict):
		#message = GameStateObj()
		Message = gameStateDict["gameState"]
		print ("Server received data:",Message.color, Message.canvasNumber,Message.UserID)
		if(Message.color=="yellow" and Message.state == "disabled"):
			ReceiveQueue.append(gameStateDict)
			priorityValue = getFastestUser(ReceiveQueue)
			ReceiveQueue.remove(priorityValue)
			priorityState = priorityValue["gameState"]
			if(CurrentGameBoard[int(priorityState.canvasNumber)-1].state !="disabled"):
				#lock.acquire()
				print("priority queue processed Server:",priorityState.UserID)
				CurrentGameBoard[int(priorityState.canvasNumber)-1].color = priorityState.color
				CurrentGameBoard[int(priorityState.canvasNumber)-1].UserID = priorityState.UserID
				CurrentGameBoard[int(priorityState.canvasNumber)-1].state = priorityState.state
				#canvasList[int(priorityState.canvasNumber)-1].config(background = priorityState.color,state = priorityState.state)
				#lock.release()
		else:
			#lock.acquire()
			print("direct Updating value for Server",Message.UserID)
			CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
			CurrentGameBoard[int(Message.canvasNumber)-1].UserID = Message.UserID
			CurrentGameBoard[int(Message.canvasNumber)-1].state = Message.state
			canvasList[int(Message.canvasNumber)-1].config(background = Message.color,state = Message.state)
			#lock.release()
		

 
	 
	

def HandleReconnectToAnotherServer():
	global tcpClientA
	global IPList
	global notConnected
	while (True):
		print("IPlist is",IPList)
		reconnectLock.acquire()
	
		if(notConnected):
			#Reconnecting MSG
			if (not firstConnection):
				hideGrid()
			if(IPList[0]!= (socket.gethostbyname(socket.gethostname()))):
				# check ip list vs your own ip
				try:
					print("checking for old socket")
					#if(socketUseList):
						# print("oldSocket found and pop")
						# oldSocket = socketUseList.pop()
						# oldSocket.shutdown(socket.SHUT_RDWR)
						# oldSocket.close()

					time.sleep(4.0)
					print("IPlist2 is",IPList)
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
					print("Connected. Establishing rtt")
					calculateRTT(tcpClientA)
					socketUseList.append(tcpClientA)
					syncLock.release()
					print("should be connect")
					notConnected = False
					if (not firstConnection):
						showGrid()	
				
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
			time.sleep(0.1)
			data = pickle.dumps(gameStateMessage)
			conn.send(data)
			#print("size of server data", str(sys.getsizeof(pickle.dumps(gameStateMessage))))
			
#def server insert
# 	insert into the queue with time stamp delay. 

 
def ReceiveUpdatesFromClient(conn,ip,port): 
	global ReceiveQueue
	while True : 
			try:
				data = conn.recv(20000) 
				#check that field other wise.
				data = pickle.loads(data)
				#print("serverRecievedData",data)
				if ("gameState" in data):
					#message = GameStateObj()
					Message = data["gameState"]
					#print( "Client time is " +  str(data["Time"]) ) 

					print ("Server received data:",Message.color, Message.canvasNumber,Message.UserID)
					if(Message.color=="yellow" and Message.state == "disabled"):
						ReceiveQueue.append(data)
						priorityValue = getFastestUser(ReceiveQueue)
						ReceiveQueue.remove(priorityValue)
						priorityState = priorityValue["gameState"]
						if(CurrentGameBoard[int(priorityState.canvasNumber)-1].state !="disabled"):
							lock.acquire()# be careful of these locks!
							print("priority queue processed user:",priorityState.UserID)
							CurrentGameBoard[int(priorityState.canvasNumber)-1].color = priorityState.color
							CurrentGameBoard[int(priorityState.canvasNumber)-1].UserID = priorityState.UserID
							CurrentGameBoard[int(priorityState.canvasNumber)-1].state = priorityState.state
							canvasList[int(priorityState.canvasNumber)-1].config(background = priorityState.color,state = priorityState.state)
							lock.release()# seems like we don't need them
							# further testing required.

					#	get highest yellow item insert
					# 	current gaem board set 
					#else:
					#  if color not yellow and disabled.
					# set the color. 
					#add to queue
					# take out smallest time stamp. 
					##here have a sorted priority queue based on time. 
					# server has its own function to add to this queue
					# here we process the queue. and set the canvas board based on prioity
					# average send time. 
					#
					#get highest priority. 
					else:
						lock.acquire()
						print("direct Updating value for User",Message.UserID)
						CurrentGameBoard[int(Message.canvasNumber)-1].color = Message.color
						CurrentGameBoard[int(Message.canvasNumber)-1].UserID = Message.UserID
						CurrentGameBoard[int(Message.canvasNumber)-1].state = Message.state
						canvasList[int(Message.canvasNumber)-1].config(background = Message.color,state = Message.state)
						lock.release()
				elif("Alive" in data):
					print("Alive")
					continue
			
			except Exception as e: 
				print("receive update from client exception",e)
				pass

			
			
class UpdateClientFromServer(threading.Thread): 
 
	def __init__(self): 
		threading.Thread.__init__(self) 
	   
	
	def run(self): 
		
		global firstConnection 
		global tcpClientA
		global CurrentGameBoard
		global IPList,penWidth,rows,filledThreshold,myUserID
		global genesis

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
							#print(i,CurrentGameBoard[i-1].state)
							canvasList[i-1].config(background = CurrentGameBoard[i-1].color, state = CurrentGameBoard[i-1].state)#, state = CurrentGameBoard[i-1].state)
				
				#elif( "IPList" in data):
					#print("IpListRecieved",data["IPList"])
					#global IPList
					#IPList = data["IPList"]
					#print(IPList)

	
				elif( "initialise" in data):

					genesis = time.time()
					
					print("initialise", data)
					IPList = data["IPList"]
					print("IpListRecieved",IPList)

					penWidth = data["Penwidth"]
					print("penWidthreceived",penWidth)

					rows = data["rows"]
					print("rows received:",rows)

					filledThreshold = data["threshold"]
					print("Threshold received",filledThreshold)
					myUserID = data["UserID"]
					print("UserID received",myUserID)
					startLock.release()
				
			#TODO:change test general exception. 
			except socket.timeout:
				pass
				# global notConnected
				# global reconnectLock
				# reconnectLock.release()
				# notConnected = True
				# print("reconnecting to next Server")
				# pass

			except Exception as e:
				#print("update client from server exception",e)
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
			#if(socketUseList):
				# print("oldSocket found and pop")
				# oldSocket = socketUseList.pop()
				# oldSocket.shutdown(socket.SHUT_RDWR)
				# oldSocket.close()

			TCP_IP = '0.0.0.0' 
			TCP_PORT = 2008
			BUFFER_SIZE = 20  # Usually 1024, but we need quick response 
			tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
			tcpServer.bind((socket.gethostname(), TCP_PORT))    
			print("binded waiting for players")
			global number
			players = 0 
			number = 0
			print("Len IPLIST", len(IPList))
			print("IP List: ")
			print(IPList)
			 
			global firstConnection
			if (not firstConnection):
				print("not first connection")
				#len of the IP list now for that many clients.
				number = int(len(IPList))-1
				IPList.clear()
				#number = number -1


			if(isServer):
				while players<number: 
					tcpServer.listen(4) 
					print ("Multithreaded Python server : Waiting for connections from TCP clients..." )
					(conn,(ip,port)) = tcpServer.accept() 
					try:
						calculateRTT(conn)
						_thread.start_new_thread(ReceiveUpdatesFromClient,(conn,ip,port,))
						_thread.start_new_thread(sendConstantUpdatesToClient,(conn,ip,port,))
						print("newConnection")
						IPList.append(ip)
						ConnectionList.append(conn)
					except:
						print ("Error: unable to start thread")
					players = players+1

				print("Do I get HEre?")
				if (not firstConnection):
					showGrid()
		if(isServer):
			print("sending initiliaze data")
			global penWidth,rows,filledThreshold,myUserID, genesis
			ownIP = socket.gethostbyname(socket.gethostname())
			#inpput here
			#print("Enter Pen width(1-10)")
			#inPenwidth = input()

			#penWidth = 10

			#print("Enter ")
			
			#rows = 6
			#filledThreshold = 25
			genesis = time.time()
			if(firstConnection):
				myUserID =0

				toSend = {"initialise":1,"IPList":IPList,"Penwidth":penWidth,"rows":rows,"threshold":filledThreshold}
				
				print(rows)
				print(penWidth)
				print(filledThreshold)
		
				for i in range (len(ConnectionList)):#len(IPList):
					toSend.update({"UserID":i+1})
					ConnectionList[i].send(pickle.dumps(toSend))
					del toSend["UserID"]
				startLock.release()
				break
'''
		if(isServer):
			ownIP = socket.gethostbyname(socket.gethostname())
			disctIpList = {"IPList":IPList}
			for i in range (len(ConnectionList)):#len(IPList):
				ConnectionList[i].send(pickle.dumps(disctIpList))
			break
'''
		 
	   
		#threads.append(newthread)
		
def calculateRTT(conn):
	global rtt
	global isServer
	if(isServer): 
		conn.send(b'DEADBEEF')
	else:
		currTime = time.time()
		conn.recv(1024)
		afterTime = time.time()
		elapsedTime = afterTime - currTime
		rtt = elapsedTime / 2
		print("My RTT is : " + str(rtt))
		
def PositionIntoIndex(position):
	columnNumber = position %rows
	rowNumber = position//rows
	return (rowNumber,columnNumber)


#Function that is called on the initial click of the mouse on one of the tiles
#Stores the lastx and last y coordinates for line drawing
#Has the logic for the locking mechanism for tiles
def xy(event):
	global lastx, lasty
	#Check for if the tile is in a disabled state (you should not be able to draw in it)
	if event.widget.cget('state') != 'disabled':
		#If not, update lastx and lasty and append to mouseEventList
		lastx, lasty = event.x, event.y
		mouseEventList.extend([lastx, lasty])  
		#Calculate the index for the canvasList for server use
		id = str(event.widget)
		position =0
		if(len(id)==9):
			position = int(id[8])
		if(len(id)==11):
			position = int(id[8])*100+ int(id[9])*10 + int(id[10])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
		if (isServer):
			#TODO: delete?
			#lock.acquire()
			#buffer system to check the times, then if that time is
			# smallest then set it, 
			# other wise, dont
			# server buffer time is added some delay. 
			ServerSquareState.color = "yellow"
			ServerSquareState.state = "disabled"
			ServerSquareState.canvasNumber = position
			ServerSquareState.UserID = myUserID
			currentTime = time.time() - genesis
			#add some delay time aswell. 
			message = {"gameState":ServerSquareState,"Time":currentTime}
			PriorityServerUpdate(message)
			
			#currentTime = time.time()
			#CurrentGameBoard[int(position)-1].color = "yellow" 
			#CurrentGameBoard[int(position)-1].state = "disabled"
			#CurrentGameBoard[int(position)-1].UserID = myUserID
			# add user
			#lock.release()

		elif (not isServer):
			SquareState.color = "yellow"
			SquareState.state = "disabled"
			SquareState.canvasNumber = position
			SquareState.UserID = myUserID
			currentTime = time.time() - genesis - rtt
			# time stamp for yellow
			message = {"gameState":SquareState,"Time":currentTime}
			data = pickle.dumps(message)
   
			tcpClientA.send(data) 

#Function to draw the line while mouse button is held down
#Is pretty much for the local user		  
def addLine(event):
	global lastx, lasty
	global isServer
	#Check if you can draw a line
	if event.widget.cget('state') != 'disabled':   
		#Restrict the x and y coordinates to be within the tile 	 
		if event.x > squareSize:
			event.x = squareSize
		if event.x < 0:
			event.x = 0
		if event.y > squareSize:
			event.y = squareSize
		if event.y < 0:
			event.y = 0
		#Creates a line in the clicked on widget
		event.widget.create_line((lastx, lasty, event.x, event.y), width=penWidth)
		mouseEventList.extend([event.x, event.y])
		lastx, lasty = event.x, event.y

def checkIfServerAlive():
	global tcpClientA, isServer
	message = {"Alive":1}
	while (True):
		if(isServer):
			break
		time.sleep(4)	
		if(tcpClientA):
			try:
				data = pickle.dumps(message)
				tcpClientA.send(data)
			
			except Exception as e:
			 
				print("Server down",e)
				global notConnected
				global reconnectLock

				reconnectLock.release()
				notConnected = True
				print("handling disconnect")
				pass



#Function that is called when user releases the mouse button
#Calculate the percentage of the filled grid and contacts server
def doneStroke(event):
	if event.widget.cget('state') != 'disabled':
		global SquareState, percentFilled, filledThreshold, percentFilledChecker
		#Draws the line in the invisible pillow img to calculate % filled
		percentFilledChecker.line(mouseEventList, fill=1, width=penWidth)
		output = np.asarray(img)
		percentFilled = np.count_nonzero(output)/pixels
		percentFilledString = str(int(round(percentFilled*100, 0)))
		
		#Calculate the index of the tile in the canvasList array
		position = 0
		id = str(event.widget)
		position =0
		if(len(id)==9):
			position = int(id[8])
		if(len(id)==11):
			position = int(id[8])*100+ int(id[9])*10 + int(id[10])
		if(len(id)==10):
			position = int(id[8])*10 + int(id[9])
		if(len(id)==8):
			position = 1
		#If greater than threshold
		if (int(percentFilledString)> int(filledThreshold)):

			color = colors[int(myUserID)%4]

			#Clear the % checker img for reuse
			percentFilledChecker.rectangle((0,0,squareSize,squareSize), fill=0)
			#Clear the mouse event list for reuse
			mouseEventList.clear()

			if (isServer):
				ServerSquareState.color = color
				ServerSquareState.state = "disabled"
				ServerSquareState.canvasNumber = position
				ServerSquareState.UserID = myUserID
				message = {"gameState":ServerSquareState}
				PriorityServerUpdate(message)

				#lock.acquire()
				#CurrentGameBoard[int(position)-1].color = color
				#CurrentGameBoard[int(position)-1].state = "disabled"
				#CurrentGameBoard[int(position)-1].UserID = myUserID
				#lock.release()
				#clear list?
			elif (not isServer):
				SquareState.color = color
				SquareState.state = "disabled"
				SquareState.canvasNumber = position
				SquareState.UserID = myUserID
				
				message = {"gameState":SquareState}
				data = pickle.dumps(message)
				tcpClientA.send(data) 
				#clear list?

		   
		#add delay here to sync time
		else:
			#Clear the % checker img for reuse
			percentFilledChecker.rectangle((0,0,squareSize,squareSize), fill=0)
			#Clear the mouse event list for reuse
			mouseEventList.clear()
			if(isServer):
				ServerSquareState.color = "grey"
				ServerSquareState.state = "normal"
				ServerSquareState.canvasNumber = position
				ServerSquareState.UserID = ""
				message = {"gameState":ServerSquareState}
				PriorityServerUpdate(message)
				#lock.acquire()
				#CurrentGameBoard[int(position)-1].color = "grey" 
				#CurrentGameBoard[int(position)-1].state = "normal"
				#CurrentGameBoard[int(position)-1].UserID = ""
				# call another function. that sets its game board. 
				#lock.release()
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
		

	#Clears all the drawing in the tile
	event.widget.delete("all")

#Hides the gameboard grid
def hideGrid():
	global canvasList
	for item in canvasList:
		item.grid_remove()		

#Shows the gameboard grid
def showGrid():
	print("Show Grid Called")
	global canvasList
	for item in canvasList:
		item.grid()

#Function to check for the end of the game
#Will print into the main canvas and close the game in 15 seconds if endstate is found
def endChecker():
	global end, canvasList, window
	squares = rows*rows
	while end == False:
		endDict={"red":0,
			"black":0,
			"green":0,
			"blue":0
		}
		#Iterate through the grid and tally the colors
		for item in canvasList:
			if item.cget('bg') == "red":
				endDict["red"] += 1
			if item.cget('bg') == "black":
				endDict["black"] += 1
			if item.cget('bg') == "green":
				endDict["green"] += 1
			if item.cget('bg') == "blue":
				endDict["blue"] += 1
		total = sum(endDict.values())    
		if total >= squares:
			print("End State!")
			hideGrid()
			end = True
			#Find the highest value
			highestKey = max(endDict.values())
			#Find all the key values that match the highest key
			winnerKeys = [k for k, v in endDict.items() if v == highestKey]
			winners = ""
			#If more than one winner
			if len(winnerKeys) > 1:
				#Append the list of winners
				for num in range(len(winnerKeys)):
					if num < len(winnerKeys)-1:
						winners += winnerKeys[num] + " & "
					else:
						winners += winnerKeys[num]
				winners = winners.upper()
				endmsg = "Game is Over\n\nRed had " + str(endDict["red"]) + " squares.\nGreen had " + str(endDict["green"]) + " squares.\nBlue had " + str(endDict["blue"]) + " squares.\nBlack had " + str(endDict["black"]) + " squares.\n\nThe Winners are " + winners
				Label(window, text=endmsg, font= ("Arial", 36)).grid()
			#Only one winner
			else:
				winners = winnerKeys[0].upper()
				endmsg = "Game is Over\n\nRed had " + str(endDict["red"]) + " squares.\nGreen had " + str(endDict["green"]) + " squares.\nBlue had " + str(endDict["blue"]) + " squares.\nBlack had " + str(endDict["black"]) + " squares.\n\nThe Winner is " + winners
				Label(window, text=endmsg, font= ("Arial", 36)).grid()
			#Sleep for 15 and kill the program
			time.sleep(15)
			os._exit(1)
		#Sleep 1 second
		time.sleep(1)
	return None

#Function for the back button
def backToStart():
    for widget in window.winfo_children():
        widget.destroy()
    roleCheck()

#Clears all the widgets in the window
def clearScreen():
	for widget in window.winfo_children():
			widget.destroy()

#Main menu, checks if you are the server or client
def roleCheck():
	global isServer
	isServer = False
	Label(window, text="\n      Welcome to Divide and Conquer      ").pack()
	Label(window, text="\nAre you a server or a client?\n").pack()
	Label(window, text="       ").pack(side=LEFT)
	button1 = Button(window, text="Server", command=serverGUI)
	button1.pack(side=LEFT)
	Label(window, text="       ").pack(side=RIGHT)
	button2 = Button(window, text="Client", command=clientGUI)
	button2.pack(side=RIGHT)
	Label(window, text="\n\n").pack()

#Main menu for the server
def serverGUI():
    global isServer
    isServer = True
    clearScreen()
    hostIP = str(socket.gethostbyname(socket.gethostname()) )
    titleLabel = Label(window, text="\nDivide and Conquer - Server Settings")
    titleLabel.pack()
    ipLabel = Label(window, text="Server IP: "+hostIP)
    ipLabel.pack()
    rowLabel = Label(window, text="\n# of Rows")
    rowLabel.pack()
    rowScale = Scale(window, from_=1, to=10, orient=HORIZONTAL)
    rowScale.pack()
    penLabel = Label(window, text="\nPen Width")
    penLabel.pack()
    penScale = Scale(window, from_=1, to=10, orient=HORIZONTAL)
    penScale.pack()
    threshLabel = Label(window, text="\nFilled Threshold %")
    threshLabel.pack()
    filledThresholdScale = Scale(window, from_=1, to=100, orient=HORIZONTAL)
    filledThresholdScale.pack()
    Label(window, text="").pack()
    buttonFrame = Frame(window)
    buttonFrame.pack()
    button = Button(buttonFrame, text="Submit Settings", command=lambda: submitSettings(rowScale, penScale, filledThresholdScale))
    button.pack(side=LEFT)
    Label(buttonFrame, text=" ").pack(side=LEFT)
    button = Button(buttonFrame, text="Back", command=backToStart)
    button.pack(side=LEFT)
    Label(window, text="").pack()

#Main menu for the Client
def clientGUI():
	clearScreen()
	Label(window, text="\nEnter the IP of the server\n").pack()
	entryFrame = Frame(window)
	entryFrame.pack()
	Label(entryFrame, text="Server IP:").pack(side=LEFT)
	ipEnter = Entry(entryFrame)
	ipEnter.insert(0, "192.168.137.")
	ipEnter.pack(side=LEFT)
	Label(entryFrame, text="").pack(side=LEFT)
	Label(window, text="").pack()
	buttonFrame = Frame(window)
	buttonFrame.pack()
	button1 = Button(buttonFrame, text="Submit IP", command= lambda: clientLobby(ipEnter))
	button1.pack(side=LEFT)
	Label(buttonFrame, text=" ").pack(side=LEFT)
	button2 = Button(buttonFrame, text="Back", command=backToStart)
	button2.pack(side=LEFT)
	Label(window, text="").pack()

#Function that is called when server hits "Submit Settings" button
#Makes button that you press to start the server
def submitSettings(rowScale, penScale, filledThresholdScale):
	global window, rows, penWidth, filledThreshold, startLock
	startLock.acquire()
	rows = rowScale.get()
	penWidth= penScale.get()
	filledThreshold = filledThresholdScale.get()
	clearScreen()
	print(rows)
	print(penWidth)
	print(filledThreshold)
	button = Button(window, text="Start Server", command=start)
	button.pack(anchor=CENTER)

#Function that is called when the Client enters the IP
#Makes a button you press called Connect to Server to connect to a running server
def clientLobby(ipEnter):
	global connectionIP
	connectionIP = ipEnter.get()
	print(connectionIP)
	for widget in window.winfo_children():
		widget.destroy()
	button = Button(window, text="Connect to Server", command=start)
	button.pack(anchor=CENTER)

#The start function, launches all the threads and logic after client/server press start
def start():
	global window
	countNumber = 0

	if (not isServer):

		global connectionIP
		IPList.append(connectionIP)
		_thread.start_new_thread(HandleReconnectToAnotherServer,())
		UpdateBoard = UpdateClientFromServer()
		UpdateBoard.start()
		startLock.acquire()
		sleep(1)
		_thread.start_new_thread(checkIfServerAlive,())

	_thread.start_new_thread(TurnClientIntoServer,())

	#Initilize the game board
	clearScreen()
	startLock.acquire()
	for r in range(rows):
		for c in range(rows):
			item = Canvas(window, bg="grey", height=squareSize, width=squareSize)
			item.grid(row=r, column=c)
			#Bind the functions to the widgets
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
	startLock.release()
	#Starts the endChecker Thread
	print("DO i get here?")
	_thread.start_new_thread(endChecker,())


#The "Main" function, takes you to rolecheck dialog and starts the tkinker main loop
roleCheck()
window.mainloop()