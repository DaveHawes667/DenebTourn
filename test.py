NUM_TEST_PLAYERS = 8
TEST_ROUNDS = 3
import json
import names
import random
from tabulate import tabulate
from deneb_tourn import TournamentInfo, printdbg, ResultType

def GenerateSomeTestPlayers(players,playerInfo, numPlayers, tournamentInfo):
	while numPlayers > 0:
		tournamentInfo.RegisterPlayer(names.get_full_name())
		numPlayers-=1

def GenerateTestRoundResult(roundPairs, scoreRecordRound, tournamentInfo):	
	for pair in roundPairs:		
		bReportedResult = False
		if TournamentInfo.IsPairABye(pair):
			for side in pair:
				if side != "__BYE__":
					tournamentInfo.ReportResult(side,ResultType.BYE,0,0,scoreRecordRound)
					bReportedResult = True
		
		if not bReportedResult:
			result = random.choice(list(ResultType))
			if result == ResultType.BYE:
				result = ResultType.WIN
			sides = list(pair)
			playerAScore = random.randrange(0,5)
			if playerAScore == 0:
				playerBScore = 0
			else:
				playerBScore = random.randrange(0,playerAScore)

			if result == ResultType.WIN or result == ResultType.LOSE or result == ResultType.UNKNOWN_RESULT:				
				tournamentInfo.ReportResult(sides[0],ResultType.WIN  ,playerAScore - playerBScore,playerAScore,scoreRecordRound)
				tournamentInfo.ReportResult(sides[1],ResultType.LOSE ,playerBScore - playerAScore,playerBScore,scoreRecordRound)
			elif result == ResultType.TIMEOUT:
				tournamentInfo.ReportResult(sides[0],result,playerAScore - playerBScore,playerAScore,scoreRecordRound)
				tournamentInfo.ReportResult(sides[1],result,playerBScore - playerAScore,playerBScore,scoreRecordRound)
			else:
				print("ERROR: Invalid random result type")

	

def TestRun(players,actualRounds,playerInfo,tournamentInfo):	

	scoreRecord = tournamentInfo.scoreRecord

	#Round 1
	initialRound,scoreRecordRound = tournamentInfo.GenerateNextRound()
	printdbg("***** Round: 1",1)
	printdbg(tournamentInfo.GetVSStringForRound(initialRound),1)
	actualRounds.append(initialRound)	
	GenerateTestRoundResult(initialRound,scoreRecordRound,tournamentInfo)	
	printdbg("Recorded Results So Far:",5)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)

	#2+ rounds
	i=2
	while i<=TEST_ROUNDS:
		print("\nStandings at the end of round " + str(i-1) + "\n")
		standings = tournamentInfo.CalcStandings()		
		print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))
		nxtRound,scoreRecordRound = tournamentInfo.GenerateNextRound()
		printdbg("\n***** Round: "+str(i),1)
		printdbg(tournamentInfo.GetVSStringForRound(nxtRound),1)
		actualRounds.append(nxtRound)		
		GenerateTestRoundResult(nxtRound,scoreRecordRound,tournamentInfo)		
		printdbg("Recorded Results So Far:",5)
		printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)	
		i+=1

	#Final standings
	print("\n----------Final Standings----------\n")
	standings = tournamentInfo.CalcStandings()
	print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))