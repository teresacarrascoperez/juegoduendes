"""JUEGO GO monedaS"""

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random


LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (750, 625)

X=0
Y=1

STEP = 25

class Duende():
    
    def __init__(self, side):
        
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [SIZE[X] // 4, SIZE[Y] - 40]
            
        else:
            self.pos = [SIZE[X] - SIZE[X] // 4, SIZE[Y] - 40]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side
    
    def moveLeft_M(self):
        
        side = self.side
        if side == LEFT_PLAYER:
            self.pos[X] -= STEP
            if self.pos[X] < 0:
                self.pos[X] = 0
                
        else:
            self.pos[X] -= STEP
            if self.pos[X] < SIZE[X] // 2:
                self.pos[X] = SIZE[X] // 2 + 5
    
    def moveRight_M(self):
        
        side = self.side
        if side == LEFT_PLAYER:
            self.pos[X] += STEP
            if self.pos[X] >= SIZE[X] // 2:
                self.pos[X] = SIZE[X] // 2 - 5
                
        else:
            self.pos[X] += STEP
            if self.pos[X] > SIZE[X]:
                self.pos[X] = SIZE[X]  
         
    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"
    

class Moneda():
    
    def __init__(self,n):
        
        if n <= 4:             
            self.x = random.randint(1,350)
            self.y = random.randint(-200,-1)
        if n > 4:             
            self.x = random.randint(350,749)
            self.y = random.randint(-200,-1)
            
        self.pos = [self.x , self.y]
        self.vel_y = random.randint(3,5)  
        self.velocity = [0, self.vel_y] 
    
    def get_pos(self):
        return self.pos         
        
    def update(self):        
        
        self.pos[X] = self.pos[X] 
        self.pos[Y] += self.velocity[Y]   
     
    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    
    def __init__(self, manager):
        
        self.duendes= manager.list( [Duende(LEFT_PLAYER), Duende(RIGHT_PLAYER)] )
        self.monedas = manager.list( [Moneda(i) for i in range(10)] )
        self.score = manager.list( [0,0] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()

    def get_duende(self, side):
        return self.duendes[side]

    def get_moneda(self):
        for i in range(10): 
            return self.monedas[i]
    
    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        score = self.get_score()
        if score[0] >= 630 or score[1] >= 630:  
            self.running.value = 0
                    
    def finish(self):
        self.running.value = 0
        
    def moveLeft(self, mon):
        
        self.lock.acquire()
        m = self.duendes[mon]        
        m.moveLeft_M()
        self.duendes[mon] = m
        self.lock.release()
        
    def moveRight(self, mon):
        
        self.lock.acquire()
        m = self.duendes[mon]        
        m.moveRight_M()
        self.duendes[mon] = m
        self.lock.release()
    
    def sumar_left_collide(self, mon):
        
        self.lock.acquire()
        score = self.score[0]
        score += 1
        self.score[0] = score
        self.lock.release()
    
    def sumar_right_collide(self,mon):
        
        self.lock.acquire()
        score = self.score[1]
        score += 1
        self.score[1] = score
        self.lock.release()
    
    def get_info(self):
        
        pos_BAN = []
        for i in range(10):
            pos_BAN.append(self.monedas[i].get_pos())
    
        info = {
            'pos_left_player': self.duendes[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.duendes[RIGHT_PLAYER].get_pos(),
            'pos_monedas': pos_BAN,
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        return info
   
    def move_moneda(self):
        
        self.lock.acquire()
        for i in range(10):
            ban = self.monedas[i]
            ban.update()
            pos = ban.get_pos()           
            if pos[Y] >= SIZE[Y]:
                ban = Moneda(i)          
            self.monedas[i] = ban
        self.lock.release()
        
    def __str__(self):     
        return f"G<{self.duendes[RIGHT_PLAYER]}:{self.duendes[LEFT_PLAYER]}:{self.running.value}:Score:{self.score}>"

def player(side, conn, game):
    
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()                
                if command == "left":
                    game.moveLeft(side)
                elif command == "right":
                    game.moveRight(side)
                elif command == "quit":
                    game.finish()          
                elif command == "collideleft" and side == 0:
                    game.sumar_left_collide(side)                    
                elif command == "collideright"and side == 1:                   
                    game.sumar_right_collide(side)
                               
            if side == 1:
                game.move_moneda()
                if game.stop():
                    return f"GAME OVER"
            conn.send(game.get_info())
            
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
