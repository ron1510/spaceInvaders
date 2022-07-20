import pygame
import socket
import random
import math
from pygame import mixer
import time
import threading
import select
import json

#init game
pygame.init()

#connect_to_server
client = socket.socket()
client.connect(('127.0.0.1',5000))
inputs = [client]
outputs = []

#game_icon
pygame.display.set_caption("space invaders CO-OP")
game_icon = pygame.image.load('bruh.png')
pygame.display.set_icon(game_icon)

#game_menu
font = pygame.font.Font('freesansbold.ttf',32)
screen = pygame.display.set_mode((800,560))
openning_screen = pygame.image.load('openning.png')
menu_message = "Wating for conection..."
playerNum=""
menu_x = 315
menu_y = 250
screen.blit(openning_screen, (0,0))
menu = font.render(menu_message,True,(255,255,255))
screen.blit(menu ,(180,250))
pygame.display.update() #update

#load pictures
game_background = pygame.image.load('space_pic.webp')
player1 = pygame.image.load('battleship.png')
player2 = pygame.image.load('spaceship.png')
blast_1 = pygame.image.load('bullet.png')
blast_2 = pygame.image.load('bullet.png')
power1 = pygame.image.load('peircing.png')
c_p1 = pygame.image.load('cancel_p1.png')
power2 = pygame.image.load('boost.png')
c_p2 = pygame.image.load('snail.png')
power3 = pygame.image.load('love-potion.png')
c_p3 = pygame.image.load('ball-and-chain.png')
shield = pygame.image.load('shield (1).png')
enemy1 = pygame.image.load('alien.png')
enemy2 = pygame.image.load('alien.png')
enemy3 = pygame.image.load('alien.png')
enemy4 = pygame.image.load('alien.png')
enemy5 = pygame.image.load('alien.png')
enemy6 = pygame.image.load('alien.png')
enemy_dead = pygame.image.load('ufo.png')
fire = pygame.image.load('fire.png')
score_board = pygame.image.load('score.png')
heart = pygame.image.load('heart_2.png')
heart2 = pygame.image.load('heart_2.png')
heart3 = pygame.image.load('heart_2.png')
no_color = pygame.image.load('lpo.png')
bomb = pygame.image.load('missile.png')
explosion = pygame.image.load('explosion.png')

#vars:

#player1
player1_x = 304
player1_y = 480
player1_speed_x = 0
player1_speed_y = 0


#player2
player2_x = 420
player2_y = 480

#bullet
bullet_x = player1_x
bullet_y = player1_y
bullet_speed = 2
bullet_state = True
is_collide = "not collide" 
ready_to_shoot = False

#bullet_2
bullet2_x = -2500
bullet2_y = -2500
bullet2_state = False

#time
end_time=0
start_time=0
slow_on = False

#game over
game_over = False


#enemys
enemys_state = [False,False,False,False,False,False]
enemys = [enemy1,enemy2,enemy3,enemy4,enemy5,enemy6]
enemy_places_x = [0,0,0,0,0,0]
enemy_places_y = [0,0,0,0,0,0]
enemys_speed = 0.3
enemy_index = 0

#enemy_fire
fires = [fire,fire,fire,fire,fire,fire]
x_fires = [0,0,0,0,0,0]
y_fires = [0,0,0,0,0,0]
got_the_numbers = [False,False,False,False,False,False]

#power_up
power_type = [power1, power2, power3]
power_x = 0
power_y = 0
power_on_player = False
power_sent= False
unpower_up_sent = False
current_power_up = 0
rnd_type = 88

#score
game_score = 0

#health
health = [heart,heart2,heart3]
current_health = 3
health_x = 768
got_hit = False
shield_activated = False
shield_on_player = False

#cancel power up
unpower_type = [c_p1, c_p2, c_p3]
unpower_x = 0
unpower_y = 0
unpower_on_player = False
unpower_sent = False
current_unpower_up = 0

#bomba
bombs = [bomb,bomb,bomb,bomb,bomb,bomb]
bomb_x = [0,0,0,0,0,0]
bomb_y = [0,0,0,0,0,0]
explosions = [explosion,explosion,explosion,explosion,explosion,explosion]
start_time_explosion = [0,0,0,0,0,0]
end_time_explosion = 0
explosion_x = [0,0,0,0,0,0]
explosion_y = [0,0,0,0,0,0]
bomb_activated = False
bomb_hit = 0
pressed = False	
#slowenes
start_slow = 0
end_slow = 0

