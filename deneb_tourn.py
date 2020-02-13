import json
import math
import random
import uuid
import names

from enum import Enum
from tabulate import tabulate

POINTS_FOR_WIN = 3
POINTS_FOR_LOSE = 1
POINTS_FOR_TIMEOUT = 0
POINTS_FOR_BYE = POINTS_FOR_WIN

class ResultType(Enum):
	WIN = POINTS_FOR_WIN
	LOSE = POINTS_FOR_LOSE
	TIMEOUT = POINTS_FOR_TIMEOUT
	BYE = POINTS_FOR_BYE

VP_DIFF_SCALE = 10.0
TP_DIFF_POWER = 2
BYE_PAIR_EFFECTIVE_SKILL_DISP = 100
NUM_TEST_PLAYERS = 8
TEST_ROUNDS = 3
#players = ["A","B","C","D","E","F","G","H"]
#players = ["A","B","C"]

dbg = True
debuglevel = 1

class TournamentInfo:
	def __init__(self):
		self.players = []
		self.numPlayers = 0
		self.evenPlayers = False
		self.pairsPerRound = 0
		self.actualRounds = []
		self.scoreRecord = []
		self.playerInfo = {}

def GenerateSomeTestPlayers(players,playerInfo, numPlayers, tournamentInfo):
	while numPlayers > 0:
		RegisterPlayer(names.get_full_name(),players,playerInfo,tournamentInfo)
		numPlayers-=1

def RegisterPlayer(name,players,playerInfo, tournInfo):
	playerId = str(uuid.uuid4())
	players.append(playerId)
	playerInfo[playerId] = {"name":name}

	tournInfo.numPlayers = len(players)
	tournInfo.evenPlayers = tournInfo.numPlayers % 2 == 0
	tournInfo.pairsPerRound = math.floor(tournInfo.numPlayers / 2)

def GenerateTestRoundResult(roundPairs, scoreRecordRound):	
	for pair in roundPairs:		
		bReportedResult = False
		if IsPairABye(pair):
			for side in pair:
				if side != "__BYE__":
					ReportResult(side,ResultType.BYE,0,scoreRecordRound)
					bReportedResult = True
		
		if not bReportedResult:
			result = random.choice(list(ResultType))
			if result == ResultType.BYE:
				result = ResultType.WIN
			sides = list(pair)				
			if result == ResultType.WIN or result == ResultType.LOSE:
				winnerScore = random.randrange(0,5)
				if winnerScore == 0:
					loserScore = 0
				else:
					loserScore = random.randrange(0,winnerScore)
				ReportResult(sides[0],ResultType.WIN,winnerScore-loserScore,scoreRecordRound)
				ReportResult(sides[1],ResultType.LOSE,loserScore - winnerScore,scoreRecordRound)
			elif result == ResultType.TIMEOUT:
				ReportResult(sides[0],result,0,scoreRecordRound)
				ReportResult(sides[1],result,0,scoreRecordRound)
			else:
				print("ERROR: Invalid random result type")

def CalcStandings(scoreRecord, players, playerInfo):
	standings = {player: {"PlayerId":player,"TP":0,"VPDiff":0} for player in players}
	#print(standings)
	for round in scoreRecord:
		for player in players:
			points = round[player]["points"]
			VPDiff = round[player]["vpDiff"]
			standings[player]["TP"]+= points
			standings[player]["VPDiff"]+= VPDiff

	standingsTable = []
	for player,standing in standings.items():
		standingsTable.append([player[:4]+"...",playerInfo[player]["name"],standing["TP"],standing["VPDiff"]])

	#print("Standings table " + str(standingsTable))
	standingsTable.sort( key = lambda s: (s[2],s[3]) )
	#print("Sorted Standings table " + str(standingsTable))
	standingsTable.reverse()
	return standingsTable

