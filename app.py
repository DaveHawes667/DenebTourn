#UI bit
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelHeader,TabbedPanelItem
from kivy.uix.popup import Popup

from deneb_tourn import TournamentInfo, printdbg, ResultType
import test

def callback(instance):
	tournamentInfo = TournamentInfo()
	print('The button <%s> is being pressed' % instance.text)
	test.GenerateSomeTestPlayers(tournamentInfo.players,tournamentInfo.playerInfo,test.NUM_TEST_PLAYERS,tournamentInfo)
	test.TestRun(tournamentInfo.players,tournamentInfo.actualRounds, tournamentInfo.playerInfo,tournamentInfo)

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
		self.tournament.RegisterPlayer(self.playerName.text)
		if self.popup != None:
			self.popup.dismiss()

class PlayersPanel(GridLayout):
	def __init__(self, tournament, **kwargs):
		super(PlayersPanel, self).__init__(**kwargs)
		self.cols = 2
		self.tournament = tournament
		registerPlayerBtn = Button(text='Register Player')
		registerPlayerBtn.bind(on_press=self.RegisterPlayer)
		self.add_widget(registerPlayerBtn)

	def RegisterPlayer(self,instance):
		popUpContent = RegisterPlayerPopUp(self.tournament)
		popup = Popup(title='Register Player', content=popUpContent, auto_dismiss=False)		
		popUpContent.popup = popup
		popup.open()

class TournamentPanelContent(GridLayout):
	def __init__(self,tournament, **kwargs):
		super(TournamentPanelContent, self).__init__(**kwargs)
		self.tournament = tournament
		self.cols = 1		
		self.tabPanel = TabbedPanel()

		#The players tab
		self.tabPanel.default_tab_text = "Players"		
		self.tabPanel.default_tab_content = PlayersPanel(self.tournament)
		self.add_widget(self.tabPanel)

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