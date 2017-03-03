
import json
import random

ws = None

def sendChat(msg):
  packet = { 'c': 'chat', 'msg': msg }
  ws.send(json.dumps(packet))

def sendUserNotification(user_id, msg):
  packet = { 'c': 'notify', 'user_id': user_id, 'msg': msg }
  ws.send(json.dumps(packet))
  pass

def sendEndpointNotification(endpoint_id, msg):
  packet = { 'c': 'notify_ep', 'user_id': endpoint_id, 'msg': msg }
  ws.send(json.dumps(packet))
  pass

def changeMotd(endpoint_id, motd):
  packet = { 'c': 'motd', 'motd': motd }
  ws.send(json.dumps(packet))
  pass

def createGame(name, server_id, map, time_limit, score_limit, players):
  game_id = random.randint(0, 10000000)

  settings = { 'm_Name': name, 'm_Map': map, 'm_TimeLimit': time_limit, 'm_ScoreLimit': score_limit, 'm_PlayerLimit': len(players) }
  packet = { 'c': 'game', 'server_id': server_id, 'game_id': game_id, 'game_settings': settings, 'players': players }

  ws.send(json.dumps(packet))
  return game_id