def GetVSStringForRound(round,playerInfo):
	roundStr = ""
	for pair in round:
		if IsPairABye(pair):
			for side in pair:
				if side != "__BYE__":
					roundStr+="\n"+playerInfo[side]["name"]+" got a bye this round."
		else:
			sideList = list(pair)
			roundStr+="\n"+playerInfo[sideList[0]]["name"] + " Vs. " + playerInfo[sideList[1]]["name"]

	return roundStr


def TestRun(players,actualRounds,playerInfo,tournamentInfo):	

	scoreRecord = tournamentInfo.scoreRecord

	#Round 1
	initialRound = ConstructInitialRound(players,tournamentInfo)
	printdbg("***** Round: 1",1)
	printdbg(GetVSStringForRound(initialRound,playerInfo),1)
	actualRounds.append(initialRound)
	scoreRecordRound = {}
	GenerateTestRoundResult(initialRound,scoreRecordRound)
	scoreRecord.append(scoreRecordRound)
	printdbg("Recorded Results So Far:",5)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)

	#2+ rounds
	i=2
	while i<=TEST_ROUNDS:
		print("\nStandings at the end of round " + str(i-1) + "\n")
		standings = CalcStandings(scoreRecord,players,playerInfo)		
		print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))
		nxtRound = GenerateNextRound(players,actualRounds,scoreRecord,tournamentInfo)
		printdbg("\n***** Round: "+str(i),1)
		printdbg(GetVSStringForRound(nxtRound,playerInfo),1)
		actualRounds.append(nxtRound)
		scoreRecordRound = {}
		GenerateTestRoundResult(nxtRound,scoreRecordRound)
		scoreRecord.append(scoreRecordRound)
		printdbg("Recorded Results So Far:",5)
		printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)	
		i+=1

	#Final standings
	print("\n----------Final Standings----------\n")
	standings = CalcStandings(scoreRecord,players,playerInfo)		
	print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))

def ConstructInitialRound(players,tournamentInfo):

	initialRound = set([])
	i=0
	while len(initialRound) < tournamentInfo.pairsPerRound:
		pair = frozenset([players[i],players[i+1]])
		initialRound.add(pair)
		i+=2
	
	if not tournamentInfo.evenPlayers:
		initialRound.add(frozenset([players[tournamentInfo.numPlayers-1],"__BYE__"]))

	return frozenset(initialRound)

def IsPairABye(pair):
	for side in pair:
		if side == "__BYE__":
			return True

	return False

def CalcPairSkillDisparity(pair, scoreRecord):
	pairList = list(pair)	
	playerA = {"points":0, "vpDiff":0, "id":pairList[0]}
	playerB = playerA.copy()
	playerB["id"] = pairList[1]
	playerData = [playerA,playerB]
	
	#total up scores
	for pd in playerData:
		for scoreRecordRound in scoreRecord:
			if pd["id"] in scoreRecordRound:
				pd["points"]+=scoreRecordRound[pd["id"]]["points"]
				pd["vpDiff"]+=scoreRecordRound[pd["id"]]["vpDiff"]
	
	tournamentPointDiff = playerA["points"] - playerB["points"]
	tournamentVpDiff = playerA["vpDiff"] - playerB["vpDiff"]

	if tournamentPointDiff == 0:
		return tournamentVpDiff/VP_DIFF_SCALE
	else:
		return math.pow(tournamentPointDiff,TP_DIFF_POWER)

def CalcTotalPairSkillDisparity(round, cachePairSkillDisp):
	printdbg(cachePairSkillDisp,4)
	totalPairSkillDisp = 0
	for pair in round:
		totalPairSkillDisp+=cachePairSkillDisp[pair]
	return totalPairSkillDisp

