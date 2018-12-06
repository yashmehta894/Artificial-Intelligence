import copy
import timeit
import signal

answer = None


class Person:
    def checkLAHSAElligible(self, age, sex, ownsPet):
        # checks whether applicant is elligible for LAHSA or not
        if bool(int(age) > 17) & bool(sex == 'F') & bool(ownsPet == 'N'):
            return True
        return False

    def checkSPLAElligible(self, ownsCar, ownsDL, medicalHealth):
        # checks whether applicant is elligible for SPLA or not
        if bool(ownsCar == 'Y') & bool(ownsDL == 'Y') & bool(medicalHealth == 'N'):
            return True
        return False

    def __init__(self, applicantId, sex, age, ownsPet, medicalHealth, ownsCar, ownsDL, timeTableForWeek):
        self.applicantId = applicantId
        self.sex = sex
        self.age = age
        self.ownsPet = ownsPet
        self.medicalHealth = medicalHealth
        self.ownsCar = ownsCar
        self.ownsDL = ownsDL
        self.timeTableForWeek = timeTableForWeek
        self.isPersonLAHSAElligible = self.checkLAHSAElligible(age, sex, ownsPet)
        self.isPersonLAHSAElligibleOnly = self.checkLAHSAElligible(age, sex, ownsPet)
        self.isPersonSPLAElligibleOnly = self.checkSPLAElligible(ownsCar, ownsDL, medicalHealth)
        self.isPersonSPLAElligible = self.checkSPLAElligible(ownsCar, ownsDL, medicalHealth)
        self.isPersonEligibleForBoth = self.isPersonLAHSAElligible and self.isPersonSPLAElligible
        self.checkForCommon = 0
        if (self.isPersonEligibleForBoth):
            self.checkForCommon = 1
            self.isPersonLAHSAElligibleOnly = False
            self.isPersonSPLAElligibleOnly = False
        self.countOfOccupiedDays = 0
        for k in range(7):
            if self.timeTableForWeek[k] == '1':
                self.countOfOccupiedDays += 1

    def __eq__(self, other):
        if isinstance(other, Person):
            return self.applicantId == other.applicantId
        return False

    def __str__(self):
        # print(self.countOfOccupiedDays)
        return self.applicantId + " " + self.sex + " " + self.age + " " + self.ownsPet + " " + self.medicalHealth + " " + self.ownsCar + " " + self.ownsDL + " " + self.timeTableForWeek

class Dynamic_Node:
    def __init__(self, efficiency, configuration, parentIndex):
        self.efficiency = efficiency
        self.configuration = configuration
        self.parentIndex = parentIndex

