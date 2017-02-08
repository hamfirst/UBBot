
import websocket
import json
import sys
import UBBotInterface
import UBBotConnection
import ChangeNotifier

UBBotInterface.onStart()

try:
  UBBotConnection.ws = websocket.create_connection("ws://uniballhq.com:8002", 10) 
except:
  print "Could not connect to server"
  sys.exit()

if(UBBotConnection.ws.connected == False):
  print "Could not connect to server"
  sys.exit()

login = { 'c': 'identify', 'user_name': UBBotInterface.user_name, 'password': UBBotInterface.password }

UBBotConnection.ws.send(json.dumps(login))

frame = UBBotConnection.ws.recv_data()
data = json.loads(frame[1])

if('c' not in data or data['c'] != 'connected'):
  print "Failed to connect properly to server"
  sys.exit()

print "Connected to server"

channel_data = {}
channel_callbacks = []

server_data = {}
server_callbacks = []

def HandlePlayerJoin(idx, val):
  UBBotInterface.onPlayerJoined(val['m_UserKey'], val['m_Name'], val['m_SquadTag'])

def HandlePlayerUpdate(idx, val):
  UBBotInterface.onPlayerUpdated(val['m_UserKey'], val['m_Name'], val['m_SquadTag'])

def HandlePlayerRemove(idx):
  val = channel_data['m_Users'][idx]
  UBBotInterface.onPlayerRemoved(val['m_UserId'], val['m_Name'])

def HandlePlayerListClear():
  print "Player list cleared"

def HandleServerJoin(idx, val):
  UBBotInterface.onServerJoined(idx, val['m_Name'])

def HandleServerUpdate(idx, val):
  pass

def HandleServerRemove(idx):
  val = server_data['m_ServerList'][idx]
  UBBotInterface.onServerRemoved(idx, val['m_Name'])

def HandleServerListClear():
  print "Server list cleared"

ChangeNotifier.CreateListChangeCallback(channel_callbacks, channel_data, ".m_Users", HandlePlayerJoin, HandlePlayerUpdate, HandlePlayerRemove, HandlePlayerListClear)
ChangeNotifier.CreateListChangeCallback(server_callbacks, server_data, ".m_ServerList", HandleServerJoin, HandleServerUpdate, HandleServerRemove, HandleServerListClear)

got_channel_sync = False;
got_server_sync = False

while(True):
  try:
    frame = UBBotConnection.ws.recv_data()
    data = json.loads(frame[1])

    if(data['c'] == 'channel'):

      change = ChangeNotifier.ParseChangeNotification(data['data'])

      channel_data = ChangeNotifier.ApplyChangeNotification(change, channel_data)
      ChangeNotifier.CallChangeCallbacks(change, channel_callbacks, channel_data)
      got_channel_sync = True

    elif(data['c'] == 'server'):
      change = ChangeNotifier.ParseChangeNotification(data['data'])

      server_data = ChangeNotifier.ApplyChangeNotification(change, server_data)
      ChangeNotifier.CallChangeCallbacks(change, server_callbacks, server_data)

      got_server_sync = True

    else:
      raise RuntimeError()

    if(got_server_sync and got_channel_sync):
      break

  except Exception, e:
    print "Didn't get initial sync"
    sys.exit()

UBBotInterface.onInitialSyncComplete()

UBBotConnection.ws.settimeout(1);

while(True):
  try:
    frame = UBBotConnection.ws.recv_data();
    data = json.loads(frame[1])

    if(data['c'] == 'chat'):
      UBBotInterface.onChat(data['user_id'], data['endpoint_id'], data['user_name'], data['msg'])
    elif(data['c'] == 'game_result'):
      players = []
      for p in data['game_info']['m_ConnectedUsers']:
        player_info = { 
            'user_id': p['m_AccountId'], 
            'goals': p['m_Stats']['m_UBGoals'] + p['m_Stats']['m_DBGoals'],
            'assists': p['m_Stats']['m_UBAssists'] + p['m_Stats']['m_DBAssists'] }
        players.append(player_info)

      UBBotInterface.onGameResult(data['game_id'], data['game_info']['m_GameCompleted'], data['game_info']['m_TeamScores'], players)
    elif(data['c'] == 'channel'):
      change = ChangeNotifier.ParseChangeNotification(data['data']);

      if(change["op"] == "kRemove" or change["op"] == "kClear"):
          ChangeNotifier.CallChangeCallbacks(change, channel_callbacks, channel_data)
          channel_data = ChangeNotifier.ApplyChangeNotification(change, channel_data)
      else:
          channel_data = ChangeNotifier.ApplyChangeNotification(change, channel_data)
          ChangeNotifier.CallChangeCallbacks(change, channel_callbacks, channel_data)
    elif(data['c'] == 'server'):

      change = ChangeNotifier.ParseChangeNotification(data['data']);

      if(change["op"] == "kRemove" or change["op"] == "kClear"):
          ChangeNotifier.CallChangeCallbacks(change, server_callbacks, server_data)
          server_data = ChangeNotifier.ApplyChangeNotification(change, server_data)
      else:
          server_data = ChangeNotifier.ApplyChangeNotification(change, server_data)
          ChangeNotifier.CallChangeCallbacks(change, server_callbacks, server_data)
    
  except IOError:
    print "Disconnected from server"
    sys.exit()
  except Exception, e:
      
    UBBotInterface.tick()

