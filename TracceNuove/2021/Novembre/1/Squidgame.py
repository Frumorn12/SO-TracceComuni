from threading import RLock, Thread, Condition
from random import randint
from time import sleep

'''

Il codice fornito implementa il gioco di â€œUn, due, tre, Stella!â€, nella versione resa famosa dalla serie The Squid Game. 
457 diversi Player devono riuscire a compiere un certo numero di passi N entro lo scadere di un certo tempo limite T (gameDuration nel codice). 
Un semaforo che si alterna a intervalli temporali casuali tra i valori RED e GREEN stabilisce i momenti in cui i Player possono muoversi. 
Se un Player si muove in un momento in cui il  semaforo Ã¨ RED, il Player in questione viene immediatamente eliminato. 
Un Player puÃ² invece compiere liberamente dei passi nei momenti in cui il semaforo Ã¨ GREEN. 
Quando un Player compie piÃ¹ degli N (winningLine nel codice) passi richiesti esso si puÃ² considerare salvo. 
Allo scadere del tempo T, tutti i Player che non hanno ancora compiuto i passi richiesti per salvarsi vengono eliminati e infine il gioco termina definitivamente.

'''

GREEN = 0
RED = 1
NUMPLAYERS = 20

#
# Suggerimento per le prove a casa: ridurre il numero di giocatori e variare la durata del gioco e la winningLine.
#


#
# Funzione di stampa di debug
#
debugOn = True
def debug(text : str):
    if debugOn:
        print(text)

#
# Scheda di ciascun giocatore
#
class PlayerData:

    def __init__(self,p, n : str):
        self.player = p
        self.num = n
        self.position = 0
#
# Classe che tiene traccia dello stato del gioco
#
class UnDueTreStella:

    def __init__(self):

        #
        # Numero di passi che un giocatore deve compiere in tempo per poter salvarsi
        #         
        self.winningLine = 80
        #
        # Tempo a disposizione per poter salvarsi (in secondi)
        #
        self.gameDuration = 20
        #
        # Dizionario che tiene traccia dello stato di ciascun giocatore
        #
        self.playerData = {}
        #
        # Il semaforo puÃ² essere RED o GREEN. Inizialmente Ã¨ GREEN
        #
        self.currentMode = GREEN
        #
        # Il gioco inizia subito e ne teniamo traccia con la variabile running
        #
        self.running = True
        #
        # Lock per proteggere l'accesso a tutte le variabili condivise che stanno in UnDueTreStella
        #
        self.lock = RLock()
        #
        # Creo NUMPLAYERS giocatori, e tengo traccia del loro stato nel dizionario playerData; creo tanti Thread Player corrispondenti e li avvio
        #
        for i in range(1,NUMPLAYERS+1):
            num = "%03d" % i   # num = f"{i:03}"
            pd = PlayerData(Player(self,num),num)
            self.playerData[num] = pd   
            pd.player.start()
        #
        # Avvio il Thread timer, il quale fermerÃ  il gioco dopo self.gameDuration secondi
        #
        Timer(self).start()
        #
        # stellaMaster Ã¨ il Thread che cicla a intervalli casuali il valore del semaforo tra RED e GREEN. Lo creo e lo avvio
        # 
        self.stellaMaster = StellaMaster(self)
        self.stellaMaster.start()
        #
        # Avvio un thread display, il quale mostrerÃ  lo stato del gioco periodicamente.
        #   
        Display(self).start()

    #
    # Metodo per stampare urla concitate
    #    
    def shout(self,text : str):
        print(text.upper()+"!!!!")

    #
    # Ogni Thread Player prova periodicamente a eseguire l'operazione di STEP. Se perÃ² l'operazione viene fatta quando il semaforo Ã¨ RED, si MUORE
    #
    def step(self, num : str) -> int:
        sleep(randint(0,5)/10)
        with self.lock:
            if self.currentMode == GREEN:
                self.playerData[num].position += 1
                if self.playerData[num].position > self.winningLine:
                    #
                    # SAFE! Sono salvo e oltre la linea finale
                    #
                    return 0 
                else:
                    #
                    # Sono riuscito a fare un passo in piÃ¹
                    #
                    return 1
            else: 
                # se si arriva in questo ramo, il semaforo Ã¨ RED. il Player viene UCCISO
                self.kill(num)
                return -1

    #
    # Metodo per testare il colore attuale del semaforo. Usato dai Player
    #
    def getLight(self) -> int:
        with self.lock:
            return self.currentMode

    #
    #  Metodo per cambiare il colore del semaforo. Usato da StellaMaster
    #
    def setLight(self, v : int):
        with self.lock:
            self.currentMode = v
    #
    # Metodo per interrompere il gioco. Invocato da Timer
    #
    def stop(self):
        with self.lock:
            self.running = False

    #
    # Metodo per verificare se il gioco Ã¨ finito.
    # Un gioco si considera terminato se sono morti tutti i giocatori, oppure il Timer ha impostato self.running = False
    # Invocato da StellaMaster.
    #
    def gameOver(self) -> bool:
        with self.lock:
            return not self.running or len(self.playerData) == 0

    #
    # Metodo che uccide un player ed elimina i suoi dati da playerData. Invocato in due casi:
    #    -dall'interno di step() quando si fa un passo falso con luce RED
    #    -a tempo scaduto quando il player Ã¨ rimasto dietro la linea di salvezza
    #
    def kill(self,num):
        with self.lock:
            if num in self.playerData:
                self.shout("killing player %s aahahahahaha" % num)   # self.shout(f"killing player {num} aahahahahaha")
                del self.playerData[num]
            #else: 
            #    print(f"Player {num} is dead already")
    #
    # Uccide tutti i player che a tempo scaduto si trovano ancora dietro la linea di salvezza. Invocato da stellaMaster
    #
    def killPeople(self):
        with self.lock:
            #
            # Non si possono cancellare elementi da un dizionario mentre vi si sta iterando sopra. 
            # dunque Ã¨ necessario prima ricopiare tutte le chiavi in una nuova lista separata.
            #
            for num in list(self.playerData.keys()):
                #
                #  Giocatore che non si Ã¨ salvato. Lo eliminiamo
                #
                if self.playerData[num].position <= self.winningLine:
                    self.kill(num)
                #
                #  Giocatore che si Ã¨ salvato.
                #
                else:
                    print("Sparing player %s" % num)     # print(f"Sparing player {num}")
    #
    # Stampa la situazione di gioco attuale. Per ogni giocatore viene stampato il numero corrispondente e il numero di passi fatti
    # Esempio: 045:013 => Il giocatore 045 ha compiuto 13 passi finora.
    # Invocato da Display
    #
    def printPlayers(self):
        with self.lock:
            txt = ""
            for pd in self.playerData.values():
                txt += f"%s:%03d " % (pd.num,pd.position)   #  txt += f"{pd.num}:{pd.position:03} "
            print(txt)    
