from __future__ import print_function

import sys
import robot_util
import json
import schedule
import platform
import subprocess
import tts.tts as tts
import watchdog

from socketIO_client import SocketIO, LoggingNamespace

if (sys.version_info > (3, 0)):
#    import _thread as thread
    import urllib.request as urllib2
else:
#    import thread
    import urllib2

controlHostPort = None
chatHostPort = None
infoServer = None
robot_id = None

appServerSocketIO = None
controlSocketIO = None
chatSocket = None
no_chat_server = None
secure_cert = None
debug_messages = None

def getControlHostPort():
    url = 'https://%s/get_control_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)

def getChatHostPort():
    url = 'https://%s/get_chat_host_port/%s' % (infoServer, robot_id)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)
    
def getOwnerDetails(username):
    url = 'https://api.letsrobot.tv/api/v1/accounts/%s' % (username)
#    url = 'https://api.letsrobot.tv/api/v1/robocasters/%s' % (username)
    response = robot_util.getWithRetry(url, secure=secure_cert).decode('utf-8')
    return json.loads(response)
    

def waitForAppServer():
    while True:
        try:
            appServerSocketIO.wait(seconds=1)
        except AttributeError:
            if debug_messages:
                print("Warning: App Server Socket not connected.");

def waitForControlServer():
    while True:
        try:
            controlSocketIO.wait(seconds=1)        
        except AttributeError:
            if debug_messages:
                print("Warning: Control Server Socket not connected.");

def waitForChatServer():
    while True:
        try:
            chatSocket.wait(seconds=1)        
        except AttributeError:
            if debug_messages:
                print("Warning: Chat Server Socket not connected.");
        
def startListenForAppServer():
#   thread.start_new_thread(waitForAppServer, ())
    watchdog.start("AppServerListen", waitForAppServer)

def startListenForControlServer():
#   thread.start_new_thread(waitForControlServer, ())
    watchdog.start("ControlServerListen", waitForControlServer)

def startListenForChatServer():
#   thread.start_new_thread(waitForChatServer, ())
    watchdog.start("ChatServerListen", waitForChatServer)


def onHandleAppServerConnect(*args):
    identifyRobotID()    
    if debug_messages:
        print
        print("app socket.io connect")
        print


def onHandleAppServerReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("app server socket.io reconnect")
        print
    
def onHandleAppServerDisconnect(*args):    
    print
    print("app server socket.io disconnect")
    print
 
def onHandleChatConnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("chat socket.io connect")
        print

def onHandleChatReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("chat socket.io reconnect")
        print
    
def onHandleChatDisconnect(*args):
    print
    print("chat socket.io disconnect")
    print

def onHandleControlConnect(*args):
    identifyRobotID()    
    if debug_messages:
        print
        print("control socket.io connect")
        print

def onHandleControlReconnect(*args):
    identifyRobotID()
    if debug_messages:
        print
        print("control socket.io reconnect")
        print
    
def onHandleControlDisconnect(*args):
    print
    print("control socket.io disconnect")
    print

def setupSocketIO(robot_config):
    global controlHostPort
    global chatHostPort
    global infoServer
    global robot_id
    global no_chat_server
    global secure_cert
    global debug_messages

    debug_messages = robot_config.getboolean('misc', 'debug_messages') 
    robot_id = robot_config.getint('robot', 'robot_id')
    infoServer = robot_config.get('misc', 'info_server')
    no_chat_server = robot_config.getboolean('misc', 'no_chat_server')
    secure_cert = robot_config.getboolean('misc', 'secure_cert')
    
    controlHostPort = getControlHostPort()
    chatHostPort = getChatHostPort()
    schedule.repeat_task(60, identifyRobot_task)
    
    if debug_messages:   
        print("using socket io to connect to control", controlHostPort)
        print("using socket io to connect to chat", chatHostPort)

    if robot_config.getboolean('misc', 'check_internet'):
        #schedule a task to check internet status
        schedule.task(robot_config.getint('misc', 'check_freq'), internetStatus_task)


def setupControlSocket(on_handle_command):
    global controlSocketIO
    if debug_messages:
        print("Connecting socket.io to control host port", controlHostPort)
    controlSocketIO = SocketIO(controlHostPort['host'], int(controlHostPort['port']), LoggingNamespace)
    print("Connected to control socket.io")
    startListenForControlServer()
    controlSocketIO.on('connect', onHandleControlConnect)
    controlSocketIO.on('reconnect', onHandleControlReconnect)    
    if debug_messages:
        controlSocketIO.on('disconnect', onHandleControlDisconnect)
    controlSocketIO.on('command_to_robot', on_handle_command)
    return controlSocketIO

def setupChatSocket(on_handle_chat_message):
    global chatSocket
    
    if not no_chat_server:
        if debug_messages:
            print('Connecting socket.io to chat host port', chatHostPort)
        chatSocket = SocketIO(chatHostPort['host'], chatHostPort['port'], LoggingNamespace)
        print("Connected to chat socket.io")
        startListenForChatServer()
        chatSocket.on('chat_message_with_name', on_handle_chat_message)
        chatSocket.on('connect', onHandleChatConnect)
        chatSocket.on('reconnect', onHandleChatReconnect)    
        if debug_messages:
            chatSocket.on('disconnect', onHandleChatDisconnect)
        return chatSocket
    else:
        print("chat server connection disabled")

def setupAppSocket(on_handle_exclusive_control):
    global appServerSocketIO
    if debug_messages:
        print("Connecting to socket.io to app server")
    appServerSocketIO = SocketIO('letsrobot.tv', 8022, LoggingNamespace)
    print("Connected to app server")
    startListenForAppServer()
    appServerSocketIO.on('exclusive_control', on_handle_exclusive_control)
    appServerSocketIO.on('connect', onHandleAppServerConnect)
    appServerSocketIO.on('reconnect', onHandleAppServerReconnect)
    if debug_messages:
        appServerSocketIO.on('disconnect', onHandleAppServerDisconnect)
    return appServerSocketIO

def sendChargeState(charging):
    chargeState = {'robot_id': robot_id, 'charging': charging}
    try:
        appServerSocketIO.emit('charge_state', chargeState)
    except AttributeError:
        if debug_messages:
            print("Error: Can't update server on charge state, no app socket")
    print("charge state:", chargeState)


def ipInfoUpdate():
    appServerSocketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]).decode('utf-8'), 'robot_id': robot_id})

def identifyRobotID():
    """tells the server which robot is using the connection"""
    if debug_messages:
        print("Sending identify robot id message")
    if not no_chat_server and not chatSocket == None:
        chatSocket.emit('identify_robot_id', robot_id);
    if not appServerSocketIO == None:
        appServerSocketIO.emit('identify_robot_id', robot_id);
   
#schedule a task to tell the server our robot it.
def identifyRobot_task():
    # tell the server what robot id is using this connection
    identifyRobotID()
    
    if platform.system() == 'Linux':
        ipInfoUpdate()
    
def isInternetConnected():
    try:
        urllib2.urlopen('https://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

lastInternetStatus = False
def internetStatus_task():
    global lastInternetStatus
    internetStatus = isInternetConnected()
    if internetStatus != lastInternetStatus:
        if internetStatus:
            tts.say("ok")
        else:
            tts.say("missing internet connection")
    lastInternetStatus = internetStatus

