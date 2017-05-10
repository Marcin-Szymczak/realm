import hooks
from xml.etree import ElementTree as etree
from xml.dom import minidom
import globals
import game

history = etree.Element('history')
worlds = etree.SubElement(history,"worlds")
events = etree.SubElement(history,'events')

def init():
    hooks.hook("packet_processed",packet_arrived)
    hooks.hook("client_connected",client_connected)
    hooks.hook("client_logged_in",client_logged_in)
    hooks.hook("client_disconnected", client_disconnected)
    hooks.hook("packet_successful", packet_successful)
    hooks.hook("game_initialized", save_worlds)

def save_worlds():
    for name, world in globals.worlds.items():
        worldel = etree.SubElement(worlds,"world")

        worldel.set("name",name)
        worldstr = ""
        for y in range(world.height):
            for x in range(world.width):
                worldstr += str(world.data[x+y*world.width])
            worldstr += ','
        worldel.text = worldstr

def packet_successful(client,p):
    if p.group == 'game':
        d = p.data
        if d['type'] == 'set_position':
            event = etree.SubElement(events,'player_moved')
            event.set('client_id',str(client.id))
            event.text = f"{d['x']},{d['y']}"
        if d['type'] == 'attack':
            event = etree.SubElement(events, 'attack')
            event.set('client_id', str(client.id))
            event.text = f"{d['x']},{d['y']}"

def packet_arrived(client, p):
    if p.group == 'game':
        d = p.data
        if d['type'] == 'chat':
            event = etree.SubElement(events,'chat')
            event.set("channel", d['channel'])
            if 'player_id' in d:
                event.set('player_id', d['player_id'])
            event.text = d['message']

def client_connected(client):
   event = etree.SubElement(events,"client_connected")
   event.set("id", str(client.id))

def client_logged_in(client):
   event = etree.SubElement(events,"login")
   event.set("id", str(client.id))
   event.text = client.account

def client_disconnected(client):
   event = etree.SubElement(events,"client_disconnected")
   event.set("id",str(client.id))
   event.text = client.account

def save(filename):
   data = minidom.parseString( etree.tostring(history)).toprettyxml(indent='    ')
   with open(filename,'w') as f:
      f.write(data)
