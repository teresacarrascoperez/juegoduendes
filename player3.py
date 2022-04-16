"""JUEGO GO monedaS"""

from multiprocessing.connection import Client
import traceback
import pygame
import sys, os


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

X = 0
Y = 1
SIZE = (750, 625)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1


FPS = 60


SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Duende():
    
    def __init__(self, side):        
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

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
    
    def __init__(self):
        self.duendes = [Duende(i) for i in range(2)]
        self.moneda =  [Moneda(i) for i in range(10)] 
        self.score = [0,0]
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
        self.set_pos_duende(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_duende(RIGHT_PLAYER, gameinfo['pos_right_player'])
        info_ban = gameinfo['pos_monedas']
        for i in range(10):
            Ban_i = info_ban[i]
            self.set_pos_moneda(i,Ban_i)
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def finish(self):
        self.running = False

    def __str__(self):
        for i in range(10):
            return f"G<{self.duendes[RIGHT_PLAYER]}:{self.duendes[LEFT_PLAYER]}:{self.moneda[i]}>"

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
    
    def __init__(self, ban):
        super().__init__()
        self.moneda = ban
        self.image= pygame.image.load('moneda2.png')
        self.image = pygame.transform.scale(self.image,(50,50))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.moneda.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    def draw(self,screen):
        screen.window.blit(self.image,(self.ball.pos))
       
    def __str__(self):
        return f"P<{self.ban.pos}>"
   
class Display():
    
    def __init__(self, game):        
        self.game = game
        self.score = game.get_score()
        self.duendesD = [duende_Draw(self.game.get_duende(i)) for i in range(2)]
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
        pygame.init()
     
    def analyze_events(self, side):        
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
        #if pygame.sprite.groupcollide(self.duendesD,self.monedaD,False,False):            
        if pygame.sprite.spritecollideany(self.duendesD[0],self.monedaD):
            events.append("collideleft")
            
        if pygame.sprite.spritecollideany(self.duendesD[1],self.monedaD):
           events.append("collideright")               
                
        return events

    def refresh(self):
        
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 70)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (10, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]- 100, 10))
        
        if score[0] >= 600 or score[1] >= 600:
            font2 = pygame.font.Font(None,100) 
            text1 = font2.render(f"!GAME OVER¡", 1, WHITE)
            self.screen.blit(text1, (150, 250))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
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
        

