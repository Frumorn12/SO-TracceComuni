from threading import Thread, RLock, Barrier, Condition
from random import randint, seed
from time import sleep

NUM_GIOCATORI_PER_SQUADRA = 5
max_tiri = 50 #Punto 3: numero massimo di tiri



class TiroAllaFune:
    
    def __init__(self, soglia=10):
        self.posizione = 0
        self.soglia = soglia
        self.lock = RLock()
        self.condition = Condition(self.lock) 
        self.vincitore = None
        self.tirieffettuati = 0 #Punto 3: numero di tiri effettuati
        self.squadra1 = [] #Punto 5: Fatto per il killer
        self.squadra2 = [] #Punto 5: Fatto per il killer


    def start(self):
        self.squadra1 = [Player(self, 1) for _ in range(NUM_GIOCATORI_PER_SQUADRA)]
        self.squadra2 = [Player(self, -1) for _ in range(NUM_GIOCATORI_PER_SQUADRA)]
        
        for p in self.squadra1 + self.squadra2: # Inizializza tutti i thread
            p.start()
            
        self.threadKiller = Killer(self) # Punto 5: Inizializza il killer
        self.threadKiller.start() # Punto 5: Starta il killer
        self.caricatori = [Caricatore(self) for _ in range(3)] # Punto 1: Inizializza i caricatore 
        for c in self.caricatori: #Punto1 starta i caricatori
            c.start() 
        self.visualizzatore = Visualizatore(self) # Punto 2: Inizializza il visualizzatore 
        self.visualizzatore.start() # Punto 2: Starta il visualizzatore

        for p in self.squadra1 + self.squadra2: 
            p.join()
            
        print(f"Vincitore: {self.vincitore}!") 


    def tira(self, direzione):
        with self.lock:

            if self.vincitore is None  :  # Controlla se il gioco Ã¨ ancora attivo
                self.posizione += direzione

                self.tirieffettuati += 1 # Punto 3: Incrementa il numero di tiri effettuati
                

                if self.tirieffettuati >= max_tiri:  # Punto 3: Controlla se sono stati effettuati troppi tiri
                    self.vincitore = "Pareggio"
                elif self.posizione >= self.soglia:
                    self.vincitore = "Squadra 1"
                elif self.posizione <= -self.soglia:
                    self.vincitore = "Squadra 2"

            return self.vincitore is None  # True se il gioco continua, False se Ã¨ finito
    
    def tira_con_energia(self, direzione, energia): #Punto 4: Aggiunta del parametro energia
        with self.lock:
            while energia[0] <= 3: # la lista viene passata per riferimento, quindi se la energia[0] scende sotto 3 il thread si ferma 
                self.condition.wait() 
            
            energia[0] -= 1 # Simula il consumo di energia

            return self.tira(direzione) 

    def ricarica(self): #Punto 1: Aggiunta del metodo per ricaricare l'energia
        with self.lock:
            # prendo a caso un giocatore da una delle due squadre
            if randint(0, 1) == 0:
                giocatore = self.squadra1[randint(0, len(self.squadra1) - 1)]
            else:
                giocatore = self.squadra2[randint(0, len(self.squadra2) - 1)] 
            # Aumento l'energia del giocatore casualmente tra 1 o 2
            energia_aumento = randint(1, 2)
            giocatore.energia[0] += energia_aumento
            self.condition.notify_all()  # Risveglia i thread in attesa di essere ricaricati   
    
    def stampa_situazione(self):
        # Pulisce schermo
        with self.lock:
            print("\033[H\033[J") # questo print serve a pulire lo schermo (clear su terminale)
            # Stampa graficamente la posizione della fune
            print("=" * (self.soglia + self.posizione) + "|" + "=" * (self.soglia - self.posizione))
            
            # stampo le energie dei giocatori
            print("Energie:")
            for i, p in enumerate(self.squadra1 + self.squadra2):
                print(f"Giocatore {i+1}: {p.energia[0]}")
            
    
    #Punto 5: Aggiunta funzione per uccidere il giocatore con meno tiri
    def killa(self):
        with self.lock:
            minimo = 999999999999999
            player = None 
            for p in self.squadra1 + self.squadra2:
                if p.tiri < minimo:
                    minimo = p.tiri
                    player = p 
            
            # stoppa il thread del giocatore con meno tiri
            player.STOP = True
            # devo cacciarlo anche dalla lista dei giocatori
            if player in self.squadra1:
                self.squadra1.remove(player)
            else:
                self.squadra2.remove(player)

#Punto 5 : Aggiunta del killer
class Killer(Thread):
    def __init__(self, game: TiroAllaFune):
        super().__init__()
        self.game = game

    def run(self):
        while True:
            sleep(15)  # Aspetta 5 secondi tra un uccisione e l'altra
            self.game.killa()  # Uccide il giocatore con meno tiri

        

class Player(Thread):

    def __init__(self, game: TiroAllaFune, direzione: int):
        super().__init__()
        self.energia = [10] # Punto 1: Inizializza l'energia 
        self.game = game
        self.direzione = direzione
        self.tiri = 0 # Punto 3: Inizializza il numero di tiri effettuati dal giocatore 
        self.STOP = False # Punto 5: Inizializza la variabile di stop per il killer 

    def run(self):
        
        while not self.STOP: 
            sleep(randint(1, 3) * 0.5)  # Simula forza diversa tra giocatori
            if not self.game.tira_con_energia(self.direzione, self.energia):  # Punto Tira la fune
                break  # Se il gioco Ã¨ finito, il thread si ferma
            self.tiri += 1 # per il killer punto 5 

        if self.STOP:
            print(f"Giocatore {self.direzione} ha tirato {self.tiri} volte e viene eliminato!") 

#Punto 1: Aggiunta del caricatore          
class Caricatore(Thread):
    def __init__(self, game: TiroAllaFune):
        super().__init__()
        self.game = game
        
    def run(self):
        while True:
            sleep(0.5)
            print("Ricarico energia...") 
            self.game.ricarica() 


#Punto 2 :  Aggiunta del visualizzatore
class Visualizatore(Thread):
    def __init__(self, game: TiroAllaFune):
        super().__init__()
        self.game = game
        
    def run(self):
        while True:
            sleep(0.5)
            self.game.stampa_situazione()  # Punto 4: Stampa la situazione della fune 

if __name__ == "__main__":
    gioco = TiroAllaFune()
    gioco.start()

