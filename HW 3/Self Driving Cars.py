import copy
import numpy as np
import math
cityMap = None
mapOfCarPosWithCity = {}
cacheResult = {}
dx = [0, -1, 0, 1] # configuration to move in the x coordinate in the four directions
dy = [-1, 0, 1, 0] # configuration to move in the y coordinate in the four directions
def printCityMap():
    global cityMap
    for i in range(len(cityMap)):
        for j in range(len(cityMap)):
            print(cityMap[i][j])
class GridConfiguration:
    def __init__(self, startPosition, endPosition, rewardMap, directionMap, utilityMap, directionMapVar):
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.rewardMap = rewardMap
        self.directionMap = directionMap
        self.utilityMap = utilityMap
        self.directionMapVar = directionMapVar
    def __str__(self):
        return str(self.startPosition) + " " + str(self.endPosition) + " " + str(self.rewardMap) + " " + str(self.directionMap) + " " + str(self.utilityMap) +" " + str(self.directionMapVar)

class AutonomousCars:
    def __init__(self, sizeOfCity, numberOfCars, numberOfObstacles, startPositionsOfCars, endPositionOfCars):
        self.sizeOfCity = sizeOfCity # the size of the city
        self.numberOfCars = numberOfCars # total number of cars
        self.numberOfObstacles = numberOfObstacles # total number of obstacles
        self.startPositionsOfCars = startPositionsOfCars # start position of all the cars
        self.endPostionOfCars = endPositionOfCars # end position of all the cars
    def turnLeft(self, currentMove):
        # turns the move in the left direction
        if currentMove == (0, 1):#right
            return (-1, 0)#up
        if currentMove == (-1, 0):#up
            return (0, -1)#left
        if currentMove == (0, -1):#left
            return (1, 0) # down
        if currentMove == (1, 0): #down
            return (0, 1) #right

    def turnRight(self, currentMove):
        # turns the move in the right direction
        if currentMove == (0, 1): #right
            return (1, 0) # down
        if currentMove == (1, 0):# down
            return (0, -1) #left
        if currentMove == (0, -1):#left
            return (-1, 0) #up
        if currentMove == (-1, 0):#up
            return (0, 1) #right

    def simulate(self):
        # code to simulate the uncertain enviornment and the uncertain nature of the move
        global  mapOfCarPosWithCity
        global  cacheResult
        result = []
        for i in range(self.numberOfCars):
            totalPoints = 0
            currentPolicy = mapOfCarPosWithCity[(self.endPostionOfCars[i][0], self.endPostionOfCars[i][1])]
            if (self.startPositionsOfCars[i], currentPolicy.endPosition) in cacheResult:
                # print(cacheResult)
                answer = cacheResult[(self.startPositionsOfCars[i], currentPolicy.endPosition)]
                # print(answer)
                result.append(answer)
                continue
            for j in range(10):
                points = 0
                np.random.seed(j)
                swerve = np.random.random_sample(1000000)
                k = 0
                currentPosition = (self.startPositionsOfCars[i][0], self.startPositionsOfCars[i][1])
                if currentPosition == currentPolicy.endPosition:
                    totalPoints = 1000
                    break
                while currentPosition != currentPolicy.endPosition:
                    currentMove = currentPolicy.directionMap[currentPosition[0]][currentPosition[1]]
                    if swerve[k] > 0.7:
                        if swerve[k] > 0.8:
                            if swerve[k] > 0.9:
                                currentMove = self.turnLeft(self.turnLeft(currentMove))
                            else:
                                currentMove = self.turnRight(currentMove)
                        else:
                            currentMove = self.turnLeft(currentMove)
                    k += 1
                    if self.isSafe(currentPolicy.utilityMap, currentPosition[0] + currentMove[0], currentPosition[1] + currentMove[1]):
                        currentPosition = (currentPosition[0] + currentMove[0], currentPosition[1] + currentMove[1])
                    points += currentPolicy.rewardMap[currentPosition[0]][currentPosition[1]]
                # print(points)
                totalPoints += points
            answer = int(math.floor(totalPoints / 10))
            cacheResult[(self.startPositionsOfCars[i], currentPolicy.endPosition)] = answer
            result.append(answer)
        return result

    def generatePolicy(self):
        # generates the most optimal and efficient policy to reach the reward state
        global mapOfCarPosWithCity
        for key in mapOfCarPosWithCity:
            # destinationTuple = (self.endPostionOfCars[i][0], self.endPostionOfCars[i][1])
            currentGrid =  mapOfCarPosWithCity[key]
            epsilon = 0.1
            gamma = 0.9
            limit = epsilon * 0.1 / 0.9
            newUtilityMap = [[0 for i in range(self.sizeOfCity)] for j in range(self.sizeOfCity)]
            count = 0
            newDirectionMap = [[(0, 0) for i in range(self.sizeOfCity)] for j in range(self.sizeOfCity)]
            newdirectionMapVar = [['X' for i in range(self.sizeOfCity)] for j in range(self.sizeOfCity)]
            while True:
                delta = 0
                count += 1
                # newUtilityMap = [[0 for i in range(self.sizeOfCity)] for j in range(self.sizeOfCity)]
                currentGrid.directionMap = copy.deepcopy(newDirectionMap)
                currentGrid.directionMapVar = copy.deepcopy(newdirectionMapVar)
                for i in range(self.sizeOfCity):
                    for j in range(self.sizeOfCity):
                        # newUtilityMap[currentGrid.endPosition[0]][currentGrid.endPosition[1]] = 99
                        if (i, j) == currentGrid.endPosition:
                            newUtilityMap[currentGrid.endPosition[0]][currentGrid.endPosition[1]] = 99
                            continue
                        previousUtility = currentGrid.utilityMap[i][j]
                        goLeft = self.calculateUtilityPerMove(currentGrid.utilityMap, i, j, 0, -1)
                        goUp = self.calculateUtilityPerMove(currentGrid.utilityMap, i, j, -1, 0)
                        goRight = self.calculateUtilityPerMove(currentGrid.utilityMap, i, j, 0, 1)
                        goDown = self.calculateUtilityPerMove(currentGrid.utilityMap, i, j, 1, 0)
                        maxScore = max(goLeft, goUp, goRight, goDown)
                        if maxScore == goUp:
                            direction = (-1, 0)
                            directionVar = '^'
                        else:
                            if maxScore == goDown:
                                direction = (1, 0)
                                directionVar = 'v'
                            else:
                                if maxScore == goRight:
                                    direction = (0, 1)
                                    directionVar = '>'
                                else:
                                    if maxScore == goLeft:
                                        direction = (0, -1)
                                        directionVar = '<'
                        if currentGrid.startPosition == (i, j):
                            directionVar = 'S'
                        newUtilityMap[i][j] = np.float64(currentGrid.rewardMap[i][j] + 0.9 * maxScore)
                        newDirectionMap[i][j] = direction
                        newdirectionMapVar[i][j] = directionVar

                        if abs(newUtilityMap[i][j] - previousUtility) > delta:
                            delta = abs(newUtilityMap[i][j] - previousUtility)
                if delta < limit:
                    break
                currentGrid.utilityMap = copy.deepcopy(newUtilityMap)

    def isSafe(self, utilityMap, i, j):
        # returns whether the given move is safe of not
        return i >= 0 and i < len(utilityMap) and j >= 0 and j < len(utilityMap)

    def calculateUtilityPerMove(self, utilityMap, rowIndex, columnIndex, rowDeviation, columnDeviation):
        #calculate utility per move by row column deviation
        result = 0
        maxProbablity = 0.7
        minProbablity = 0.1
        minProb = 0
        global dx, dy
        for i in range(len(dx)):
            rowDx = dx[i]
            colDx = dy[i]
            if((rowDeviation, columnDeviation) == (rowDx, colDx)):
                if(self.isSafe(utilityMap, rowIndex + rowDx, columnIndex + colDx)):
                    result += maxProbablity * utilityMap[rowIndex + rowDx][columnIndex + colDx]
                    continue
                else:
                    result += maxProbablity * utilityMap[rowIndex][columnIndex]
                    continue
            if (self.isSafe(utilityMap, rowIndex + rowDx, columnIndex + colDx)):
                minProb += utilityMap[rowIndex + rowDx][columnIndex + colDx]
            else:
                minProb += utilityMap[rowIndex][columnIndex]
        result += minProbablity * minProb
        return np.float64(result)

