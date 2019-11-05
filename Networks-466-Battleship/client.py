import sys
import requests 


# while True:
# 	msg = s.recv(128)
# 	print(msg.decode("utf-8"))

def updateBoard(board):
	open('opp_board.txt', 'w').close()
	with open("opp_board.txt", 'w') as f:
		for innerlist in board:
			for item in innerlist:
				f.write(item)

def readBoardFile(boardFile):
	with open(boardFile) as boardFile:
		board = [list(line) for line in boardFile]
	return board

def printBoard(board):
	for row in board:
		print(' '.join(row))

if __name__ == "__main__":
	host = str(sys.argv[1])
	port = str(sys.argv[2])
	x_coordinate = str(sys.argv[3])
	y_coordinate = str(sys.argv[4])
	oppBoard = readBoardFile('opp_board.txt')
	uri = "http://" + str(host) + ":" + str(port)
	fireMessage = {'x_coordinate' : x_coordinate,
				   'y_coordinate' : y_coordinate}

	r = requests.get(url = uri, params=fireMessage)
	response = r.text

	
	if (response == ""):
		print("response empty")

	if "1" in response:
		print("Hit")
		oppBoard[int(x_coordinate)][int(y_coordinate)] = "X"
		updateBoard(oppBoard)
	elif "0" in response:
		print("Miss")
		oppBoard[int(x_coordinate)][int(y_coordinate)] = "0"
		updateBoard(oppBoard)

	print(response + "\n")
	printBoard(oppBoard)

	