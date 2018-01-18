from Timeline.Server.Constants import TIMELINE_LOGGER, LOGIN_SERVER, WORLD_SERVER
from Timeline import Username, Password, Inventory
from Timeline.Utils.Events import Event, PacketEventHandler, GeneralEvent
from Timeline.Handlers.Games.CardJitsu import CJ_MATS, CardJitsuGame, CJMat
from Timeline.Handlers.Games.CardJitsu.Sensei import CardJitsuSensei, Sensei
from Timeline.Database.DB import Penguin, Ninja

from twisted.internet.defer import inlineCallbacks, returnValue

from collections import deque
import logging
from time import time

logger = logging.getLogger(TIMELINE_LOGGER)

@GeneralEvent.on('onEngine')
@inlineCallbacks
def getSensei(engine):
	if not engine.type is  WORLD_SERVER:
		returnValue(0)
	sensei = Sensei(engine)

	sensei.penguin.username = Sensei.username
	yield sensei.db_init()
	sensei.penguin.id = sensei.dbpenguin.id
	sensei.penguin.swid = sensei.dbpenguin.swid
	sensei.initialize()

	engine.sensei = sensei

@GeneralEvent.on('Room-handler')
def setCJMats(ROOM_HANDLER):
	for i in CJ_MATS:
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i] = CJMat(ROOM_HANDLER, i, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
		ROOM_HANDLER.ROOM_CONFIG.WADDLES[i].waddle = i

	logger.debug("Card Jitsu Initiated")

@PacketEventHandler.onXT('z', 'gwcj', WORLD_SERVER, p_r = False)
def handleGetWaddlingCJ(client, data):
	mat = int(data[2][0])
	ROOM_HANDLER = client.engine.roomHandler

	if mat not in ROOM_HANDLER.ROOM_CONFIG.WADDLES:
		return

	users = [str(k['id']) for k in ROOM_HANDLER.ROOM_CONFIG.WADDLES[mat]]
	client.send('%xt%gwcj%-1%'.format('%'.join(users)))

@PacketEventHandler.onXT('z', 'jsen', WORLD_SERVER, p_r = False)
def handleJoinSenseiCJ(client, data):
	ROOM_HANDLER = client.engine.roomHandler
	gameMat = CJMat(ROOM_HANDLER, 998, "JitsuMat", "Card Jitsu Mat", 3, False, False, None)
	gameMat.waddle = 998
	gameMat.game = CardJitsuSensei

	sensei = client.engine.sensei
	gameMat.append(sensei)
	gameMat.append(client)

	game = client['game']
	game.send('scard', game.ext_id, 998, 2)

	game.joinGame(sensei)

@inlineCallbacks
def checkForSensei():
	username = Sensei.username
	exists = yield Penguin.exists(where = ['username = ?', username])
	
	if not exists:
		sensei = Penguin(username = username, nickname = "Sensei", password = '', email = 'me@me.me', coins = 1000, igloos = '',
            furnitures = '', floors = '', locations = '', care = '', stamps = '', cover = '')
		yield sensei.save()
		yield sensei.refresh()

		SenseiNinja = Ninja(pid = sensei.id, belt = 10, cards = '427,99|749,99|591,99|724,99|90,99|259,99|574,99|736,99|257,99|580,99|83,99|97,99|748,99|76,99|252,99|355,99|590,99|593,99|734,99|260,99|739,99', matches = '')
		yield SenseiNinja.save()

	logger.debug('Sensei has been born!')

checkForSensei()