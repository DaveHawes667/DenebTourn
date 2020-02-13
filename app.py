#UI bit
from kivy.app import App
from kivy.uix.button import Button

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
					tournamentInfo.ReportResult(side,ResultType.BYE,0,scoreRecordRound)
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
				tournamentInfo.ReportResult(sides[0],ResultType.WIN,winnerScore-loserScore,scoreRecordRound)
				tournamentInfo.ReportResult(sides[1],ResultType.LOSE,loserScore - winnerScore,scoreRecordRound)
			elif result == ResultType.TIMEOUT:
				tournamentInfo.ReportResult(sides[0],result,0,scoreRecordRound)
				tournamentInfo.ReportResult(sides[1],result,0,scoreRecordRound)
			else:
				print("ERROR: Invalid random result type")

	

def TestRun(players,actualRounds,playerInfo,tournamentInfo):	

	scoreRecord = tournamentInfo.scoreRecord

	#Round 1
	initialRound = tournamentInfo.ConstructInitialRound()
	printdbg("***** Round: 1",1)
	printdbg(tournamentInfo.GetVSStringForRound(initialRound),1)
	actualRounds.append(initialRound)
	scoreRecordRound = {}
	GenerateTestRoundResult(initialRound,scoreRecordRound,tournamentInfo)
	scoreRecord.append(scoreRecordRound)
	printdbg("Recorded Results So Far:",5)
	printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)

	#2+ rounds
	i=2
	while i<=TEST_ROUNDS:
		print("\nStandings at the end of round " + str(i-1) + "\n")
		standings = tournamentInfo.CalcStandings()		
		print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))
		nxtRound = tournamentInfo.GenerateNextRound()
		printdbg("\n***** Round: "+str(i),1)
		printdbg(tournamentInfo.GetVSStringForRound(nxtRound),1)
		actualRounds.append(nxtRound)
		scoreRecordRound = {}
		GenerateTestRoundResult(nxtRound,scoreRecordRound,tournamentInfo)
		scoreRecord.append(scoreRecordRound)
		printdbg("Recorded Results So Far:",5)
		printdbg(json.dumps(scoreRecord, indent=4, sort_keys=True),5)	
		i+=1

	#Final standings
	print("\n----------Final Standings----------\n")
	standings = tournamentInfo.CalcStandings()
	print(tabulate(standings,headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]))


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

if __name__ == '__main__':
	TournApp().run()