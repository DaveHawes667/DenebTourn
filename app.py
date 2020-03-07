#UI bit
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelHeader,TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from functools import partial



from deneb_tourn import TournamentInfo, printdbg, ResultType
import test

def callback(instance):
	tournamentInfo = TournamentInfo()
	print('The button <%s> is being pressed' % instance.text)
	test.GenerateSomeTestPlayers(tournamentInfo.players,tournamentInfo.playerInfo,test.NUM_TEST_PLAYERS,tournamentInfo)
	test.TestRun(tournamentInfo.players,tournamentInfo.actualRounds, tournamentInfo.playerInfo,tournamentInfo)

class IntegerInput(TextInput):
	def insert_text(self, substring, from_undo=False):
		try: 
			x = int(substring)
			return super(IntegerInput, self).insert_text(str(x), from_undo=from_undo)
		except:
			return super(IntegerInput, self).insert_text("", from_undo=from_undo)

class IncompleteRoundPopUp(GridLayout):
	def __init__(self, tournament, unreported, scoreRound,  **kwargs):
		super(IncompleteRoundPopUp, self).__init__(**kwargs)
		self.cols = 1
		self.popup = None
		self.add_widget(Label(text='Some results not yet reported. Do you want to auto-report all as timeouts with 0VP?'))
		
		self.scoreRound = scoreRound
		self.tournament = tournament
		self.unreported = unreported

		btn1 = Button(text='Yes')
		btn1.bind(on_press=self.Done)
		self.add_widget(btn1)

		btn2 = Button(text='No')
		btn2.bind(on_press=self.Cancel)
		self.add_widget(btn2)
	
	def Cancel(self,instance):
		if self.popup != None:
			self.popup.dismiss()

	def Done(self,instance):
		for pair in self.unreported:
			pairList = list(pair)
			self.tournament.ReportResult(pairList[0],ResultType.TIMEOUT,0,0,self.scoreRound,False)
			self.tournament.ReportResult(pairList[1],ResultType.TIMEOUT,0,0,self.scoreRound,False)
		
		if self.popup != None:
			self.popup.dismiss()

class ReportResultPopUp(GridLayout):
	def __init__(self, tournament, pair, scoreRound, results,  **kwargs):
		super(ReportResultPopUp, self).__init__(**kwargs)
		self.cols = 3
		self.popup = None
		self.add_widget(Label(text='Player'))
		self.add_widget(Label(text='Result'))
		self.add_widget(Label(text='VP'))		
		self.pair = pair
		self.pairList = list(pair)

		if results[self.pairList[0]]["result"] == ResultType.UNKNOWN_RESULT.name:
			self.oldResults = {side: {"PlayerId":side,"result":ResultType.WIN.name,"vpDiff":0, "vp":0} for side in pair}
		else:
			self.oldResults = results
		
		self.scoreRound = scoreRound
		self.add_widget(Label(text=tournament.GetPlayerName(self.pairList[0])))
		self.spinner = Spinner(
			# default value shown
			text=self.oldResults[self.pairList[0]]["result"],
			# available values
			values=(ResultType.LOSE.name,ResultType.WIN.name,ResultType.TIMEOUT.name),
			)
		self.spinner.bind(text=self.OnResultChange)
		self.add_widget(self.spinner)
		self.playerAVP = IntegerInput(multiline=False,text=str(self.oldResults[self.pairList[0]]["vp"]))
		self.add_widget(self.playerAVP)

		self.add_widget(Label(text=tournament.GetPlayerName(self.pairList[1])))
		self.playerBResult = Label(text=self.GetResultType()[1].name)
		self.add_widget(self.playerBResult)
		self.playerBVP = IntegerInput(multiline=False,text=str(self.oldResults[self.pairList[1]]["vp"]))
		self.add_widget(self.playerBVP)
		
		self.tournament = tournament
		btn1 = Button(text='Done')
		btn1.bind(on_press=self.Done)
		self.add_widget(btn1)
	
	def OnResultChange(self, spinner, text):
		self.playerBResult.text = self.GetResultType()[1].name

	def GetResultType(self):
		result = [ResultType[self.spinner.text]]
		if result[0] == ResultType.WIN:
			result.append(ResultType.LOSE)
		elif result[0] == ResultType.LOSE:
			result.append(ResultType.WIN)
		elif result[0] == ResultType.TIMEOUT:
			result.append(ResultType.TIMEOUT)
		else:
			printdbg("ERROR: Wrong kind of result type?",1)
		
		return result


	def Done(self,instance):
		result = self.GetResultType()
		vpa = int(self.playerAVP.text)
		vpb = int(self.playerBVP.text)

		vpDiffA = vpa - vpb
		vpDiffB = vpb - vpa

		self.tournament.ReportResult(self.pairList[0],result[0],vpDiffA,vpa,self.scoreRound,True)
		self.tournament.ReportResult(self.pairList[1],result[1],vpDiffB,vpb,self.scoreRound,True)
		if self.popup != None:
			self.popup.dismiss()

