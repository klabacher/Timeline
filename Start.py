# -*-coding: utf-8-*-
'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Below shows examples of starting a World-Server and Login-Server
'''

'''
Basic imports : These are mandatory to import before starting any server.
'''
import Timeline
from Timeline.Server import Constants
from Timeline.Database import DBManagement as DBM
from Timeline.Server.Engine import Engine
from Timeline.Server.Penguin import Penguin
from Timeline.Utils.Events import GeneralEvent
from Timeline.Utils.Modules import ModuleHandler
from Timeline.Utils.Plugins import loadPlugins, loadPluginObjects, getPlugins, PLUGINS_LOADED

from Timeline import Handlers
from Timeline import PacketHandler
from Timeline import Plugins

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python import log

import logging
import os, sys, signal
import subprocess
import gc

'''
global -> TIMELINE_LOGGER : Defines the name of logging class used globally!
'''
Constants.TIMELINE_LOGGER = 'Timeline'

'''
InitiateLogger : This is function initiates the logger accessed all along Timeline.
@dependencies : logging
@param[name]->optional : Defines the name of the logger you are going to use all along, default - Timeline
'''


def InitiateColorLogger(name='Timeline'):
    from colorlog import ColoredFormatter

    Constants.TIMELINE_LOGGER = name
    Timeline_logger = logging.getLogger(name)

    Timeline_stream = logging.StreamHandler()

    LogFormat = "  %(reset)s%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s"
    Timeline_stream.setFormatter(ColoredFormatter(LogFormat, log_colors={
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'black,bg_red',
    }))

    Timeline_logger.addHandler(Timeline_stream)

    Timeline_logger.setLevel(logging.DEBUG)

    Timeline_logger.debug("Timeline Logger::Initiated")

    return Timeline_logger


def InitiateLogger(name="Timeline"):
    Constants.TIMELINE_LOGGER = name
    Timeline_logger = logging.getLogger(name)

    Timeline_stream = logging.StreamHandler()
    LogFormat = logging.Formatter("%(asctime)s [%(levelname)s]\t : %(message)s", "%H:%M")
    Timeline_stream.setFormatter(LogFormat)
    Timeline_logger.addHandler(Timeline_stream)

    Timeline_logger.setLevel(logging.DEBUG)

    Timeline_logger.debug("Timeline Logger::Initiated")

    return Timeline_logger


def HotLoadModule(module):
    Handler = ModuleHandler(module)
    return Handler.startLoadingModules()


def LoadPlugins(module):
    loadPlugins(module)
    plugins_loaded = map(str, PLUGINS_LOADED)
    TimelineLogger.info("Loaded %s Plugin(s) : %s", len(plugins_loaded), ', '.join(map(lambda x: x.name, getPlugins())))

    loadPluginObjects()


print \
    """
     _______
    |__   __|
       | |  #   _ _     __  ||  #  __     __  py 
       | | | | | | |  / //| || || |  |  / //|
       | | | | | | | |_||/  || || |  | |_||/
       |_| |_| | | |  \\___  || || |  |  \\__
    ----------------------------------------------
    > AS3 + AS2 CPPS Emulator. Written in Python
    > Developer : Dote
    > Version   : 7 production stable (AS2 + AS3) [Cross-compatible]
    > Updates   : [+] Complete Database overhaul
                  [+] Complete avatar support (In-game transformation)
                  [+] Language support
                  [+] Mascot messages
                  [+] Friends handler overhaul
                  [+] Mail handler overhaul
                  [+] Puffle handler overhaul
                  [+] Stamps handler overhaul
                  [+] Cache Implementation
                  [+] Game: Fire Sensei
                  [+] Game: CJ, Fire, CJ Sensei Cleanup
                  [+] Fix for round redis bug
                  [+] Automation script to identify and convert
                      old Database Structure to new one.
                      Force strict naming nomenclature.
                  [+] Logs coins history
                  [+] Event to auto-create commands, if not exists
                  [+] AS2/AS3 explicit restricted commands
                  [+] Ice-rink mess
                  [*] Thanks for patience. 
                        This includes auto-update plugin, 
                        in order to enhance and support the new
                        database overhaul. 
                        Embrace it, ^_^
    
                  [!] Redemption server
                  [!] Redemption server type, handlers
                  [!] Redemption Database
                  [!] nx-cache : First time user login and first time tutorials
                  [!] Activation expiry message
                  [!] Dynamic AS2+AS3 Engine, supports both AS2 + AS3 clients at once.
                        ! Coming soon, Patience :~)
                  [-] Bugs and Glitches
    _______________________________________________
    * Make sure to download the new version of Timeline-Signup (Register)
    script, that supports the new `line` based database structure.
    * Make sure to download the new `Avatar-line.py`, from Avatar branch, 
    so that your avatar supports the new `line` based database structure.
    """

# Example of starting the logger!
TimelineLogger = InitiateColorLogger()  # InitiateLogger()

# Checking database, databas details once set cannot be change during runtime
DBMS = DBM(user = "root", passd = "", db = "line")

if not DBMS.conn:
    sys.exit()

if not DBMS.db_data[1].endswith('line'):
    TimelineLogger.critical("Unsupported Data Structure. Timeline >= v7, explicitly forces the naming convention,\n"
                            "\t\t\t for table name to end with 'line' (eg: timeline), so as to denote the new db-structure.\n"
                            "\t\t\t Please update your Table structure to the new one, and follow the new naming convention")

    TimelineLogger.warn("You can run the Python File: DatabasePort.py,\n\t\t\t to convert all your old data to new one."
                        "\n\t\t\t And also to create db of new structure, if it doesn't exist already.")

    TimelineLogger.info("Exiting Timeline. Restart timeline to continue.")
    TimelineLogger.info("If you has any issues porting your old db, run the python file in a separate console, "
                        "or contact developer for support.")

    sys.exit(1)

# Catch unhandled deferred errors
TEObserver = log.PythonLoggingObserver(loggerName=Constants.TIMELINE_LOGGER)
TEObserver.start()

SERVERS = list()


@inlineCallbacks
def safeDestroyClients():
    TimelineLogger.warn(
        "Timeline is safely shutting down, this can take some time. Please don't interrupt or close the server, that might affect users experience on next login.")

    for engine in SERVERS:
        yield engine.connectionLost('Unknown')

    TimelineLogger.debug('Viola!')
    # reactor.callFromThread(reactor.stop)


def onExitSignal(*a):
    print 'Closing Timeline?'
    if not reactor.running:
        os._exit(1)

    reactor.callFromThread(reactor.stop)


for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
    signal.signal(sig, onExitSignal)


def main():
    global SERVERS

    # Example of initiating server to listen to given endpoint.
    '''
    LOGIN_SERVER => Initiates Engine to be a Login server
    WORLD_SERVER => Initiates Engine to be a World Server

    The type of server *must* be sent to Engine as a parameter!
    '''
    LoginServer = Engine(Penguin, Constants.LOGIN_SERVER, 1, "Login")
    Gravity = Engine(Penguin, Constants.WORLD_SERVER, 100, "Gravity")

    '''
    Example of running AS2 Server. Note the server_protocol paramater in the Engine contruction.
    '''

    AS2LoginServer = Engine(Penguin, Constants.LOGIN_SERVER, 2, "Login AS2", server_protocol=Constants.AS2_PROTOCOL)
    GravityAS2 = Engine(Penguin, Constants.WORLD_SERVER, 101, "Gravity AS2", server_protocol=Constants.AS2_PROTOCOL)

    LoginServer.run('127.0.0.1', 6112)
    AS2LoginServer.run('127.0.0.1', 6113)

    Gravity.run('127.0.0.1', 9875)
    GravityAS2.run('127.0.0.1', 9876)

    SERVERS += [LoginServer, Gravity, AS2LoginServer, GravityAS2]


LoadPlugins(Plugins)

HotLoadModule(Handlers).addCallback(lambda x: HotLoadModule(PacketHandler).addCallback(lambda x: main()))

reactor.addSystemEventTrigger('before', 'shutdown', safeDestroyClients)

reactor.run()