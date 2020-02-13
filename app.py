#UI bit
from kivy.app import App
from kivy.uix.button import Button

from deneb_tourn import TournamentInfo, printdbg, ResultType
import test

def callback(instance):
	tournamentInfo = TournamentInfo()
	print('The button <%s> is being pressed' % instance.text)
	test.GenerateSomeTestPlayers(tournamentInfo.players,tournamentInfo.playerInfo,test.NUM_TEST_PLAYERS,tournamentInfo)
	test.TestRun(tournamentInfo.players,tournamentInfo.actualRounds, tournamentInfo.playerInfo,tournamentInfo)

class TournApp(App):
	def build(self):
		btn1 = Button(text='Run Tests')
		btn1.bind(on_press=callback)
		return btn1

if __name__ == '__main__':
	TournApp().run()