#
# Thread il cui unico scopo Ã¨ arrestare il gioco al termine di un periodo di durata scelta
#
class Timer(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        debug("Timer started")
        sleep(self.game.gameDuration)
        self.game.stop()
        self.game.shout("TIME IS OVER!")

#
# Thread giocatore
#
class Player(Thread):

    def __init__(self,game : UnDueTreStella, numero : str):
        Thread.__init__(self)
        self.game = game
        self.numero = numero

    #
    #  Il ciclo di vita di un giocatore Ã¨ il seguente:
    #       -verifico che la luce sia verde
    #       -se sÃ¬, provo a fare uno step
    #
    #  step puÃ² restituire tre valori diversi che finiscono nella variabile aliveAndKicking, in dipendenza dei quali il Player si regola di conseguenza:
    #   
    #   aliveAndKicking = 1. Tutto OK per ora, continua a fare step
    #   aliveAndKicking = -1. L'ultimo step Ã¨ fallito, sono MORTO, dunque il thread termina
    #   aliveAndKicking = 0. Il Player ha superato la linea. E' salvo e il thread puÃ² terminare
    #
    def run(self):
        debug("Player %s started" % self.numero)  #  debug(f"Player {self.numero} started")
        aliveAndKicking = 1
        while aliveAndKicking > 0:
            if self.game.getLight() == GREEN:
                aliveAndKicking = self.game.step(self.numero)
                    
        if aliveAndKicking == -1:
            self.game.shout("Please please no no no no don't kill meeee aaaaaahhhh. [RIP Player %s]" % self.numero)  #self.game.shout(f"Please please no no no no don't kill meeee aaaaaahhhh. [RIP Player {self.numero}]")
        else:
            self.game.shout("I'm aliveeeeeeeee. [Player %s survives beyond the line]" % self.numero)     #self.game.shout(f"I'm aliveeeeeeeee. [Player {self.numero} survives beyond the line]")

class StellaMaster(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game
    #
    # Lo StellaMaster Ã¨ il thread che gestisce il semaforo. 
    # FintantochÃ¨ il gioco non Ã¨ gameOver() lo StellaMaster alterna tra RED e GREEN LIGHT a intervalli di tempo casuali
    # Quando il gioco finisce (il timer scade, oppure sono morti tutti)
    # lo StellaMaster invoca killPeople() e uccide tutti i Player che sono rimasti dietro la linea allo scadere del tempo
    #
    def run(self):
        debug("StellaMaster Started")
        while not self.game.gameOver():
            self.game.shout("green light")
            self.game.setLight(GREEN)
            sleep(randint(1,10)/5)
            self.game.shout("red light")
            self.game.setLight(RED)
        #print(f"The timer ended with {len(self.game.playerData)} survivors. Proceeding to kill survivors still before the winning line.")
        print("The timer ended with %d survivors. Proceeding to kill survivors still before the winning line." % len(self.game.playerData))
        self.game.killPeople()
        #print(f"The game ended with {len(self.game.playerData)} survivors. Proceeding to next game.")
        print(f"The game ended with %d survivors. Proceeding to next game." % len(self.game.playerData))

#
# Il Thread Display visualizza lo stato del gioco a intervalli di un secondo.
#
class Display(Thread):

    def __init__(self,game : UnDueTreStella):
        Thread.__init__(self)
        self.game = game

    def run(self):
        while(not self.game.gameOver()):
            sleep(1)
            self.game.printPlayers()

theSquidGame = UnDueTreStella()
print ("GAME STARTED. GOOD LUCK")