#function
def draw_image(x,y,image,bullet):
    screen.blit(image, (x,y))
    #if not bullet:
        #mixer.music.load('laser.wav')
        #mixer.music.play()

def write(x,y,subject):
    something = font.render(subject,True,(255,255,255))
    screen.blit(something,(x,y))

def collision(x1,y1,x2,y2,solution):
    distance = math.sqrt((math.pow(x1-x2,2))+(math.pow(y1-y2,2)))
    if distance>solution:
        return False
    else:
        return True
        
def recieve():
    data = client.recv(8)
    data = client.recv(int(data.decode())).decode()
    return data

def send_message(message,client):
    client.send(str("0"*(8-len(str(len(message))))+str(len(message))).encode())
    client.send((str(message).encode()))

def recieve_thread():
    global running
    global enemy_places_x
    global enemy_places_y
    global current_power_up
    global unpower_x
    global current_unpower_up
    global rnd_type
    global power_on_player
    global power_sent
    global power_y
    global power_x
    global unpower_y
    global player2_y
    global player2_x,playerNum
    global bullet2_x
    global bullet2_y
    global bullet_state
    global bullet2_state
    global enemys_state
    global enemy_index
    global bomb_activated
    global unpower_up_sent


    while True:
        data = recieve()
        data=json.loads(data)
        if 'start' in data:
            print("start game")
            running = data['start']
            playerNum=data['player']
        if 'type' in data:
            if data['type']=='enemy':   
                enemy_places_x = data['x']
                enemy_places_y = data['y']
                enemy_index = data['enemy_index']
                enemys_state[enemy_index] = data['enemys_state']

            elif data['type'] == 'power_up':
                power_x = data['power_x']
                current_power_up = data['current_power_up']
                rnd_type = data['rnd_type']
                
            elif data['type'] == 'unpower_up':
                unpower_x = data['unpower_up_x']
                current_power_up = data['current_unpower_up']

            elif data['type'] == "player":
                player2_x=data['x']
                player2_y=data['y']

            elif data['type'] == 'bullet':
                bullet2_x = data['x']
                bullet2_y = data['y']
                bullet2_state = data['bullet_state']

            elif data['type'] == 'bomb':
                bomb_activated = data['bomb_activated']

            elif data['type'] == 'power_up_state':
                power_sent = data['power_sent']
                power_on_player = data['power_on_player']
                power_x = data['power_up_x']
                power_y = data['power_up_y']
                current_power_up = ['current_power_up']

            elif data['type'] == 'unpower_up_state':
                unpower_up_sent = data['unpower_sent']
                power_on_player = data['power_on_player']
                unpower_x = data['unpower_up_x']
                unpower_y = data['unpower_up_y']
                current_power_up = data['current_power_up']
            
def send_player_place(player_x,player_y):
    message = {
        "type":f"player{playerNum}",
        "x":player_x,
        "y":player_y,
    }   
    message=json.dumps(message)
    send_message(message,client)


def send_bullet_info(bullet_x, bullet_y, bullet_state):
    message = {
        "type":"bullet",
        "x":bullet_x,
        "y":bullet_y,
        "bullet_state":bullet_state
    }   
    message=json.dumps(message)
    send_message(message,client)


def send_enemy_place(enemy_x,enemy_y,index,is_collide,enemys_state):
    message = {
        "type":"enemy",
        "x":enemy_x,
        "y":enemy_y,
        "enemy_index":index,
        "is_collide":is_collide,
        "enemys_state":enemys_state
    }   
    message=json.dumps(message)
    send_message(message,client) 

def send_player_condition(got_hit):
    message = {
        "type":"condition",
        "got_hit":got_hit
    }   
    message=json.dumps(message)
    send_message(message,client) 

def send_bomb_activated(bomb_activated):
    message ={
        "type":"bomb",
        "bomb_activated":bomb_activated
    }
    message=json.dumps(message)
    send_message(message,client) 

def send_power_state(power_on_player,power_sent):
    message ={
        "type":"power_state",
        "power_on_player":power_on_player,
        "power_sent":power_sent
    }
    message=json.dumps(message)
    send_message(message,client) 

