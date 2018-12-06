
import signal
import time
import timeit
from datetime import datetime

result = -999

class Situation:
	def __init__(self,board):
		self.numberOfPoliceToPlace = 0 # stores the number of police to place on the board
		self.board = board # stores the current configuration of the board

	def destinationReached(self):
		# returns true if terminal state is reached i.e. when all the police are placed safely
		if self.numberOfPoliceToPlace != totalNumberOfPoliceToPlace:
			return False
		return True

	def isCellSafe(self, row, col, whetherToAddSubtract):
		# returns whether a particular cell is safe or not
		safeBoardConfiguration[row][col] += whetherToAddSubtract
		for ix in range(gridSize):
			if ix != col:
				safeBoardConfiguration[row][ix] += whetherToAddSubtract
		for iy in range(gridSize):
			if iy != row:
				safeBoardConfiguration[iy][col] += whetherToAddSubtract
		ix, iy = row, col
		while ix >= 0 and iy >= 0:
			if ix != row and iy != col:
				safeBoardConfiguration[ix][iy] += whetherToAddSubtract
			ix -= 1
			iy -= 1
		jx, jy = row, col
		while jx < gridSize and jy >= 0:
			if jx != row and jy != col:
				safeBoardConfiguration[jx][jy] += whetherToAddSubtract
			jx += 1
			jy -= 1
		jx, jy = row, col
		while jx >= 0 and jy < gridSize:
			if jx != row and jy != col:
				safeBoardConfiguration[jx][jy] += whetherToAddSubtract
			jx -= 1
			jy += 1
		jx, jy = row, col
		while jx < gridSize and jy < gridSize:
			if jx != row and jy != col:
				safeBoardConfiguration[jx][jy] += whetherToAddSubtract
			jx += 1
			jy += 1

class Node:
	def __init__(self,board, parent=None):
		# captures the situation of the board at each instance
		self.situation = Situation(board=board)

	def is_Destination(self):
		# tells us whether destination is reached or not
		return self.state._goal_check()
def updateSum(node):
	# update the smax sum considering the current configuration and also after flipping and transposing the matrix
	global result
	currentSum = 0
	transposeMatrixSum = 0
	lrFlipMatrixSum = 0
	udFlipMatrixSum = 0
	for xPointer in range(gridSize):
		for yPointer in range(gridSize):
			if node.situation.board[xPointer][yPointer] == 1:
				currentSum += activityPointsMatrix[xPointer][yPointer]
				transposeMatrixSum += activityPointsMatrix[yPointer][xPointer]
				lrFlipMatrixSum += activityPointsMatrix[xPointer][gridSize - yPointer - 1]
				udFlipMatrixSum += activityPointsMatrix[gridSize - xPointer - 1][yPointer]
	result = max(currentSum, transposeMatrixSum, lrFlipMatrixSum, udFlipMatrixSum, result)

class Solution():
	def solutionAlgorithm(self, currentPolice, currentRow, node):
		# gives most efficient solution securig maximum points after placing all police officers correctly
		if (currentPolice == totalNumberOfPoliceToPlace):
			updateSum(node)
			return
		if totalNumberOfPoliceToPlace - currentPolice <= gridSize - currentRow:
			for i in range(gridSize):
				if safeBoardConfiguration[currentRow][i] >= 0:
					node.situation.board[currentRow][i] = 1
					node.situation.isCellSafe(currentRow, i, -1)
					self.solutionAlgorithm(currentPolice + 1, currentRow + 1, node)
					node.situation.board[currentRow][i] = 0
					node.situation.isCellSafe(currentRow, i, 1)
			self.solutionAlgorithm(currentPolice, currentRow + 1, node)

def handleTimeOut(signum, frame):
	with open('output.txt', "w+") as out:
		out.write(str(result))
	exit()

def InputParameters():
	fileInput = open('input.txt', 'r')
	gridSize = int(fileInput.readline()) # size of the grid
	totalPolice = int(fileInput.readline()) # total number of police
	numberOfScooter = int(fileInput.readline()) # total number of scooters
	pathCostMatrix = [0] * gridSize
	for ixPointer in range(gridSize): # captures all the path cost of the entire grid
		pathCostMatrix[ixPointer] = [0] * gridSize
	for oneInput in fileInput.readlines():
		locationParameters = oneInput.split(",")
		x = int(locationParameters[0])
		y = int(locationParameters[1])
		pathCostMatrix[x][y] = pathCostMatrix[x][y] + 1
	return gridSize, totalPolice, pathCostMatrix

if __name__ == '__main__':
	start_time = time.time()
	gridSize, totalNumberOfPoliceToPlace, activityPointsMatrix = InputParameters()
	outputFile = open("output.txt", "w")

	board = [[0 for x in range(gridSize)] for x in range(gridSize)]
	safeBoardConfiguration = [[0 for x in range(gridSize)] for x in range(gridSize)]
	result = -999
	node = Node(board=board)
	signal.signal(signal.SIGALRM, handleTimeOut)
	signal.alarm(170)
	solution = Solution()
	solution.solutionAlgorithm(0, 0, node)
	outputFile.write(str(result)) # prints output to file

