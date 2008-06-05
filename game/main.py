# ###################################################
# Copyright (C) 2008 The OpenAnno Team
# team@openanno.org
# This file is part of OpenAnno.
#
# OpenAnno is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import os.path
import shutil
from game.dbreader import DbReader
from game.engine import Fife
from game.settings import Settings
from game.session import Game
from game.gui.mainlistener import MainListener

def start():
	global db, settings, fife, gui, game
	#init db
	db = DbReader(':memory:')
	db("attach ? AS data", 'content/openanno.sqlite')

	#init settings
	settings = Settings()
	settings.addCategorys('sound')
	settings.sound.setDefaults(enabled = True)

	#init fife
	fife = Fife()
	fife.init()

	if settings.sound.enabled:
		fife.bgsound.play()

	mainlistener = MainListener()
	game = None
	gui = None

	showMain()

	fife.run()

def onEscape():
	pass

def showCredits():
	global fife
	fife.pychan.loadXML('content/gui/credits.xml').execute({ 'okButton' : True })

def showSettings():
	global fife, settings
	resolutions = ["640x480", "800x600", "1024x768", "1440x900"];
	try:
		resolutions.index(str(settings.fife.screen.width) + 'x' + str(settings.fife.screen.height))
	except:
		resolutions.append(str(settings.fife.screen.width) + 'x' + str(settings.fife.screen.height))
	dlg = fife.pychan.loadXML('content/gui/settings.xml')
	dlg.distributeInitialData({
		'screen_resolution' : resolutions,
		'screen_renderer' : ["OpenGL", "SDL"],
		'screen_bpp' : ["Desktop", "16", "24", "32"]
	})
	dlg.distributeData({
		'screen_resolution' : resolutions.index(str(settings.fife.screen.width) + 'x' + str(settings.fife.screen.height)),
		'screen_renderer' : 0 if settings.fife.renderer.backend == 'OpenGL' else 1,
		'screen_bpp' : int(settings.fife.screen.bpp / 10), # 0:0 16:1 24:2 32:3 :)
		'screen_fullscreen' : settings.fife.screen.fullscreen,
		'sound_enable_opt' : settings.sound.enabled
	})
	if(not dlg.execute({ 'okButton' : True, 'cancelButton' : False })):
		return;
	screen_resolution, screen_renderer, screen_bpp, screen_fullscreen, sound_enable_opt = dlg.collectData('screen_resolution', 'screen_renderer', 'screen_bpp', 'screen_fullscreen', 'sound_enable_opt')
	changes_require_restart = False
	if screen_fullscreen != settings.fife.screen.fullscreen:
		settings.fife.screen.fullscreen = screen_fullscreen
		changes_require_restart = True
	if sound_enable_opt != settings.sound.enabled:
		settings.sound.enabled = sound_enable_opt
		changes_require_restart = True
	if screen_bpp != int(settings.fife.screen.bpp / 10):
		settings.fife.screen.bpp = 0 if screen_bpp == 0 else ((screen_bpp + 1) * 8)
		changes_require_restart = True
	if screen_renderer != (0 if settings.fife.renderer.backend == 'OpenGL' else 1):
		settings.fife.renderer.backend = 'OpenGL' if screen_renderer == 0 else 'SDL'
		changes_require_restart = True
	if screen_resolution != resolutions.index(str(settings.fife.screen.width) + 'x' + str(settings.fife.screen.height)):
		settings.fife.screen.width = int(resolutions[screen_resolution].partition('x')[0])
		settings.fife.screen.height = int(resolutions[screen_resolution].partition('x')[2])
		changes_require_restart = True
	if changes_require_restart:
		fife.pychan.loadXML('content/gui/changes_require_restart.xml').execute({ 'okButton' : True})

def showQuit():
	global fife
	if(fife.pychan.loadXML('content/gui/quitgame.xml').execute({ 'okButton' : True, 'cancelButton' : False })):
		fife.quit()

def showMain():
	global gui, onEscape, showQuit, showSingle, showMulti, showSettings, showCredits
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/mainmenu.xml')
	gui.stylize('menu')
	eventMap = {
		'startSingle'  : showSingle,
		'startMulti'   : showMulti,
		'settingsLink' : showSettings,
		'creditsLink'  : showCredits,
		'closeButton'  : showQuit,
	}
	gui.mapEvents(eventMap)
	gui.show()
	onEscape = showQuit

def showSingle():
	global gui, onEscape, showMain
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/loadmap.xml')
	gui.stylize('menu')
	eventMap = {
		'okay'  : startSingle,
		'cancel'  : showMain,
	}
	gui.mapEvents(eventMap)
	gui.show()
	onEscape = showMain

def startSingle():
	global gui, fife, game, onEscape, showPause

	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/loadingscreen.xml')
	gui.stylize('menu')
	gui.show()
	fife.engine.pump()
	gui.hide()
	gui = None
	onEscape = showPause

	map = "content/maps/demo.sqlite"
	game = Game()
	game.init()
	game.loadmap(map)

def showMulti():
	global gui, onEscape, showMain
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/serverlist.xml')
	gui.stylize('menu')
	gui.show()
	onEscape = showMain

def showLobby():
	global gui, onEscape, showMulti
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/serverlobby.xml')
	gui.stylize('menu')
	gui.show()
	onEscape = showMulti

def showMultiMapSelect():
	global gui, onEscape, showLobby
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/loadmap.xml')
	gui.stylize('menu')
	gui.show()
	onEscape = showLobby

def showPause():
	global gui, onEscape, quitSession
	if gui != None:
		gui.hide()
	gui = fife.pychan.loadXML('content/gui/gamemenu.xml')
	gui.stylize('menu')
	eventMap = {
		'startGame'    : returnGame,
		'closeButton'  : quitSession,
	}
	gui.mapEvents(eventMap)
	gui.show()
	onEscape = returnGame

def returnGame():
	global gui, onEscape, showPause
	gui.hide()
	gui = None
	onEscape = showPause

def quitSession():
	global gui, fife, game
	if(fife.pychan.loadXML('content/gui/quitsession.xml').execute({ 'okButton' : True, 'cancelButton' : False })):
		gui.hide()
		gui = None
		game = None
		showMain()
