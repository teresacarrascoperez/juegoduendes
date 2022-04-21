from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import time

TMAX = 1000
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

X = 0
Y = 1
SIZE = (750, 625)

FPS = 60


class Duende():
    
    def __init__(self, number):        
        self.number = number
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{self.number, self.pos}>"

class Moneda():
    
    def __init__(self,n):        
        self.pos= [None, None]
        self.divider = n

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

class Game():
    
    def __init__(self,n_duendes):
        self.duendes = [Duende(i) for i in range(n_duendes)]
        self.moneda =  [Moneda(i) for i in range(10)] 
        self.score = [0]*n_duendes
        self.time = time.time()
        self.running = True

    def get_duende(self, side):
        return self.duendes[side]

    def set_pos_duende(self, side, pos):
        self.duendes[side].set_pos(pos)

    def get_moneda(self, i): 
        return self.moneda[i]
  
    def set_pos_moneda(self,i,pos):
        self.moneda[i].set_pos(pos)
  
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        n_duendes = len(self.duendes)
        for i  in range (n_duendes):
            self.set_pos_duende(i, gameinfo['pos_duendes'][i])
        info_monedas = gameinfo['pos_monedas']
        for i in range(10):
            Moneda_i = info_monedas[i]
            self.set_pos_moneda(i,Moneda_i)
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def finish(self):
        self.running = False

    def __str__(self,n_duendes):
      for j in range(n_duendes):
        	for i in range(10):
            		return f"G<{self.duendes[j]}:{self.moneda[i]}>"

class duende_Draw(pygame.sprite.Sprite):
    
    def __init__(self,mon):
        super().__init__()
        self.duende = mon
        self.image = pygame.image.load('duende.png')
        self.image = pygame.transform.scale(self.image,(90,90))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.update()
        
    def update(self):        
        pos = self.duende.get_pos()
        self.rect.centerx, self.rect.centery = pos  
        
    def draw(self, screen):
        screen.window.blit(self.image, self.rect)
   
    def __str__(self):
        return f"S<{self.mon}>"

class moneda_Draw(pygame.sprite.Sprite):
    
    def __init__(self, mon):
        super().__init__()
        self.moneda = mon
        self.image= pygame.image.load('moneda2.png')
        self.image = pygame.transform.scale(self.image,(50,50))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.moneda.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    def draw(self,screen):
        screen.window.blit(self.image,(self.mon.pos))
       
    def __str__(self):
        return f"P<{self.mon.pos}>"
   
class Display():
    
    def __init__(self,game, n_duendes):        
        self.game = game
        self.n_duendes=n_duendes
        self.score = game.get_score()
        self.duendesD = [duende_Draw(self.game.get_duende(i)) for i in range(n_duendes)]
        self.monedaD = [moneda_Draw(self.game.get_moneda(i)) for i in range(10)]
        self.all_sprites = pygame.sprite.Group()
        self.duende_group = pygame.sprite.Group()
        self.moneda_group = pygame.sprite.Group()
        for duende in self.duendesD:
            self.all_sprites.add(duende)
            self.duende_group.add(duende)
        for moneda in self.monedaD:
            self.all_sprites.add(moneda)
            self.moneda_group.add(moneda)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('city.jpg')
        self.background = pygame.transform.scale(self.background,(750,625))
        pygame.mixer.init()
        self.sound=pygame.mixer.music.load('musica.ogg')
        self.sound=pygame.mixer.music.set_volume(0.4)
        pygame.init()
        pygame.mixer.music.play(loops=-1)
    def analyze_events(self):
        events = []        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
            elif event.type == pygame.QUIT:
                events.append("quit")       
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 20)
        for i in range(self.n_duendes):
        	text = font.render(f"Player {i}: {score[i]}", 1, WHITE)
        	self.screen.blit(text, (SIZE[X]-100, i*35))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    
    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    print ('¿Cuántos jugadores desean comenzar la partida?')
    n_duendes = int(input())
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game(n_duendes)
            i,gameinfo = conn.recv()
            print(f"I am playing number {i}")
            game.update(gameinfo)
            display = Display(game, n_duendes)
            while game.is_running():
                events = display.analyze_events()
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.finish()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)    
        

