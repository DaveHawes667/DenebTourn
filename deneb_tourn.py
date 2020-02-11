import json
import math

#players = ["A","B","C","D","E","F"]
players = ["A","B","C"]

numPlayers = len(players)
evenPlayers = numPlayers % 2 == 0
pairsPerRound = math.floor(numPlayers / 2)
actualRounds = []
dbg = True
debuglevel = 1

def TestRun(players,actualRounds):
	initialRound = ConstructInitialRound()
	printdbg("Initial Round",1)
	printdbg(initialRound,1)
	actualRounds.append(frozenset(initialRound))
	nxtRound = GenerateNextRound(players,actualRounds)
	printdbg("2nd Round",1)
	printdbg(nxtRound,1)
	actualRounds.append(frozenset(nxtRound))
	nxtRound = GenerateNextRound(players,actualRounds)
	printdbg("3rd Round",1)
	printdbg(nxtRound,1)
	actualRounds.append(frozenset(nxtRound))

def ConstructInitialRound():
	initialRound = set([])
	i=0
	while i < pairsPerRound:
		pair = frozenset([players[i],players[i+1]])
		initialRound.add(pair)
		i+=2
	
	if not evenPlayers:
		initialRound.add(frozenset([players[numPlayers-1],"__BYE__"]))

	return initialRound

def GenerateNextRound(players, actualRounds):
	allPairs = FindAllPossiblePairingsForRound(players,actualRounds)
	possibleRounds = FindPotentialRounds(allPairs)

	for round in possibleRounds:
		printdbg("Potential Round...",3)
		printdbg(round,3)
	
	return possibleRounds[0]

def PairInPreviousRound(prevRounds, pair):
	for round in prevRounds:
		if len(round.intersection(pair)) > 0:
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

	for v in allPairs.values():
		printdbg(v,5)
	
	return list(allPairs.values())

def FindPotentialRounds(allPairs):
	potentialRounds = []

	def AlreadyPaired(potentialRound, newPair):
		for pair in potentialRound:
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
				if not AlreadyPaired(candidate,potentialRound):
					potentialRound.add(candidate)
		
		missingPlayers = PlayersMissed(potentialRound)

		for missed in missingPlayers.values():
			potentialRound.add(frozenset([missed,"__BYE__"]))


		if not potentialRound in actualRounds:
			potentialRounds.append(potentialRound)
	
	return potentialRounds

def printdbg( msg, level=1 ):
	if dbg == True and level <= debuglevel:
		print(msg)

			
TestRun(players,actualRounds)

