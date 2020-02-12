import json
import math
import random

from enum import Enum

POINTS_FOR_WIN = 3
POINTS_FOR_LOSE = 1
POINTS_FOR_TIMEOUT = 0
POINTS_FOR_BYE = POINTS_FOR_WIN

class ResultType(Enum):
	WIN = POINTS_FOR_WIN
	LOSE = POINTS_FOR_LOSE
	TIMEOUT = POINTS_FOR_TIMEOUT
	BYE = POINTS_FOR_BYE

players = ["A","B","C","D","E","F"]
#players = ["A","B","C"]

numPlayers = len(players)
evenPlayers = numPlayers % 2 == 0
pairsPerRound = math.floor(numPlayers / 2)
actualRounds = []
scoreRecord = []
dbg = True
debuglevel = 1

def GenerateTestRoundResult(roundPairs, scoreRecordRound):
	byePlayers = FindByePlayers(roundPairs)
	for pair in roundPairs:		
		bReportedResult = False
		for side in pair:
			if side == "__BYE__" or side in byePlayers:
				if side in byePlayers:
					ReportResult(side,ResultType.BYE,0,scoreRecordRound)
				bReportedResult = True
		
		if not bReportedResult:
			result = random.choice(list(ResultType))
			if result == ResultType.BYE:
				result = ResultType.WIN
			sides = list(pair)
			if result == ResultType.LOSE:
				ReportResult(sides[0],result,random.randrange(-5,0),scoreRecordRound)
				ReportResult(sides[1],ResultType.WIN,random.randrange(0,5),scoreRecordRound)
			elif result == ResultType.WIN:
				ReportResult(sides[0],result,random.randrange(0,5),scoreRecordRound)
				ReportResult(sides[1],ResultType.LOSE,random.randrange(-5,0),scoreRecordRound)
			elif result == ResultType.TIMEOUT:
				ReportResult(sides[0],result,0,scoreRecordRound)
				ReportResult(sides[1],result,0,scoreRecordRound)
			else:
				print("ERROR: Invalid random result type")
			

def TestRun(players,actualRounds):
	#Round 1
	initialRound = ConstructInitialRound(players)
	printdbg("Initial Round",1)
	printdbg(initialRound,1)
	actualRounds.append(initialRound)
	scoreRecordRound = {}
	GenerateTestRoundResult(initialRound,scoreRecordRound)
	scoreRecord.append(scoreRecordRound)
	printdbg("Recorded Results So Far:",1)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),1)

	#Round 2
	nxtRound = GenerateNextRound(players,actualRounds)
	printdbg("2nd Round",1)
	printdbg(nxtRound,1)
	actualRounds.append(nxtRound)
	scoreRecordRound = {}
	GenerateTestRoundResult(nxtRound,scoreRecordRound)
	scoreRecord.append(scoreRecordRound)
	printdbg("Recorded Results So Far:",1)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),1)

	#Round 3
	nxtRound = GenerateNextRound(players,actualRounds)
	printdbg("3rd Round",1)
	printdbg(nxtRound,1)
	actualRounds.append(nxtRound)
	scoreRecordRound = {}
	GenerateTestRoundResult(nxtRound,scoreRecordRound)
	scoreRecord.append(scoreRecordRound)
	printdbg("Recorded Results So Far:",1)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),1)

def ConstructInitialRound(players):
	initialRound = set([])
	i=0
	while len(initialRound) < pairsPerRound:
		pair = frozenset([players[i],players[i+1]])
		initialRound.add(pair)
		i+=2
	
	if not evenPlayers:
		initialRound.add(frozenset([players[numPlayers-1],"__BYE__"]))

	return frozenset(initialRound)

def ReportResult(playerId, resultType, vpDiff, scoreRecordRound):
	if playerId in scoreRecordRound:
		print("ERROR: Reporting players result twice for the same round?")
	else:
		scoreRecordRound[playerId] = {
			"points": resultType.value,
			"vpDiff": vpDiff,
		}



def FindByePlayers(round):
	byePlayers = []
	for pair in round:
		for side in pair:
			if side == "__BYE__":
				byePlayers.append(pair - frozenset("__BYE__"))
	
	return byePlayers

def EliminateSecondByes(potentialRounds, actualRounds):
	toEliminate = set([])
	
	for potential in potentialRounds:
		for actual in actualRounds:
			actualByes = set(FindByePlayers(actual))
			potentialByes = set(FindByePlayers(potential))

			if len(actualByes.intersection(potentialByes)) > 0:
				toEliminate.add(potential)
				break


			
	return list(frozenset(potentialRounds) - frozenset(toEliminate))


def GenerateNextRound(players, actualRounds):
	allPairs = FindAllPossiblePairingsForRound(players,actualRounds)
	possibleRounds = FindPotentialRounds(allPairs)
	possibleRounds = EliminateSecondByes(possibleRounds,actualRounds)

	for round in possibleRounds:
		printdbg("Potential Round...",3)
		printdbg(round,3)
	
	return possibleRounds[0]

def PairInPreviousRound(prevRounds, pair):
	for round in prevRounds:
		printdbg(round,6)
		printdbg(pair,6)
		#printdbg("intersection",6)
		#printdbg(round.intersection(frozenset([pair])),6)
		if len(round.intersection(frozenset([pair]))) > 0:
			return True
	return False

def FindAllPossiblePairingsForRound(players, actualRounds):
	allPairs = {}
	for x in players:
		candidates = list(players)
		candidates.remove(x)
		for y in candidates:
			potentialPair = frozenset([x,y])
			if not potentialPair in allPairs:
				if not PairInPreviousRound(actualRounds,potentialPair): #Don't repeat previous match-ups
					allPairs[potentialPair] = potentialPair

	printdbg("All Possible Pairs - ",5)
	for v in allPairs.values():
		printdbg(v,5)
	
	return list(allPairs.values())

def FindPotentialRounds(allPairs):
	potentialRounds = []

	def AlreadyPaired(potentialRound, newPair):
		printdbg("potential round",5)
		printdbg(potentialRound,5)
		for pair in potentialRound:
			printdbg("pair from round",5)
			printdbg(pair,5)
			printdbg("pair to consider",5)
			printdbg(newPair,5)
			venn = pair.intersection(newPair)
			if len(venn) > 0:
				return True
		return False

	def PlayersMissed(potentialRound):
		playersToFind = {}
		for player in players:
			playersToFind[player] = player

		for pair in potentialRound:
			for side in pair:
				del playersToFind[side]

		return playersToFind

	unexploredPairs = allPairs.copy()

	for i in range(len(allPairs)):
		potentialRound = set([])
		initialPair = allPairs[i]
		potentialRound.add(initialPair)
		unexploredPairs.remove(initialPair)
		for candidate in unexploredPairs:
			if len(potentialRound) < pairsPerRound:
				printdbg("Candidate...",5)
				printdbg(candidate,5)
				if not AlreadyPaired(potentialRound,candidate):
					potentialRound.add(candidate)
		
		missingPlayers = PlayersMissed(potentialRound)

		for missed in missingPlayers.values():
			potentialRound.add(frozenset([missed,"__BYE__"]))

		potentialRound = frozenset(potentialRound)
		if not potentialRound in actualRounds:
			potentialRounds.append(potentialRound)
	
	return potentialRounds

def printdbg( msg, level=1 ):
	if dbg == True and level <= debuglevel:
		print(msg)

			
TestRun(players,actualRounds)