class AllocationManager:
    def __init__(self, totalApplicants, totalNumBeds, totalNumSpots, numOfApplicantChosenByLahsa,
                 numOfApplicanrChosenBySpla):
        self.totalApplicants = totalApplicants
        self.totalNumBeds = totalNumBeds # captures total number of beds
        self.totalNumSpots = totalNumSpots # captures total number of spots
        self.totalApplicant = []
        self.lahsaApplicants = []
        self.splaApplicants = []
        self.onlySplaApplicants = [] # captures list of all the LAHSA specific applicants
        self.onlylahsaApplicants = [] # captures list of all the LAHSA specific applicants
        self.leftOverSpots = []
        self.leftOverBeds = []
        self.mapOfPersons = {}
        self.commonApplicants = [] # captures list of all the common applicants
        for k in range(7):
            self.leftOverSpots.append(totalNumSpots)
        self.leftOverBeds = []
        for k in range(7):
            self.leftOverBeds.append(totalNumBeds)

    def subtractLAHSAApplicantchedule(self, listOfLAHSAApplicantToSubtract):
        for k in range(len(listOfLAHSAApplicantToSubtract)):
            applicantToSubtract = self.mapOfPersons[listOfLAHSAApplicantToSubtract[k]]
            scheduleOfApplicant = applicantToSubtract.timeTableForWeek
            for scheduleIterator in range(len(scheduleOfApplicant)):
                self.leftOverBeds[scheduleIterator] -= int(scheduleOfApplicant[scheduleIterator])
            if applicantToSubtract.isPersonEligibleForBoth:
                self.lahsaApplicants.remove(applicantToSubtract)
                self.splaApplicants.remove(applicantToSubtract)
            else:
                self.lahsaApplicants.remove(applicantToSubtract)

    def subtractSPLAApplicantchedule(self, listOfSPLAApplicantToSubtract):
        for k in range(len(listOfSPLAApplicantToSubtract)):
            applicantToSubtract = self.mapOfPersons[listOfSPLAApplicantToSubtract[k]]
            scheduleOfApplicant = applicantToSubtract.timeTableForWeek
            for scheduleIterator in range(len(scheduleOfApplicant)):
                self.leftOverSpots[scheduleIterator] -= int(scheduleOfApplicant[scheduleIterator])
            if applicantToSubtract.isPersonEligibleForBoth:
                self.lahsaApplicants.remove(applicantToSubtract)
                self.splaApplicants.remove(applicantToSubtract)
            else:
                self.splaApplicants.remove(applicantToSubtract)

    def addToApplicants(self, applicant):
        newApplicant = Person(applicant[0:5], applicant[5:6], applicant[6:9], applicant[9:10], applicant[10:11],
                              applicant[11:12], applicant[12:13], applicant[13:20])
        self.mapOfPersons[applicant[0:5]] = newApplicant
        self.totalApplicant.append(newApplicant)
        if newApplicant.isPersonEligibleForBoth:
            self.commonApplicants.append(newApplicant)
        if newApplicant.isPersonLAHSAElligible:
            self.lahsaApplicants.append(newApplicant)
        if newApplicant.isPersonSPLAElligible:
            self.splaApplicants.append(newApplicant)
        if newApplicant.isPersonLAHSAElligibleOnly:
            self.onlylahsaApplicants.append(newApplicant)
        if newApplicant.isPersonSPLAElligibleOnly:
            self.onlySplaApplicants.append(newApplicant)

    def searchNextApplicantForSPLA(self):
        # search for the next best possible choice of applicant for SPLA
        self.splaApplicants.sort(key=lambda x: x.checkForCommon, reverse=True)
        self.lahsaApplicants.sort(key=lambda x: x.checkForCommon, reverse=True)
        global answer
        if len(self.commonApplicants) != 0:
            answer = self.findMaxCommonApplicationPersonInSPLA(self.leftOverBeds, self.leftOverSpots, self.commonApplicants, self.commonApplicants, 0)
            answer = self.findMaxApplicationPersonInSPLA(self.leftOverBeds, self.leftOverSpots, self.splaApplicants, self.lahsaApplicants, 0, self.commonApplicants)
        else:
            answer = self.findMaxApplicationPersonInSPLA(self.leftOverBeds, self.leftOverSpots, self.splaApplicants, self.lahsaApplicants, 0, self.commonApplicants)
        return answer

    def findMaxApplicationPersonInSPLA(self, leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants, depth, commonApplicants):
        # find applicant which gives highest utility in SPLA
        if len(splaApplicants) == 0 or len(lahsaApplicants) == 0:
            return self.calculateEfficiencyGreedy(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        # if len(commonApplicants) == 0:
        #     if len(lahsaApplicants) != 0:
        #         vBedsSpecific = self.calculateEfficiencyIfOneOfListIsNotEmptySPLA(leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants)
        #     if len(splaApplicants) != 0:
        #         vSpotsSpecific = self.calculateEfficiencyIfOneOfListIsNotEmptyLAHSA(leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants)
        #
        #     res = self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots)
        #     if len(lahsaApplicants) != 0:
        #         vBeds = res[1] + vBedsSpecific[0]
        #     else:
        #         vBeds = res[1]
        #     if len(splaApplicants) != 0:
        #         vSpots = res[0] + vSpotsSpecific[0]
        #         chosenAction = vSpotsSpecific[1]
        #     else:
        #         vSpots = res[1]
        #         chosenAction = None
        #     chosenValue = [vSpots, vBeds]
        #     return chosenValue, chosenAction
        v = -float('inf')
        vPrevious = v
        chosenApplicant = None
        chosenConfiguration = None
        i = 0
        while i < len(splaApplicants):
            flag = False
            oneApplicant = splaApplicants[i]
            if oneApplicant in lahsaApplicants:
                indexLahsa = lahsaApplicants.index(oneApplicant)
                indexCommon = commonApplicants.index(oneApplicant)
                flag = True
            startNextApplicant = False
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    if (leftOverSpots[k] == 0):
                        startNextApplicant = True
            if startNextApplicant:
                i += 1
                continue
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverSpots[k] -= 1
            if flag:
                res = self.findMaxApplicationPersonInLAHSA(leftOverBeds, leftOverSpots, splaApplicants[:i] + splaApplicants[i + 1:], lahsaApplicants[:indexLahsa] + lahsaApplicants[indexLahsa + 1:], depth + 1, commonApplicants[:indexCommon] + commonApplicants[indexCommon + 1:])
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vSpots)
            else:
                res = self.findMaxApplicationPersonInLAHSA(leftOverBeds, leftOverSpots,
                                                           splaApplicants[:i] + splaApplicants[i + 1:], lahsaApplicants,
                                                           depth + 1, commonApplicants)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vSpots)
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverSpots[k] += 1
            if vPrevious != v:
                vPrevious = v
                chosenApplicant = oneApplicant
                chosenConfiguration = [vSpots, vBeds]
            if depth == 0:
                if chosenConfiguration[0] == vSpots:
                    if chosenApplicant.countOfOccupiedDays == oneApplicant.countOfOccupiedDays:
                        if int(chosenApplicant.applicantId) > int(oneApplicant.applicantId):
                            chosenApplicant = oneApplicant
                            chosenConfiguration = [vSpots, vBeds]
                    else:
                        if chosenApplicant.countOfOccupiedDays < oneApplicant.countOfOccupiedDays:
                            chosenApplicant = oneApplicant
                            chosenConfiguration = [vSpots, vBeds]
            i += 1
        if chosenConfiguration == None:
            if chosenApplicant == None:
                if len(lahsaApplicants) != 0:
                    return self.findMaxApplicationPersonInLAHSA(leftOverBeds, leftOverSpots, [], lahsaApplicants, depth + 1,commonApplicants)
                return self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        return chosenConfiguration, chosenApplicant

    def findMaxApplicationPersonInLAHSA(self, leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants, depth, commonApplicants):
        # find applicant which gives highest utility in LAHSA
        if len(lahsaApplicants) == 0 or len(splaApplicants) == 0:
            return self.calculateEfficiencyGreedy(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        # if len(commonApplicants) == 0:
        #     if len(lahsaApplicants) != 0:
        #         vBedsSpecific = self.calculateEfficiencyIfOneOfListIsNotEmptySPLA(leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants)
        #     if len(splaApplicants) != 0:
        #         vSpotsSpecific = self.calculateEfficiencyIfOneOfListIsNotEmptyLAHSA(leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants)
        #
        #     res = self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots)
        #     if len(lahsaApplicants) != 0:
        #         vBeds = res[1] + vBedsSpecific[0]
        #         chosenAction = vBedsSpecific[1]
        #     else:
        #         vBeds = res[1]
        #         chosenAction = None
        #     if len(splaApplicants) != 0:
        #         vSpots = res[0] + vSpotsSpecific[0]
        #
        #     else:
        #         vSpots = res[1]
        #     chosenValue = [vSpots, vBeds]
        #     return chosenValue, chosenAction
        v = -float('inf')
        vPrevious = v
        chosenApplicant = None
        chosenConfiguration = None
        i = 0
        while i < len(lahsaApplicants):
            flag = False
            oneApplicant = lahsaApplicants[i]
            if oneApplicant in splaApplicants:
                indexSpla = splaApplicants.index(oneApplicant)
                indexCommon = commonApplicants.index(oneApplicant)
                flag = True
            startNextApplicant = False
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    if (leftOverBeds[k] == 0):
                        startNextApplicant = True
            if startNextApplicant:
                i += 1
                continue
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverBeds[k] -= 1
            if flag:
                res = self.findMaxApplicationPersonInSPLA(leftOverBeds, leftOverSpots,
                                                          splaApplicants[:indexSpla] + splaApplicants[indexSpla + 1:],
                                                          lahsaApplicants[:i] + lahsaApplicants[i + 1:], depth + 1, commonApplicants[:indexCommon] + commonApplicants[indexCommon + 1:])
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vBeds)
            else:
                res = self.findMaxApplicationPersonInSPLA(leftOverBeds, leftOverSpots, splaApplicants,
                                                          lahsaApplicants[:i] + lahsaApplicants[i + 1:], depth + 1, commonApplicants)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vBeds)
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverBeds[k] += 1
            if vPrevious != v:
                vPrevious = v
                chosenApplicant = oneApplicant
                chosenConfiguration = [vSpots, vBeds]
            i += 1
        if chosenConfiguration == None:
            if chosenApplicant == None:
                if len(splaApplicants) != 0:
                    return self.findMaxApplicationPersonInSPLA(leftOverBeds, leftOverSpots, splaApplicants, [], depth + 1, commonApplicants)
                return self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        return chosenConfiguration, chosenApplicant

    def calculateEfficiency(self, succeedingLAHSAApplicants, succeedingSPLAApplicants, leftOverBeds, leftOverSpots):
        # calculates efficiency at terminal state
        sumBeds = 0
        sumSpots = 0
        res = []
        for i in range(len(leftOverBeds)):
            sumBeds += self.totalNumBeds - leftOverBeds[i]

        for i in range(len(leftOverSpots)):
            sumSpots += self.totalNumSpots - leftOverSpots[i]
        res.append(sumSpots)
        res.append(sumBeds)
        return res

    def calculateEfficiencyIfOneOfListIsNotEmptySPLA (self, leftOverBeds, leftOverSpots, succeedingSPLAApplicants, succeedingLAHSAApplicants):
        dp = self.calculateEfficiencyIfOneOfListIsNotEmptyDp(succeedingLAHSAApplicants, leftOverBeds)
        lastApplicant = dp[len(dp) - 1]
        k = len(dp) - 1
        while(lastApplicant.efficiency == 0):
            lastApplicant = dp[--k]
            if k == 0:
                break
        bestApplicant = dp[k]
        bestApplicantIndex = -1
        bestEfficiency = bestApplicant.efficiency
        while(bestApplicant.parentIndex != -1):
            bestApplicantIndex = bestApplicant.parentIndex
            bestApplicant = dp[bestApplicant.parentIndex]
        res = []
        sumBeds = bestEfficiency
        res.append(sumBeds)
        res.append(succeedingLAHSAApplicants[bestApplicantIndex])
        return res

    def calculateEfficiencyIfOneOfListIsNotEmptyLAHSA (self, leftOverBeds, leftOverSpots, succeedingSPLAApplicants, succeedingLAHSAApplicants):
        dp = self.calculateEfficiencyIfOneOfListIsNotEmptyDp(succeedingSPLAApplicants, leftOverSpots)
        lastApplicant = dp[len(dp) - 1]
        k = len(dp) - 1
        while(lastApplicant.efficiency == 0):
            k -= 1
            lastApplicant = dp[k]
            if k == 0:
                break
        bestApplicant = dp[k]
        bestApplicantIndex = -1
        bestEfficiency = bestApplicant.efficiency
        while(bestApplicant.parentIndex != -1):
            bestApplicantIndex = bestApplicant.parentIndex
            bestApplicant = dp[bestApplicant.parentIndex]
        res = []
        sumSpots= bestEfficiency
        res.append(sumSpots)
        res.append(succeedingSPLAApplicants[bestApplicantIndex])
        return res

    def calculateEfficiencyIfOneOfListIsNotEmptyDp(self, listOfApplicant, listOfRemainingThings):
        dp = []
        # efficiency, configuration, parentIndex
        valid = isValid(listOfApplicant[0], listOfRemainingThings)
        tempRemaining = copy.deepcopy(listOfRemainingThings)
        flagUpdateListOfRemainingThings = False
        if not valid:
            maxefficiency = 0
            configuration = tempRemaining
            parentIndex = -1
            efficiency = 0
        else:
            flagUpdateListOfRemainingThings = True
            efficiency = 0
            for k in range(7):
                if listOfApplicant[0].timeTableForWeek[k] == '1':
                    tempRemaining[k] -= 1
                    efficiency += 1
            maxefficiency = efficiency
            configuration = tempRemaining
            parentIndex = -1
        dp.append(Dynamic_Node(maxefficiency, configuration, parentIndex))
        for i in range(1, len(listOfApplicant)):
            tempRemaining = copy.deepcopy(listOfRemainingThings)
            flagUpdateListOfRemainingThings = False
            valid = isValid(listOfApplicant[i], tempRemaining)
            if not valid:
                maxefficiency = 0
                configuration = tempRemaining
                parentIndex = -1
            else:
                flagUpdateListOfRemainingThings = True
                efficiency = 0
                for k in range(7):
                    if listOfApplicant[i].timeTableForWeek[k] == '1':
                        tempRemaining[k] -= 1
                        efficiency += 1
                maxefficiency = efficiency
                configuration = tempRemaining
                parentIndex = -1
            nothingValid = True
            for k in range(i):
                compareApplicant = dp[i- k - 1]
                currentConfiguration = compareApplicant.configuration
                currentValid = isValid(listOfApplicant[i], currentConfiguration)
                if currentValid:
                    nothingValid = False
                    for l in range(7):
                        if listOfApplicant[i].timeTableForWeek[l] == '1':
                            currentConfiguration[l] -= 1
                    maxefficiency = compareApplicant.efficiency + efficiency
                    configuration = currentConfiguration
                    parentIndex = i- k - 1
                    break
            dp.append(Dynamic_Node(maxefficiency, configuration, parentIndex))
        return dp

    def calculateEfficiencyGreedy(self, lahsaApplicant, splaApplicant, leftOverBeds, leftOverSpots):
        # greedily calculate the efficiency at terminal state
        sumBeds = 0
        sumSpots = 0
        res = []

        remainingBeds = copy.deepcopy(leftOverBeds)
        remainingSpots = copy.deepcopy(leftOverSpots)

        lahsaApplicant.sort(key=lambda x: x.countOfOccupiedDays, reverse=True)
        splaApplicant.sort(key=lambda x: x.countOfOccupiedDays, reverse=True)

        for applicant in lahsaApplicant:
            isPossible = isValid(applicant, remainingBeds)
            if isPossible:
                for i in range(7):
                    if (applicant.timeTableForWeek[i] == '1'):
                        remainingBeds[i] -= 1

        for applicant in splaApplicant:
            isPossible = isValid(applicant, remainingSpots)
            if isPossible:
                for i in range(7):
                    if (applicant.timeTableForWeek[i] == '1'):
                        remainingSpots[i] -= 1

        for i in range(len(remainingBeds)):
            sumBeds += (self.totalNumBeds - remainingBeds[i])

        for i in range(len(remainingSpots)):
            sumSpots += (self.totalNumSpots - remainingSpots[i])

        res.append(sumSpots)
        res.append(sumBeds)
        return res
    def findMaxCommonApplicationPersonInSPLA(self, leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants, depth):
        # find the maximum common applicant from SPLA
        if len(splaApplicants) == 0 or len(lahsaApplicants) == 0:
            return self.calculateEfficiencyGreedy(self.onlylahsaApplicants, self.onlySplaApplicants, self.leftOverBeds, self.leftOverSpots), None

        v = -float('inf')
        vPrevious = v
        chosenApplicant = None
        chosenConfiguration = None
        i = 0
        while i < len(splaApplicants):
            flag = False
            oneApplicant = splaApplicants[i]
            if oneApplicant in lahsaApplicants:
                indexLahsa = lahsaApplicants.index(oneApplicant)
                flag = True
            startNextApplicant = False
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    if (leftOverSpots[k] == 0):
                        startNextApplicant = True
            if startNextApplicant:
                i += 1
                continue
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverSpots[k] -= 1
            if flag:
                res = self.findMaxCommonApplicationPersonInLAHSA(leftOverBeds, leftOverSpots, splaApplicants[:i] + splaApplicants[i + 1:], lahsaApplicants[:indexLahsa] + lahsaApplicants[indexLahsa + 1:], depth + 1)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vSpots)
            else:
                res = self.findMaxCommonApplicationPersonInLAHSA(leftOverBeds, leftOverSpots,
                                                           splaApplicants[:i] + splaApplicants[i + 1:], lahsaApplicants,
                                                           depth + 1)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vSpots)
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverSpots[k] += 1
            if vPrevious != v:
                vPrevious = v
                chosenApplicant = oneApplicant
                chosenConfiguration = [vSpots, vBeds]
            if depth == 0:
                if chosenConfiguration[0] == vSpots:
                    if int(chosenApplicant.applicantId) > int(oneApplicant.applicantId):
                        chosenApplicant = oneApplicant
                        chosenConfiguration = [vSpots, vBeds]
            i += 1
        if chosenConfiguration == None:
            if chosenApplicant == None:
                if len(lahsaApplicants) != 0:
                    return self.findMaxCommonApplicationPersonInLAHSA(leftOverBeds, leftOverSpots, [], lahsaApplicants, depth + 1)
                return self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        return chosenConfiguration, chosenApplicant

    def findMaxCommonApplicationPersonInLAHSA(self, leftOverBeds, leftOverSpots, splaApplicants, lahsaApplicants, depth):
        if len(lahsaApplicants) == 0 or len(splaApplicants) == 0:
            return self.calculateEfficiencyGreedy(self.onlylahsaApplicants, self.onlySplaApplicants, self.leftOverBeds, self.leftOverSpots), None
        v = -float('inf')
        vPrevious = v
        chosenApplicant = None
        chosenConfiguration = None
        i = 0
        while i < len(lahsaApplicants):
            flag = False
            oneApplicant = lahsaApplicants[i]
            if oneApplicant in splaApplicants:
                indexSpla = splaApplicants.index(oneApplicant)
                flag = True
            startNextApplicant = False
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    if (leftOverBeds[k] == 0):
                        startNextApplicant = True
            if startNextApplicant:
                i += 1
                continue
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverBeds[k] -= 1
            if flag:
                res = self.findMaxCommonApplicationPersonInSPLA(leftOverBeds, leftOverSpots,
                                                          splaApplicants[:indexSpla] + splaApplicants[indexSpla + 1:],
                                                          lahsaApplicants[:i] + lahsaApplicants[i + 1:], depth)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vBeds)
            else:
                res = self.findMaxCommonApplicationPersonInSPLA(leftOverBeds, leftOverSpots, splaApplicants,
                                                          lahsaApplicants[:i] + lahsaApplicants[i + 1:], depth + 1)
                vSpots = res[0][0]
                vBeds = res[0][1]
                v = max(v, vBeds)
            for k in range(7):
                if oneApplicant.timeTableForWeek[k] == '1':
                    leftOverBeds[k] += 1
            if vPrevious != v:
                vPrevious = v
                chosenApplicant = oneApplicant
                chosenConfiguration = [vSpots, vBeds]
            i += 1
        if chosenConfiguration == None:
            if chosenApplicant == None:
                if len(splaApplicants) != 0:
                    return self.findMaxCommonApplicationPersonInSPLA(leftOverBeds, leftOverSpots, splaApplicants, [], depth + 1)
                return self.calculateEfficiency(lahsaApplicants, splaApplicants, leftOverBeds, leftOverSpots), None
        return chosenConfiguration, chosenApplicant

    def printApplicants(self):
        print(self.lahsaApplicants)
        print(self.splaApplicants)
        print('Lahsa ')
        for k in range(len(self.lahsaApplicants)):
            print(self.lahsaApplicants[k])
        print('Spla ')
        for k in range(len(self.splaApplicants)):
            print(self.splaApplicants[k])
        print("common")
        for k in range(len(self.commonApplicants)):
            print(self.commonApplicants[k])
        print("spla only")
        for k in range(len(self.onlySplaApplicants)):
            print(self.onlySplaApplicants[k])
        print("lahsa only")
        for k in range(len(self.onlylahsaApplicants)):
            print(self.onlylahsaApplicants[k])
        print(self.mapOfPersons)
        print("leftOverBeds")
        print(self.leftOverBeds)
        print("leftOverSpots")
        print(self.leftOverSpots)

