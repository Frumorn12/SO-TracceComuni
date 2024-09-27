"""
Bisogna creare un programmino multithread che permetta a i partecipanti di
sedersi su N sedie. Il programma deve permettere a i partecipanti di sedersi
sulle sedie se esse sono libere, altrimenti devono aspettare che una sedia si
liberi. Quando tutte le sedie sono occupate, il programma deve stampare a
schermo "Tutte le sedie sono occupate" e terminare.

Ci sono n+1 partecipanti di n sedie, quindi uno dei partecipanti non riuscirà
a sedersi.

"""


from threading import Thread,Lock
from time import sleep
from random import random,randrange


class Posto:
    def __init__(self):
        self.occupato = False # Posto libero o occupato
        self.lock = Lock() # Lock per la mutua esclusione

    def testANDsit(self):
        with self.lock:
            if self.occupato:
                return False
            self.occupato = True
            return True


class Partecipante(Thread):
    def __init__(self,posti):
        super().__init__()
        self.posti = posti

    def run(self):
        sleep(randrange(1,5)) # Attesa casuale
        for posto in self.posti:
            if posto.testANDsit():
                print(f"Partecipante {self.name} si è seduto")
                return

        print(f"Tutte le sedie sono occupate, sono {self.name}")


class Display(Thread):
    def __init__(self,posti):
        super().__init__()
        self.posti = posti

    def run(self):
        while True:

            for i,posto in enumerate(self.posti):
                if posto.occupato:
                    print("*", end="", flush=True)
                else:
                    print("o", end="", flush=True)

            print ("\n") # Vado a capo
            sleep(1)



def main():
    N = 10 # Numero di posti
    posti = [Posto() for _ in range(N)]
    partecipanti = [Partecipante(posti) for _ in range(N+1)]
    display = Display(posti)
    display.start()

    # i thread partono in modo casuale
    for partecipante in partecipanti:
        partecipante.start() # Avvio del thread partecipante



main() # Avvio del programma







