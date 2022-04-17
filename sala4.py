from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random
import time

TMAX = 100000000000000000000000000000000000000000000000
SIZE = (750, 625)

X=0
Y=1

STEP = 25

class Duende():
    
    def __init__(self, number):
        self.pos =[random.randint(0,SIZE[X]),SIZE[Y] - 40] 
        self.index = number #Que cada una lleve su numero
        
    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.index
    
    def moveLeft_M(self):
        self.pos[X] -= STEP
        if self.pos[X] < 0:
            self.pos[X] = 0
     
    def moveRight_M(self):
        self.pos[X] -= STEP
        if self.pos[X] > SIZE[X]:
                self.pos[X] = SIZE[X]  
         
    def __str__(self):
        return str(self.pos)
    

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
    
    def __init__(self, manager,n_duendes):
        self.time = time.time()
        self.duendes= manager.list( [Duende(i) for i in range(n_duendes)]  )
        self.monedas = manager.list( [Moneda(i) for i in range(10)] )
        self.score = manager.list([0]*n_duendes)
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()

    def get_duende(self, s):
        return self.duendes[s]

    def get_moneda(self):
        for i in range(10): 
            return self.monedas[i]
    
    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        if time.time() - self.time > TMAX:#cuando el tiempo haya finalizado:  #mejor dicho, if todas las  mueren?
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
    
    def collide(self, i): # unse choca con la i
        self.mutex.acquire()
        score = self.score[i]
        score += 1
        self.score[i] = score
        self.mutex.release()
    def get_info(self):
        pos_BAN = []
        for i in range(10):
             pos_BAN.append(self.monedas[i].get_pos())
        info = {
            'pos_duendes': [duende.get_pos() for duende in self.duendes],
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
        
    def __str__(self):# FALTA
        return f"{self.get_info()}"




def player(side, conn, game):
    
    try:
        print(f"{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()                
                if command == "left":
                    game.moveLeft(side)
                elif command == "right":
                    game.moveRight(side)         
                elif command == "collide":
                    game.collide(i)
                elif command == "quit":
                    game.finish()
                               
            if side == 2:
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
    n_duendes = 3
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None]*n_duendes
            game = Game(manager,n_duendes)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == n_duendes:
                    for i in range(n_duendes):
                        players[i].start()
                    game = Game(manager,n_duendes)
    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