def isValid(oneApplicant, listOfRemainingThings):
    # return whether the particular configuration is valid or not
    for k in range(7):
        if oneApplicant.timeTableForWeek[k] == '1':
            if listOfRemainingThings[k] == 0:
                return False
    return True


def main():
    linesOfInput = tuple(open("input.txt", 'r'))
    outputFile = open('output.txt', 'w')
    linesOfInput = [l.strip() for l in linesOfInput]

    # total num of beds and spots
    totalBeds = int(linesOfInput[0])
    totalSpots = int(linesOfInput[1])

    # get the applications alloted by lahsa
    numOfApplicantChosenByLahsa = int(linesOfInput[2])
    lahsaAllocatedApplicant = []
    lahsaIterator = 3
    for k in range(numOfApplicantChosenByLahsa):
        lahsaAllocatedApplicant.append(linesOfInput[lahsaIterator])
        lahsaIterator += 1

    # get the applicants chosen by SPLA
    numOfApplicantChosenBySpla = int(linesOfInput[lahsaIterator])
    splaIterator = lahsaIterator + 1
    splaAllocatedApplicant = []
    for k in range(numOfApplicantChosenBySpla):
        splaAllocatedApplicant.append(linesOfInput[splaIterator])
        splaIterator += 1

    # get the total number of applicants
    totalApplicants = int(linesOfInput[splaIterator])
    totalApplicantsIterator = splaIterator + 1
    totalApplicantsToBeAlloted = []
    for t in range(totalApplicants):
        totalApplicantsToBeAlloted.append(linesOfInput[totalApplicantsIterator])
        totalApplicantsIterator += 1
    allocateManager = AllocationManager(totalApplicants, totalBeds, totalSpots, numOfApplicantChosenByLahsa,
                                        numOfApplicantChosenBySpla)
    for k in range(totalApplicants):
        oneApplicant = totalApplicantsToBeAlloted[k][0:5]
        allocateManager.addToApplicants(totalApplicantsToBeAlloted[k])

    allocateManager.subtractLAHSAApplicantchedule(lahsaAllocatedApplicant)
    allocateManager.subtractSPLAApplicantchedule(splaAllocatedApplicant)
    signal.signal(signal.SIGALRM, time_handler)
    signal.alarm(170)
    global answer
    result = allocateManager.searchNextApplicantForSPLA()
    outputFile.write(answer[1].applicantId)

def time_handler(signum, frame):
    outputFile = open('output.txt', 'w')
    global answer
    for k in range(len(answer)):
        print(answer[k])
    for k in range(len(answer)):
        print (answer[k])
    outputFile.write(answer[1].applicantId)
    exit()
main()