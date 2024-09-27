"""
Cosa bisogna fare:

Abbiamo un topo e un gatto che sono rappresentati all'interno di una stringa
di S dimensione. Il gatto è rappresentato dal simbolo "*"  e il topo dal
simbolo "." . Il gatto si muove periodicamente di una posizione, da
sinistra verso destra, fino al bordo della striscia, per poi alternativaemnte
cominciare a muoversi da destra fino a sinistra. Il topo si muove di una
posizione in modo casuale. Il topo puo muoversi a destra, sinistra o stare fermo.
Il gatto mangia il topo se si trovano nella stessa posizione.

"""


from threading import Thread, Condition, RLock
from time import sleep
from random import random,randrange, randint

class Pavimento:
    S = 50 # lunghezza del pavimento

    # Inizializzazione del pavimento con il topo e il gatto

    def __init__(self):
        self.pavimento = [" "]*self.S
        self.topo = randint(0, self.S - 1)
        self.gatto = randint(0, self.S - 1) if (gatto := randint(0, self.S - 1)) != self.topo else randint(0, self.S - 1)
        self.pavimento[self.topo] = "."
        self.pavimento[self.gatto] = "*"
        self.salto = 0
        self.Fine = False # Il gioco non è finito

        # bordo prende false o true casulamente ad inzio
        self. bordo = bool(randint(0,1))
        self.lock = RLock()
        self.condition = Condition(self.lock) # Condition per la sincronizzazione del display

    def muoviTopo(self):
        with self.lock:


            self.pavimento[self.topo] = " "
            self.salto = randrange(-1,2)
            if 0 <= self.topo + self.salto < self.S:
                self.topo = self.topo + self.salto
            self.pavimento[self.topo] = "."
            if self.topo == self.gatto:
                print("Il topo `e stato mangiato dal gatto")
                self.pavimento[self.topo] = "X"
                self.Fine = True # Il gioco è finito

            self.condition.notify() # Notifico il display
            return self.Fine # Ritorno se il gioco è finito

    def muoviGatto(self):
        with self.lock:
            self.pavimento[self.gatto] = " "
            if self.gatto == 0:
                self.bordo = False # Il gatto si muove da sinistra verso destra
            elif self.gatto == self.S - 1:
                self.bordo = True

            if self.bordo:
                self.salto = -1
            else:
                self.salto = 1

            self.gatto = self.gatto + self.salto
            self.pavimento[self.gatto] = "*"
            if self.topo == self.gatto:
                print("Il gatto ha mangiato il topo")
                self.pavimento[self.topo] = "X"
                self.Fine = True
            self.condition.notify()
            return self.Fine



class Display(Thread):
    def __init__(self,pavimento):
        super().__init__()
        self.pavimento = pavimento

    def run(self):
        while True:
            with self.pavimento.lock:
                self.pavimento.condition.wait()
                print("".join(self.pavimento.pavimento))
                if self.pavimento.Fine:
                    break



class Topo(Thread):
    def __init__(self,pavimento):
        super().__init__()
        self.pavimento = pavimento

    def run(self):
        while True:
            if self.pavimento.muoviTopo():
                break
            sleep(random())
            if self.pavimento.Fine:
                print ("Il topo è stato mangiato")
                break # Se il gioco è finito, termino il thread del topo

class Gatto(Thread):
    def __init__(self,pavimento):
        super().__init__()
        self.pavimento = pavimento

    def run(self):
        while True:
            if self.pavimento.muoviGatto():
                break
            sleep(random())
            if self.pavimento.Fine:
                print ("Il gatto ha mangiato il topo")
                break # Se il gioco è finito, termino il thread del gatto



def main():
    pavimento = Pavimento()
    display = Display(pavimento)
    display.start()
    topo = Topo(pavimento)
    gatto = Gatto(pavimento)
    topo.start()
    gatto.start()

main() # Avvio del programma