class RegisterPlayerPopUp(GridLayout):
	def __init__(self, tournament, **kwargs):
		super(RegisterPlayerPopUp, self).__init__(**kwargs)
		self.cols = 1
		self.popup = None
		self.add_widget(Label(text='Player Name'))
		self.playerName = TextInput(multiline=False)
		self.add_widget(self.playerName)
		self.tournament = tournament
		btn1 = Button(text='Done')
		btn1.bind(on_press=self.Done)
		self.add_widget(btn1)

	def Done(self,instance):
		if len(self.playerName.text) > 0:
			self.tournament.RegisterPlayer(self.playerName.text)
		if self.popup != None:
			self.popup.dismiss()

class PlayerListView(GridLayout):
	def __init__(self, tournament, **kwargs):
		super(PlayerListView, self).__init__(**kwargs)
		self.tournament = tournament
		self.Refresh()
		
	def Refresh(self):
		self.clear_widgets()
		self.rows = len(self.tournament.players)
		for player in self.tournament.players:
			self.add_widget(Label(text=self.tournament.GetPlayerName(player)))

class PlayersPanel(GridLayout):
	def __init__(self, tournament, tournamentPanel, **kwargs):
		super(PlayersPanel, self).__init__(**kwargs)
		self.cols = 3
		self.tournament = tournament
		self.tournamentPanel = tournamentPanel
		registerPlayerBtn = Button(text='Register Player')
		registerPlayerBtn.bind(on_press=self.RegisterPlayer)
		self.add_widget(registerPlayerBtn)
		self.playerListView = PlayerListView(self.tournament)
		self.add_widget(self.playerListView)
		startFirstRoundBtn = Button(text='Start First Round')
		startFirstRoundBtn.bind(on_press=self.StartFirstRound)
		self.add_widget(startFirstRoundBtn)
	
	def StartFirstRound(self,instance):
		if len(self.tournament.actualRounds) == 0:
			self.tournamentPanel.AddRoundPanel()


	def RefreshPlayerList(self,instance):
		self.playerListView.Refresh()

	def RegisterPlayer(self,instance):
		popUpContent = RegisterPlayerPopUp(self.tournament)
		popup = Popup(title='Register Player', content=popUpContent, auto_dismiss=False)		
		popUpContent.popup = popup
		popup.bind(on_dismiss=self.RefreshPlayerList)
		popup.open()