def main():
    # input0 : 95
    # input1 : 88, 97, 84, 82, 92
    # input2 :82, 76, 82, 65, 77, 45
    # input 4: [88, 100, 29, 29, 68, 77, 97, 84, 82, 92]
    # input 5: [30,30]
    # input 6: [-88]
    # input 7: [-45]
    # input 9: [93, 83, 79, 83, -45, 91, -224, 73, 85]
    # input 10: [89, 63, 84, 86, -2182]
    # input 11:
    # pdf name input : 95

    linesOfInput = tuple(open("input.txt", 'r'))
    outputFile = open('output.txt', 'w')
    linesOfInput = [l.strip() for l in linesOfInput]
    position = 0
    sizeOfCity = int(linesOfInput[position])
    # print("sizeOfCity", sizeOfCity)
    position += 1
    numberOfCars = int(linesOfInput[position])
    # print("numberOfCars", numberOfCars)
    position += 1
    numberOfObstacles = int(linesOfInput[position])
    # print("numberOfObstacles", numberOfObstacles)
    position += 1
    global cityMap
    global mapOfCarPosWithCity
    cityMap = [[-1 for i in range(sizeOfCity)] for j in range(sizeOfCity)]
    for i in range(numberOfObstacles):
        obstaclePosition = linesOfInput[position].split(',')
        position += 1
        # print("obstacleposition", obstaclePosition)
        cityMap[int(obstaclePosition[1])][int(obstaclePosition[0])] = -101
    # for i in range(sizeOfCity):
    #     for j in range(sizeOfCity):
    #         print(cityMap[i][j], end=' ')
    #     print()
    startPositionsOfCars = []
    # print(startPositionsOfCars)
    for i in range(numberOfCars):
        startPosition = linesOfInput[position].split(',')
        startPositionsOfCars.append((int(startPosition[1]), int(startPosition[0])))
        # cityMap[int(startPosition[1])][int(startPosition[0])] = 0
        position += 1
    endPositionOfCars = []
    for i in range(numberOfCars):
        destinationOfCar = linesOfInput[position].split(',')
        destinationOfCarTuple = int(destinationOfCar[1]), int(destinationOfCar[0])
        endPositionOfCars.append(destinationOfCarTuple)
        temp = cityMap[destinationOfCarTuple[0]][destinationOfCarTuple[1]]
        cityMap[destinationOfCarTuple[0]][destinationOfCarTuple[1]] = 99
        directionMap = [[(0, 0) for m in range(sizeOfCity)] for n in range(sizeOfCity)]
        utilityMap = [[0 for l in range(sizeOfCity)] for x in range(sizeOfCity)]
        # utilityMap[destinationOfCarTuple[0]][destinationOfCarTuple[0]] = 99
        directionMapVar = [['X' for k in range(sizeOfCity)] for y in range(sizeOfCity)]
        mapOfCarPosWithCity[destinationOfCarTuple] = GridConfiguration(startPositionsOfCars[i], destinationOfCarTuple, copy.deepcopy(cityMap), directionMap, copy.deepcopy(cityMap), directionMapVar)
        cityMap[destinationOfCarTuple[0]][destinationOfCarTuple[1]] = temp
        position += 1
    # for i in range(sizeOfCity):
    #     for j in range(sizeOfCity):
    #         print(cityMap[i][j], end=' ')
    #     print()
    # for key in mapOfCarPosWithCity:
    #     print (key, 'corresponds to', mapOfCarPosWithCity[key])
    autoCar = AutonomousCars(sizeOfCity, numberOfCars, numberOfObstacles, startPositionsOfCars, endPositionOfCars)
    autoCar.generatePolicy()
    result = autoCar.simulate()
    # print(result)
    for i in range(len(result)):
        outputFile.write(str(result[i]) + "\n")
    # for key in mapOfCarPosWithCity:
    #     currentGrid = mapOfCarPosWithCity[key]
    #     currentGrid.printValues()
    #     print (key, 'corresponds to', mapOfCarPosWithCity[key])
# print(np.finfo(np.float64))
main()