#def send_if_gameover
#loop
running = False
recvThread=threading.Thread(target=recieve_thread)
recvThread.start()


run=True
while run:
    while running:
        #events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                run=False
                client.close()
        #player movement
            if event.type == pygame.KEYDOWN:
                if player1_x <= 734 and player1_x >= 0:
                    if event.key == pygame.K_a:
                        if power_on_player and rnd_type==1:
                            player1_speed_x = -1
                        elif slow_on:
                            player1_speed_x = -0.25
                        else:
                            player1_speed_x = -0.5
                    if event.key == pygame.K_d:
                        if power_on_player and rnd_type==1:
                            player1_speed_x = 1
                        elif slow_on:
                            player1_speed_x = 0.25
                        else:
                            player1_speed_x = 0.5
                else:
                    if player1_x < 0:
                        player1_x = 734
                    else:
                        player1_x = 0  
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    player1_speed_x = 0
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_w:
                    if power_on_player and rnd_type==1:
                        player1_speed_y = -1
                    elif slow_on:
                            player1_speed_y = -0.25
                    else:
                        player1_speed_y = -0.5
                if event.key ==pygame.K_s:
                    if power_on_player and rnd_type==1:
                        player1_speed_y = 1
                    elif slow_on:
                        player1_speed_y = 0.25
                    else:
                        player1_speed_y = 0.5
            if event.type == pygame.KEYUP and not game_over:
                if event.key == pygame.K_s or event.key == pygame.K_w:
                    player1_speed_y = 0

        #score        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and game_score>=10 and current_health<3 and not game_over:
                    game_score-=10
                    current_health+=1

        #bomb activation

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and game_score>=1 and bomb_activated == False:
                    game_score-= 1
                    bomb_activated = True
                    send_bomb_activated(bomb_activated)
                    pressed = True
        #suicide

            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_c and game_over == False:
                    game_score = 0
                    game_over = True
        #teleport

            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_t and player2_x > 64 and player2_x<736 and player2_y > 64 and player2_y<536 and game_score>=2:
                    game_score-=2
                    player1_x = player2_x
                    player1_y = player2_y
        #bullet fire

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and bullet_state == True:
                    bullet_state = False
                    bullet_x = player1_x + 30
                    bullet_y = player1_y - 0.1
                    ready_to_shoot = True
        #dash

            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_q and player1_x - 139 > 64 and player1_x + 139 <736 and  game_score>=5:
                    game_score-=5
                    player1_x -=75

                if event.key == pygame.K_e and player1_x - 139 > 64 and player1_x + 139 <736 and  game_score>=5:
                    game_score-=5
                    player1_x +=75

        #major_loop
            
        screen.blit(game_background, (0,0))
        screen.blit(score_board, (0,0))
        write(40,5,str (game_score))
        inc_hearts_x = 0

        for i in range (current_health):
            draw_image(768+inc_hearts_x,0,health[i],False)
            inc_hearts_x=inc_hearts_x-35

        if collision(player1_x,player1_y,power_x,power_y,False):
            shield_on_player = True
            
        if rnd_type==2 and shield_on_player:
            shield_activated = True
            
        if shield_activated:
            draw_image(663,0,shield,False)
        else: 
            draw_image(2000,123,shield,False)
        
        if got_hit:
            end_time = time.monotonic()
            if end_time-start_time>2:
                got_hit=False
        #send

        if ready_to_shoot:
            send_bullet_info(bullet_x,bullet_y,bullet_state)
        send_player_place(player1_x,player1_y)
        
        #borders
        
        if player1_y <= 0:
            player1_y = 0
        if player1_y >= 500:
            player1_y = 500
        
        #draw object
        
        for i in range (6):
            if enemys_state[i] == False:
                draw_image(enemy_places_x[i], enemy_places_y[i],enemys[i], False)
            else:
                draw_image(enemy_places_x[i], enemy_places_y[i],enemy_dead, False)

                if y_fires[i] >= 620 or not got_the_numbers[i]:
                    y_fires[i] = enemy_places_y[i] + 64
                    x_fires[i] = enemy_places_x[i] + 30
                    got_the_numbers[i] = True
                else:
                    y_fires[i] += 0.5

                draw_image(x_fires[i],y_fires[i],fires[i], False)
            enemy_places_x[i] += enemys_speed

            if enemy_places_x[i] >= 780:
                enemy_places_y[i] += 30
                enemy_places_x[i] = 0

            if collision(enemy_places_x[i],enemy_places_y[i],bullet_x,bullet_y,32):
                enemys_state[i]=True
                is_collide="collide"
                send_enemy_place(enemy_places_x,enemy_places_y,i,is_collide,enemys_state[i])
                mixer.music.load('explosion.wav')
                mixer.music.play()
                game_score+=1
                if power_on_player and rnd_type==0:
                    pass
                else:
                    bullet_state=True
                    bullet_x=3000
                    bullet_y=3000
                is_collide="not collide" 

            if collision(enemy_places_x[i],enemy_places_y[i],bullet2_x,bullet2_y,32):
                bullet2_x=3100
                bullet2_y=3100
                draw_image(3100,3100,blast_2,bullet_state)
                
            if not got_hit and collision(x_fires[i],y_fires[i],player1_x,player1_y,32):
                if shield_activated:
                    shield_activated = False
                    shield_on_player = False
                else:
                    current_health-=1
                got_hit = True
                start_time=time.monotonic()

            if not got_hit and collision(enemy_places_x[i],enemy_places_y[i],player1_x,player1_y,64):
                if shield_activated:
                    shield_activated = False
                    shield_on_player = False
                else:
                    current_health-=1
                got_hit = True
                start_time=time.monotonic()
                
            if enemy_places_y[i] >= 525:
                game_over = True

        draw_image(bullet2_x,bullet2_y,blast_2,bullet_state)

        if not got_hit:
            draw_image(player1_x,player1_y,player1,bullet_state)

        else:
            draw_image(player1_x,player1_y,no_color,bullet_state)

        draw_image(player2_x,player2_y,player2,bullet_state)

        #moving object

        player1_x += player1_speed_x
        player1_y += player1_speed_y
        
        if not bullet_state:
            draw_image(bullet_x,bullet_y,blast_1,bullet_state)
            bullet_y -= bullet_speed

        if bullet_y<=-20:
            bullet_state = True

        if current_health == 0:
            game_over = True
           
        if game_over:
            player1_x = 4000
            player1_y = 4000
            send_player_place(player1_x,player1_y)
            write(335,250,"you died")

        
        if bomb_activated:
            for i in range(6):

                bomb_x[i] = enemy_places_x[i]

                if bomb_y[i] < enemy_places_y[i]:

                    bomb_y[i] += 0.5
                    draw_image(bomb_x[i], bomb_y[i], bombs[i], False)

                elif collision(bomb_x[i],bomb_y[i],enemy_places_x[i],enemy_places_y[i],32):

                    draw_image(1001, 1001, bombs[i], False)
                    pygame.display.update()
                    start_time_explosion[i] = time.time()
                    explosion_x[i] = bomb_x[i]
                    explosion_y[i] = bomb_y[i]
                    draw_image(explosion_x[i], explosion_y[i], explosions[i], False)
                    bomb_x[i] = 1001
                    bomb_y[i] = 1001
                    enemys_state[i] = True
                    bomb_hit += 1

                    if pressed:
                        is_collide = "collide"
                        send_enemy_place(enemy_places_x,enemy_places_y,i,is_collide,enemys_state[i])
                        game_score += 1

                    is_collide = "not_collide"   

        for i in range(6):

            end_time_explosion = time.time()
            if end_time_explosion-start_time_explosion[i] < 0.2 and start_time_explosion[i] != 0:
                draw_image(explosion_x[i], explosion_y[i], explosions[i], False)

            else:
                draw_image(1000, 1000, explosions[i], False)
                start_time_explosion[i] = 0

        if bomb_hit == 6:
            bomb_activated = False
            pressed = False

            for i in range(6):
                bomb_y[i] = 0
            bomb_hit = 0

        if power_sent:
            draw_image(power_x, power_y, power_type[rnd_type], False)
        elif unpower_up_sent:
            draw_image(unpower_x, unpower_y, unpower_type[rnd_type], False)

        if not power_on_player and not power_sent and not unpower_up_sent and rnd_type==2:
            start_slow = time.monotonic()
            slow_on = True

        end_slow = time.time()
        if slow_on and end_slow-start_slow>=5:
            slow_on = False
            
        #refresh the screen
        pygame.display.update()