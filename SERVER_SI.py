import pygame
import socket
import random
import math
from pygame import mixer
import time
import threading
import time
import json
import select
#vars
#enemy
enemy_x=[0,0,0,0,0,0]
enemy_y=[0,0,0,0,0,0]
enemy_index=0
enemy_count=len(enemy_x)
enemy_bullet_x = [0,0,0,0,0,0]
enemy_bullet_y = [0,0,0,0,0,0]
enemys_state = False

#player1
player1_x = 1000
player1_y = 1000

#player2
player2_x = 2000
player2_y = 2000

#bullet
bullet_y = 0
bullet_x = 0
bullet_state = False

is_collide=False
#client&server

server = socket.socket()
server.bind(('',5555))
server.listen(5)

#power ups
power_up_x = 0
power_up_y = 0
power_up_type=[0,0,0]
used = False
current_power_up=0
power_on_player = False
power_sent = False

#unpower up
unpower_up_x = 0
unpower_up_y = 0
unpower_up_type=[0,0,0]
current_unpower_up=0
unpower_up_sent = False

#score
score_count = 0

#game over
is_game_over = False
#x,y,Game Over
got_hit_1=False
got_hit_2=False

#bomba
bomb_activated = False

#functions

def recieve(client):
    data = client.recv(8)
    data = client.recv(int(data.decode())).decode()
    return data

def send_message(message,client):
    client.send(str("0"*(8-len(str(len(message))))+str(len(message))).encode())
    client.send((str(message).encode()))
    
def generate_enemy_place(clients):
    global enemy_x
    global enemy_y
    for i in range(enemy_count):
        enemy_x[i]=random.randint(60, 730)
        enemy_y[i]=random.randint(20, 120)
    message = {
        "type":"enemy",
        "x":enemy_x,
        "y":enemy_y,
        "enemy_index":enemy_index,
        "enemys_state":enemys_state
    }   
    #print(message)
    message=json.dumps(message)
    SendToAll(None,clients,message)

def collision(x1,y1,x2,y2,solution):
    distance = math.sqrt((math.pow(x1-x2,2))+(math.pow(y1-y2,2)))
    if distance>solution:
        return False
    else:
        return True

def generate_power_ups(clients):
    global current_power_up
    global power_up_x
    global power_on_player
    global power_sent
    global power_up_y
    rnd_num=random.randint(0, 5000)
    if rnd_num==500:
        rnd_num = 0
        rnd_type = random.randint(0,2)
        current_power_up = rnd_type
        power_up_x  = random.randint(60, 730)
        power_up_y = 0
        power_sent = True
        message = {
            "type":"power_up",
            "power_x":power_up_x,
            "current_power_up":current_power_up,
            "rnd_type":rnd_type
        }
        message=json.dumps(message)
        SendToAll(None,clients,message)


def generate_unpower_ups(clients):
    global current_unpower_up
    global current_power_up
    global unpower_up_x
    global power_on_player
    global power_sent
    global unpower_up_sent

    unpower_up_sent = True
    if power_on_player:
        unpower_up_x  = random.randint(60, 730)
        
        message = {
            "type":"unpower_up",
            "unpower_up_x":unpower_up_x,
            "current_unpower_up":current_power_up
        }
        message=json.dumps(message)
        SendToAll(None,clients,message)
    else:
        pass
        
def SendToAll(client,clients,data):
    for i in clients:
        if i != client:
            send_message(data,i)

def recieve_message(data,client,clients):
    global player1_x
    global player1_y
    global player2_x
    global player2_y
    global bullet_x
    global enemy_x
    global enemy_y
    global bullet_y
    global enemy_index
    global is_collide
    global bullet_state
    global enemys_state
    global bomb_activated
    global power_on_player
    global power_sent
        
    data=json.loads(data)
    if 'type' in data:
        if data['type']=='player1':   
            player1_x = data['x']
            player1_y = data['y']
            data['type']="player"  

        elif data['type']=='player2':   
            player2_x = data['x']
            player2_y = data['y']
            data['type']="player"

        elif data['type']=='bullet':   
            bullet_x = data['x']
            bullet_y = data['y']
            bullet_state = ['bullet_state']
            data['type'] = 'bullet'

        elif data['type']=='enemy':   
            enemy_x = data['x']
            enemy_y = data['y']
            enemy_index = data['enemy_index']
            is_collide = data['is_collide']
            enemys_state = data['enemys_state']
            data['type'] = 'enemy'
        
        elif data['type'] == 'bomb':
            bomb_activated= data['bomb_activated']
            data['type'] = 'bomb'

        elif data['type'] == 'power_state':
            power_on_player = data['power_on_player']
            power_sent = data['power_sent']
            data['type'] = 'power_state'


    data=json.dumps(data)
    SendToAll(client,clients,data)