def CalcMaximumPairSkillDisparity(round, scoreRecord, cachePairSkillDisp):
	skillDisp = []
	for pair in round:
		if not IsPairABye(pair):
			pairSkillDisp = 0
			if pair in cachePairSkillDisp:
				pairSkillDisp = cachePairSkillDisp[pair]
			else:
				pairSkillDisp = CalcPairSkillDisparity(pair,scoreRecord)
				cachePairSkillDisp[pair] = pairSkillDisp

			skillDisp.append(pairSkillDisp)
		else:
			cachePairSkillDisp[pair] = BYE_PAIR_EFFECTIVE_SKILL_DISP
	
	if len(skillDisp) > 0:
		return max(skillDisp)
	else:
		return float("inf")


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


def GenerateNextRound(players, actualRounds, scoreRecord,tournamentInfo):
	allPairs = FindAllPossiblePairingsForRound(players,actualRounds)
	possibleRounds = FindPotentialRounds(allPairs,tournamentInfo)
	possibleRounds = EliminateSecondByes(possibleRounds,actualRounds)

	for round in possibleRounds:
			printdbg("Potential Round...",3)
			printdbg(round,3)

	maxPairSkillDisp = {}
	cachePairSkillDispByPair = {}
	for round in possibleRounds:		
		maxPairSkillDisp[round] = CalcMaximumPairSkillDisparity(round,scoreRecord,cachePairSkillDispByPair)
	
	roundWithMinSkillDispPair = min(maxPairSkillDisp, key=maxPairSkillDisp.get)
	smallestMaxPairSkillDisp = math.ceil(maxPairSkillDisp[roundWithMinSkillDispPair])
	smallestMaxPairSkillDisp = max(1,smallestMaxPairSkillDisp)
	
	printdbg("smallestMaxPairSkillDisp",3)
	printdbg(smallestMaxPairSkillDisp,3)

	if smallestMaxPairSkillDisp < float("inf"):
		smallestMaxPairRounds = []

		for round, maxPairDisp in maxPairSkillDisp.items():
			if maxPairDisp <= smallestMaxPairSkillDisp:
				smallestMaxPairRounds.append(round)
		

		smallestMaxPairRounds.sort(key = lambda round: CalcTotalPairSkillDisparity(round,cachePairSkillDispByPair))

		for round in smallestMaxPairRounds:
			printdbg("Small Max Pair Rounds...",3)
			printdbg(round,3)

		return smallestMaxPairRounds[0]	

	print("ERROR: COULD NOT GENERATE A NEW ROUND!!!")
	return None
		

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

def FindPotentialRounds(allPairs, tournamentInfo):
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

	def PlayersMissed(potentialRound,tournamentInfo):
		playersToFind = {}
		for player in tournamentInfo.players:
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
			if len(potentialRound) < tournamentInfo.pairsPerRound:
				printdbg("Candidate...",5)
				printdbg(candidate,5)
				if not AlreadyPaired(potentialRound,candidate):
					potentialRound.add(candidate)
		
		missingPlayers = PlayersMissed(potentialRound,tournamentInfo)

		for missed in missingPlayers.values():
			potentialRound.add(frozenset([missed,"__BYE__"]))

		potentialRound = frozenset(potentialRound)
		if not potentialRound in tournamentInfo.actualRounds:
			potentialRounds.append(potentialRound)
	
	return potentialRounds

def printdbg( msg, level=1 ):
	if dbg == True and level <= debuglevel:
		print(msg)

#UI bit
from kivy.app import App
from kivy.uix.button import Button

def callback(instance):
	tournamentInfo = TournamentInfo()
	print('The button <%s> is being pressed' % instance.text)
	GenerateSomeTestPlayers(tournamentInfo.players,tournamentInfo.playerInfo,NUM_TEST_PLAYERS,tournamentInfo)
	TestRun(tournamentInfo.players,tournamentInfo.actualRounds, tournamentInfo.playerInfo,tournamentInfo)

class TournApp(App):
	def build(self):
		btn1 = Button(text='Run Tests')
		btn1.bind(on_press=callback)
		return btn1

TournApp().run()