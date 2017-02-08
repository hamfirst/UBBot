
import UBBotConnection

user_name = "test"
password = "Ex7Q6tEdZF8f"


servers = []
game_id = 0

def onStart():
  print "Bot Started"

def onConnect():
  print "Bot Connected"

def onInitialSyncComplete():
  print "Initial sync complete"

def onChat(user_id, endpoint_id, user_name, message):
  print "Got chat message from " + user_name + ": " + message

  if(len(message) > 0):
    if(message == "game" and len(servers) > 0):
      game_id = UBBotConnection.createGame("Test Bot Game", servers[0], "Miniball", 1, 1, [[user_id, endpoint_id, 0]])
    elif(message[0] != '!'):
      UBBotConnection.sendChat(message)
    else:
      UBBotConnection.sendEndpointNotification(endpoint_id, message)

def onPlayerJoined(user_id, user_name, squad_tag):
  print "Player joined " + user_name

def onPlayerUpdated(user_id, user_name, squad_tag):
  print "Player updated " + user_name

def onPlayerRemoved(user_id, user_name):
  print "Player left " + user_name

def onServerJoined(server_id, server_name):
  servers.append(server_id)
  print "Server joined " + server_name

def onServerRemoved(server_id, server_name):
  servers.remove(server_id)
  print "Server left " + server_name

def onGameResult(game_id, completed, team_scores, completed_players):
  print "Got game result"

  if(completed):
    print "Game was completed"
  else:
    print "Game was not completed"

  for score in team_scores:
    print "Team score " + str(score)

  for player in completed_players:
    print "User id " + str(player['user_id'])
    print "User goals " + str(player['goals'])
    print "User assists " + str(player['assists'])

def tick():
  pass