def send_power_up_state(clients):
    global player1_x
    global player1_y
    global player2_x
    global player2_y
    global power_up_x
    global power_up_y
    global power_on_player
    global power_sent
    global unpower_up_sent
    global current_power_up
    
    if collision(player1_x,player1_y,power_up_x,power_up_y,32) or collision(player2_x,player2_y,power_up_x,power_up_y,32):
        power_on_player = True
        power_sent = False
        power_up_x = 1000
        power_up_y = 1000 
    elif power_up_y >= 528:
        power_sent = False
        power_up_x = 1000
        power_up_y = 1000 
    else:
        power_up_y+=0.1
    message = {
        "type":"power_up_state",
        "power_sent":power_sent,
        "power_on_player":power_on_player,
        "power_up_x":power_up_x,
        "power_up_y":power_up_y,
        "current_power_up":current_power_up
    }
    message=json.dumps(message)
    SendToAll(None,clients,message)

def send_unpower_up_state(clients):
    global player1_x
    global player1_y
    global player2_x
    global player2_y
    global unpower_up_x
    global unpower_up_y
    global power_on_player
    global unpower_up_sent
    global current_power_up
    global power_sent
    if collision(player1_x,player1_y,unpower_up_x,unpower_up_y,32) or collision(player2_x,player2_y,unpower_up_x,unpower_up_y,32):
        power_on_player = False
        unpower_up_sent = False
        power_sent = False
        unpower_up_x = 1000
        unpower_up_y = 1000 
    elif unpower_up_y >= 528:
        unpower_up_x  = random.randint(60, 730)
        unpower_up_y = 0 
    else:
        unpower_up_y+=0.1
    message = {
        "type":"unpower_up_state",
        "unpower_sent":unpower_up_sent,
        "power_on_player":power_on_player,
        "unpower_up_x":unpower_up_x,
        "unpower_up_y":unpower_up_y,
        "current_power_up":current_power_up
    }
    message=json.dumps(message)
    SendToAll(None,clients,message)

def main():
    global is_collide
    MAX_MSG_LENGTH = 1024
    SERVER_PORT = 5000
    SERVER_IP = "0.0.0.0"
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print("Listening for clients...")
    client_sockets = []

    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, [], [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)
                if len(client_sockets)==2:
                    generate_enemy_place(client_sockets)     
                    data={
                        'start':True,
                        'player':1
                    }
                    time.sleep(5)
                    print("start game")
                    SendToAll(client_sockets[0],client_sockets,json.dumps(data))
                    data={
                        'start':True,
                        'player':2
                    }
                    SendToAll(client_sockets[1],client_sockets,json.dumps(data))  
            else:
                data = recieve(current_socket)
                if data == "":
                    print("Connection closed", )
                    client_sockets.remove(current_socket)
                    current_socket.close()
                else:
                    recieve_message(data,current_socket,client_sockets)
                    if is_collide=="collide":
                        enemy_x[enemy_index] = random.randint(60, 730)
                        enemy_y[enemy_index] = random.randint(20, 120)
                        message = {
                                "type":"enemy",
                                "x":enemy_x,
                                "y":enemy_y,
                                "enemy_index":enemy_index,
                                "enemys_state":enemys_state
                            }   
                        message=json.dumps(message)
                        SendToAll(None,client_sockets,message)
                    is_collide="not_collide"
                if power_sent:
                    send_power_up_state(client_sockets)
                elif unpower_up_sent:
                    send_unpower_up_state(client_sockets)
                else:
                    if power_on_player:
                        generate_unpower_ups(client_sockets)
                    else:
                        generate_power_ups(client_sockets)

main()