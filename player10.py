############################################################################
#                           JUEGO DUENDES                                  #        
############################################################################

from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import time

TMAX = 400
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

X = 0
Y = 1
SIZE = (750, 625)

FPS = 60

#Definimos la clase Duende, la clase Moneda y la clase Game de nuestro juego
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
    #inicializamos las variables
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
    def get_time(self):
        return self.time
    def set_time(self,time):
        self.time=time
    def set_score(self, score):
        self.score = score
    #actualizamos el juego;la cantidad de monedas obtenidas, asi como la posicion de cada duende y moneda
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
#Creamos las clases que dibujan en la pantalla los diferentes objetos
class duende_Draw(pygame.sprite.Sprite):
    
    def __init__(self,mon):
        super().__init__()
        self.duende = mon
        self.image = pygame.image.load('duende.png') #para cargar la imagen
        self.image = pygame.transform.scale(self.image,(90,90)) #para ajustar la imagen a la pantalla
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect() #para obtener el area rectangular de la imagen
        self.update()
        
    def update(self):        
        pos = self.duende.get_pos()
        self.rect.centerx, self.rect.centery = pos  
        
    def draw(self, screen):
        screen.window.blit(self.image, self.rect) #para dibujar el duende sobre la pantalla
   
    def __str__(self):
        return f"S<{self.mon}>"

class moneda_Draw(pygame.sprite.Sprite):
    
    def __init__(self, mon):
        super().__init__()
        self.moneda = mon
        self.image= pygame.image.load('moneda2.png') #para cargar la imagen
        self.image = pygame.transform.scale(self.image,(50,50)) #para ajustar la imagen a la pantalla
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect() #para obtener el area rectangular de la imagen
        self.update()

    def update(self):
        pos = self.moneda.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    def draw(self,screen):
        screen.window.blit(self.image,(self.mon.pos)) #para dibujar la moneda sobre la pantalla
       
    def __str__(self):
        return f"P<{self.mon.pos}>"
   
class Display():
    
    def __init__(self,game, n_duendes):        
        self.game = game
        self.n_duendes=n_duendes
        self.score = game.get_score()
        self.time=game.get_time()
        self.duendesD = [duende_Draw(self.game.get_duende(i)) for i in range(n_duendes)]
        self.monedaD = [moneda_Draw(self.game.get_moneda(i)) for i in range(10)]
        self.all_sprites = pygame.sprite.Group() #para administrar los multiples objetos sprite
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
        self.time_group=pygame.sprite.Group()
        self.background = pygame.image.load('city.jpg')
        self.background = pygame.transform.scale(self.background,(750,625))
        self.reloj = pygame.image.load('reloj.png')
        self.reloj = pygame.transform.scale(self.reloj,(20,30))
        self.btitulo = pygame.image.load('fondotitulo.jpg')
        self.btitulo = pygame.transform.scale(self.btitulo,(250,32))
        pygame.mixer.init() #para configurar la m??sica del juego
        self.sound=pygame.mixer.music.load('musica.ogg') 
        self.sound=pygame.mixer.music.set_volume(0.4)
        pygame.init()
        pygame.mixer.music.play(loops=-1)
#Definimos el funcionamiento del juego mediante la pulsaci??n de las teclas left y right
    def analyze_events(self):
        events = []        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: #forma de salir del juego
                    events.append("quit")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
            elif event.type == pygame.QUIT:
                events.append("quit")       
        return events

    def refresh(self):
        self.all_sprites.update() #para actualizar todos los objetos sprite del juego
        self.screen.blit(self.background, (0, 0)) #A??adimos a la pantalla un reloj, un titulo..
        self.background.blit(self.reloj,(10,5))
        self.background.blit(self.btitulo,(SIZE[X]-500, 5))
        score = self.game.get_score()
        time = self.game.get_time()
        font = pygame.font.SysFont('console', 18, True)
        font1 = pygame.font.SysFont('console', 23, True)
        text1 = font1.render('JUEGO DUENDES', 1, BLACK, self.btitulo)
        self.background.blit(text1, (SIZE[X]-460, 8))
        
        for i in range(self.n_duendes):
        	text2 = font.render(f"JUGADOR {i}: {score[i]}", 1, WHITE, (116,87,83,255))
        	self.screen.blit(text2, (SIZE[X]-160, i*30+10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    #Funcion que a??ade el contador de tiempo a la pantalla del juego
    def tick(self):       
        fuente = pygame.font.SysFont("console", 18, True)
        aux1 = 0
        clock = (pygame.time.get_ticks())//1000
        
        if aux1==clock:
            aux1=aux1+1
            print(clock)
        tiempo = TMAX-clock
        self.clock.tick(FPS)
        contador = fuente.render("TIEMPO: " + str(tiempo),1,WHITE, (116,87,83,255))
        self.screen.blit(contador,(SIZE[X]-710, 10))
        pygame.display.update()

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    print ('??Cu??ntos jugadores desean comenzar la partida?')
   
    n_duendes=int(input())
    port = 6000
    try:
        with Client((ip_address, port), authkey=b'secret password') as conn:
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
            gameScore = list(game.get_score())
            maximum = max(gameScore)
            winner = []
            for i in range (n_duendes):
                if (gameScore[i] == maximum ):
                        winner.append(i)
            print (' El GANADOR es el jugador :',  '\t'.join(map(str,winner)))
    except:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)    