class RoundPanel(GridLayout):
	def __init__(self,tournament, tournamentPanel, **kwargs):
		super(RoundPanel, self).__init__(**kwargs)
		self.tournament = tournament	
		self.tournamentPanel = tournamentPanel	
		self.roundList = None
	
	def GenerateRound(self):		
		self.round,self.scoreRound = self.tournament.GenerateNextRound()
		self.tournament.actualRounds.append(self.round)		
		self.roundList = self.tournament.GetVSForRoundAsList(self.round)
		self.cols = 1
		self.GenerateContent(False)

	def GenerateActiveRoundDisplay(self):
		for pair,vs in self.roundList.items():			
			vsGrid = GridLayout(cols=3)
			vsGrid.add_widget(Label(text = vs))
			if TournamentInfo.IsPairABye(pair):
				vsGrid.add_widget(Label(text = "No report needed"))
				vsGrid.add_widget(Label(text="N/A"))
			else:
				bFoundResult, results = self.tournament.CheckResult(pair,self.scoreRound)
				btn = Button(text = "Edit Result" if bFoundResult else "Report Result")				
				btn.bind(on_press=self.ReportResult)
				btn.results = results
				btn.pair = pair
				btn.scoreRound = self.scoreRound
				vsGrid.add_widget(btn)

				resultStr = "result TBC"
				if bFoundResult:
					resultStr = ""
					for playerId,result in results.items():
						playerName = self.tournament.GetPlayerName(playerId)
						resultStr += playerName + " " + result["result"] + " VP Diff: " + str(result["vpDiff"]) + "\n"

				vsGrid.add_widget(Label(text=resultStr))
			self.add_widget(vsGrid)

		btn = Button(text = "Close Round")
		btn.bind(on_press=self.CloseRound)		
		self.add_widget(btn)

	def GenerateStandingsDisplay(self):
		standings = self.tournament.CalcStandings()

		headers=["PlayerId","Player Name","Tournament Points", "VP Diff"]
		vsGrid = GridLayout(cols=len(headers))

		for header in headers:
			vsGrid.add_widget(Label(text = header))

		for player in standings:
			for entry in player:
				vsGrid.add_widget(Label(text = str(entry)))


		self.add_widget(vsGrid)

	def GenerateContent(self, bShowStandings):		
		self.clear_widgets()

		if bShowStandings:
			self.GenerateStandingsDisplay()
		else:
			self.GenerateActiveRoundDisplay()

	def CloseRound(self,instance):
		unreported = self.tournament.UnreportedResultsForActiveRound()
		
		if len(unreported)==0:
			#none unreported so we can end the round
			self.GenerateContent(True)
			self.tournamentPanel.AddRoundPanel()
		else: #some unreported so we need to pop-up and warn
			self.WarnIncompleteRound(unreported)

	def RefreshReportedResults(self,instance):
		self.GenerateContent(False)

	def WarnIncompleteRound(self, unreported):
		popUpContent = IncompleteRoundPopUp(self.tournament, unreported, self.scoreRound)
		popup = Popup(title='WARNING: Round Incomplete', content=popUpContent, auto_dismiss=False)		
		popUpContent.popup = popup
		popup.bind(on_dismiss=self.RefreshReportedResults)
		popup.open()

	def ReportResult(self, instance):
		popUpContent = ReportResultPopUp(self.tournament,instance.pair,instance.scoreRound, instance.results)
		popup = Popup(title='Report Result', content=popUpContent, auto_dismiss=False)		
		popUpContent.popup = popup
		popup.bind(on_dismiss=self.RefreshReportedResults)
		popup.open()

class TournamentPanelContent(GridLayout):
	def __init__(self,tournament, **kwargs):
		super(TournamentPanelContent, self).__init__(**kwargs)
		self.tournament = tournament
		self.cols = 1
		self.tabPanel = TabbedPanel()

		#The players tab
		self.tabPanel.default_tab_text = "Players"		
		self.tabPanel.default_tab_content = PlayersPanel(self.tournament,self)
		self.add_widget(self.tabPanel)
	
	def AddRoundPanel(self):
		roundPanel = RoundPanel(self.tournament,self)
		roundPanel.GenerateRound()
		tp = TabbedPanelItem()
		tp.text = "Round " + str(len(self.tournament.actualRounds))
		tp.add_widget(roundPanel)
		self.tabPanel.add_widget(tp)

class Tournaments(GridLayout):
	def __init__(self, **kwargs):
		super(Tournaments, self).__init__(**kwargs)
		self.tournaments = []
		self.cols = 1		
		self.tabPanel = TabbedPanel()
		self.tabPanel.default_tab_text = "Home"
		newTournamentBtn = Button(text='Create New Tournament')
		newTournamentBtn.bind(on_press=self.CreateNewTournament)		
		self.tabPanel.default_tab_content = newTournamentBtn

		tp = TabbedPanelItem()
		tp.text = "Tests!!"		
		runTestsBtn = Button(text='Run Tests')
		runTestsBtn.bind(on_press=callback)
		tp.add_widget(runTestsBtn)
		self.tabPanel.add_widget(tp)

		self.add_widget(self.tabPanel)
	
	def CreateNewTournament(self,instance):
		newTourn = TournamentInfo()
		self.tournaments.append(newTourn)

		tp = TabbedPanelItem()
		tp.text = "Tournament"
		tp.add_widget(TournamentPanelContent(newTourn))
		self.tabPanel.add_widget(tp)		

class TournApp(App):	
	def build(self):		
		return Tournaments()

if __name__ == '__main__':
	TournApp().run()