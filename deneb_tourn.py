import json
import math
import uuid

from enum import Enum

POINTS_FOR_WIN = 3
POINTS_FOR_LOSE = 1
POINTS_FOR_TIMEOUT = 0
POINTS_FOR_BYE = POINTS_FOR_WIN

class ResultType(Enum):
	UNKNOWN_RESULT = -1
	WIN = POINTS_FOR_WIN
	LOSE = POINTS_FOR_LOSE
	TIMEOUT = POINTS_FOR_TIMEOUT
	BYE = POINTS_FOR_BYE
	

VP_DIFF_SCALE = 10.0
TP_DIFF_POWER = 2
BYE_PAIR_EFFECTIVE_SKILL_DISP = 100


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

	def GetPlayerName(self, playerId):
		return self.playerInfo[playerId]["name"]

	def RegisterPlayer(self,name):
		playerId = str(uuid.uuid4())
		self.players.append(playerId)
		self.playerInfo[playerId] = {"name":name}

		printdbg("Registered Player: " + name,1)

		self.numPlayers = len(self.players)
		self.evenPlayers = self.numPlayers % 2 == 0
		self.pairsPerRound = math.floor(self.numPlayers / 2)

	def CalcStandings(self):
		standings = {player: {"PlayerId":player,"TP":0,"VPDiff":0} for player in self.players}
		#print(standings)
		for round in self.scoreRecord:
			for player in self.players:
				if player in round:
					points = round[player]["points"]
					VPDiff = round[player]["vpDiff"]
					standings[player]["TP"]+= points
					standings[player]["VPDiff"]+= VPDiff

		standingsTable = []
		for player,standing in standings.items():
			standingsTable.append([player[:4]+"...",self.playerInfo[player]["name"],standing["TP"],standing["VPDiff"]])

		#print("Standings table " + str(standingsTable))
		standingsTable.sort( key = lambda s: (s[2],s[3]) )
		#print("Sorted Standings table " + str(standingsTable))
		standingsTable.reverse()
		return standingsTable

	def CheckResult(self, pair, scoreRound):
		bFoundResult = False

		results = {side: {"PlayerId":side,"result":ResultType.UNKNOWN_RESULT.name,"vpDiff":0,"vp":0} for side in pair}
		for side in pair:
			if side in scoreRound:
				bFoundResult = True
				results[side]["result"] = scoreRound[side]["result"]
				results[side]["vpDiff"] = scoreRound[side]["vpDiff"]
				results[side]["vp"] = scoreRound[side]["vp"]
		
		return (bFoundResult,results)


	def ConstructInitialRound(self):

		initialRound = set([])
		i=0
		while len(initialRound) < self.pairsPerRound:
			pair = frozenset([self.players[i],self.players[i+1]])
			initialRound.add(pair)
			i+=2
		
		if not self.evenPlayers:
			initialRound.add(frozenset([self.players[self.numPlayers-1],"__BYE__"]))

		return frozenset(initialRound)
	
	@staticmethod
	def IsPairABye(pair):
		for side in pair:
			if side == "__BYE__":
				return True

		return False

	def GetVSForRoundAsList(self, round):
		roundList = {}
		for pair in round:
			if TournamentInfo.IsPairABye(pair):
				for side in pair:
					if side != "__BYE__":
						roundList[pair]=self.playerInfo[side]["name"]+" got a bye this round."
			else:
				sideList = list(pair)
				roundList[pair] = self.playerInfo[sideList[0]]["name"] + " Vs. " + self.playerInfo[sideList[1]]["name"]

		return roundList

	def GetVSStringForRound(self,round):
		roundList = self.GetVSForRoundAsList(round)
		roundStr = ""
		for vs in roundList.values():
			roundStr+="\n"+vs
		
		return roundStr
		

	def CalcMaximumPairSkillDisparity(self, round, cachePairSkillDisp):
		skillDisp = []
		for pair in round:
			if not TournamentInfo.IsPairABye(pair):
				pairSkillDisp = 0
				if pair in cachePairSkillDisp:
					pairSkillDisp = cachePairSkillDisp[pair]
				else:
					pairSkillDisp = self.CalcPairSkillDisparity(pair)
					cachePairSkillDisp[pair] = pairSkillDisp

				skillDisp.append(pairSkillDisp)
			else:
				cachePairSkillDisp[pair] = BYE_PAIR_EFFECTIVE_SKILL_DISP
		
		if len(skillDisp) > 0:
			return max(skillDisp)
		else:
			return float("inf")

	def ReportResult(self, playerId, resultType, vpDiff, vp, scoreRecordRound, allowOverride = False):
		if playerId in scoreRecordRound and not allowOverride:
			print("ERROR: Reporting players result twice for the same round?")
		else:
			printdbg("Reporting result for "+str(playerId),2)
			scoreRecordRound[playerId] = {
				"result": resultType.name,
				"points": resultType.value,
				"vpDiff": vpDiff,
				"vp": vp
			}

	def FindByePlayers(self,round):
		byePlayers = []
		for pair in round:
			for side in pair:
				if side == "__BYE__":
					byePlayers.append(pair - frozenset("__BYE__"))
		
		return byePlayers

	def EliminateSecondByes(self, potentialRounds):
		toEliminate = set([])
		
		for potential in potentialRounds:
			for actual in self.actualRounds:
				actualByes = set(self.FindByePlayers(actual))
				potentialByes = set(self.FindByePlayers(potential))

				if len(actualByes.intersection(potentialByes)) > 0:
					toEliminate.add(potential)
					break


				
		return list(frozenset(potentialRounds) - frozenset(toEliminate))

	def GetActiveScoreRecordRound(self):
		return self.scoreRecord[len(self.actualRounds)-1]

	def GenerateNextRound(self):
		scoreRecordRound = {}
		self.scoreRecord.append(scoreRecordRound)

		if len(self.actualRounds) == 0:
			return (self.ConstructInitialRound(),scoreRecordRound)

		allPairs = self.FindAllPossiblePairingsForRound()
		possibleRounds = self.FindPotentialRounds(allPairs)
		possibleRounds = self.EliminateSecondByes(possibleRounds)

		for round in possibleRounds:
				printdbg("Potential Round...",3)
				printdbg(round,3)

		maxPairSkillDisp = {}
		cachePairSkillDispByPair = {}
		for round in possibleRounds:		
			maxPairSkillDisp[round] = self.CalcMaximumPairSkillDisparity(round,cachePairSkillDispByPair)
		
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
			

			smallestMaxPairRounds.sort(key = lambda round: self.CalcTotalPairSkillDisparity(round,cachePairSkillDispByPair))

			for round in smallestMaxPairRounds:
				printdbg("Small Max Pair Rounds...",3)
				printdbg(round,3)

			return (smallestMaxPairRounds[0],scoreRecordRound)

		print("ERROR: COULD NOT GENERATE A NEW ROUND!!!")
		return None
			

	def PairInPreviousRound(self, pair):
		for round in self.actualRounds:
			printdbg(round,6)
			printdbg(pair,6)
			#printdbg("intersection",6)
			#printdbg(round.intersection(frozenset([pair])),6)
			if len(round.intersection(frozenset([pair]))) > 0:
				return True
		return False

	def FindAllPossiblePairingsForRound(self):
		allPairs = {}
		for x in self.players:
			candidates = list(self.players)
			candidates.remove(x)
			for y in candidates:
				potentialPair = frozenset([x,y])
				if not potentialPair in allPairs:
					if not self.PairInPreviousRound(potentialPair): #Don't repeat previous match-ups
						allPairs[potentialPair] = potentialPair

		printdbg("All Possible Pairs - ",5)
		for v in allPairs.values():
			printdbg(v,5)
		
		return list(allPairs.values())

	def CalcPairSkillDisparity(self, pair):
		pairList = list(pair)	
		playerA = {"points":0, "vpDiff":0, "id":pairList[0]}
		playerB = playerA.copy()
		playerB["id"] = pairList[1]
		playerData = [playerA,playerB]
		
		#total up scores
		for pd in playerData:
			for scoreRecordRound in self.scoreRecord:
				if pd["id"] in scoreRecordRound:
					pd["points"]+=scoreRecordRound[pd["id"]]["points"]
					pd["vpDiff"]+=scoreRecordRound[pd["id"]]["vpDiff"]
		
		tournamentPointDiff = playerA["points"] - playerB["points"]
		tournamentVpDiff = playerA["vpDiff"] - playerB["vpDiff"]

		if tournamentPointDiff == 0:
			return tournamentVpDiff/VP_DIFF_SCALE
		else:
			return math.pow(tournamentPointDiff,TP_DIFF_POWER)

	def CalcTotalPairSkillDisparity(self,round, cachePairSkillDisp):
		printdbg(cachePairSkillDisp,4)
		totalPairSkillDisp = 0
		for pair in round:
			totalPairSkillDisp+=cachePairSkillDisp[pair]
		return totalPairSkillDisp

	def FindPotentialRounds(self, allPairs):
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
				if len(potentialRound) < self.pairsPerRound:
					printdbg("Candidate...",5)
					printdbg(candidate,5)
					if not AlreadyPaired(potentialRound,candidate):
						potentialRound.add(candidate)
			
			missingPlayers = PlayersMissed(potentialRound,self)

			for missed in missingPlayers.values():
				potentialRound.add(frozenset([missed,"__BYE__"]))

			potentialRound = frozenset(potentialRound)
			if not potentialRound in self.actualRounds:
				potentialRounds.append(potentialRound)
		
		return potentialRounds

def printdbg( msg, level=1 ):
	if dbg == True and level <= debuglevel:
		print(msg)

