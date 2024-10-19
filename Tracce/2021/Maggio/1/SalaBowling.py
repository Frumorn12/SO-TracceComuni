#!/usr/bin/python3

from threading import RLock, Condition, Thread
from time import sleep
from random import random

class Sala:

    def __init__(self, num_piste, num_palle):
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.num_piste = num_piste
        self.pista = [False] * num_piste
        self.palleDisponibili = num_palle
        self.prossimo_da_servire = 1
        self.bollino = 1

    # Metodo originale senza starvation
    def richiediPista(self, id_squadra, numGiocatori):
        with self.lock:
            mioBollino = self.bollino
            self.bollino += 1
            while (self.__cercaPista() == -1 or
                   self.palleDisponibili < numGiocatori or
                   mioBollino != self.prossimo_da_servire):
                print(f"La squadra {id_squadra} con {numGiocatori} giocatori deve attendere il suo turno con bollino {mioBollino}")
                self.condition.wait()

            # fa scorrere il turno
            self.prossimo_da_servire += 1
            # si dà la possibilità immediata di provare a giocare al prossimo numero da servire
            self.condition.notifyAll()
            self.palleDisponibili -= numGiocatori
            p = self.__cercaPista()
            self.pista[p] = True
            print(f"La squadra {id_squadra} ottiene la pista {p} con {numGiocatori} giocatori e bollino {mioBollino}")
            return p

    # Metodo nuovo: richiedi pista con retrocessione di 4 posti
    def richiediPistaGentilmente(self, id_squadra, numGiocatori):
        with self.lock:
            mioBollino = self.bollino
            self.bollino += 1

            while True:
                # Verifica se è il turno della squadra
                if mioBollino == self.prossimo_da_servire:
                    # Controlla se ci sono abbastanza palle e una pista disponibile
                    if self.__cercaPista() != -1 and self.palleDisponibili >= numGiocatori:
                        # Se ci sono le risorse, prosegui con l'assegnazione della pista
                        self.prossimo_da_servire += 1
                        self.condition.notifyAll()
                        self.palleDisponibili -= numGiocatori
                        pista = self.__cercaPista()
                        self.pista[pista] = True
                        print(f"La squadra {id_squadra} ottiene la pista {pista} con {numGiocatori} giocatori e bollino {mioBollino}")
                        return pista
                    else:
                        # Se non ci sono le risorse, la squadra retrocede di 4 posizioni o va in fondo alla coda
                        self.prossimo_da_servire += 1
                        self.bollino += 4 if self.bollino - self.prossimo_da_servire > 4 else (self.bollino - self.prossimo_da_servire)
                        print(f"La squadra {id_squadra} non ha trovato risorse e retrocede di 4 posizioni con bollino {self.bollino}.")
                        self.condition.notifyAll()
                        self.condition.wait()
                else:
                    # Se non è il turno della squadra, aspetta
                    print(f"La squadra {id_squadra} con {numGiocatori} giocatori deve attendere il suo turno con bollino {mioBollino}")
                    self.condition.wait()

    def liberaPista(self, numPista, numGiocatori):
        with self.lock:
            self.palleDisponibili += numGiocatori
            self.pista[numPista] = False
            self.condition.notifyAll()

    def __cercaPista(self):
        for i in range(0, len(self.pista)):
            if not self.pista[i]:
                return i
        return -1

class Squadra(Thread):

    def __init__(self, id, sala, usa_metodo_gentile=False):
        super(Squadra, self).__init__()
        self.sala = sala
        self.id = id
        self.usa_metodo_gentile = usa_metodo_gentile

    def run(self):
        while True:
            # il giocatore fa altro prima di chiedere una pista
            sleep(int((random() * 6)))
            # prova a chiedere una pista
            numGiocatori = int((random() * 20)) + 1
            print(f"La squadra {self.id} chiede una pista per {numGiocatori} giocatori.")

            # Usa il metodo normale o gentile in base alla scelta
            if self.usa_metodo_gentile:
                pista = self.sala.richiediPistaGentilmente(self.id, numGiocatori)
            else:
                pista = self.sala.richiediPista(self.id, numGiocatori)

            print(f"La squadra {self.id} gioca sulla pista {pista}.")
            # tempo di gioco
            sleep(int((random() * 4)))
            self.sala.liberaPista(pista, numGiocatori)
            print(f"La squadra {self.id} lascia la pista {pista}.")

if __name__ == '__main__':
    s = Sala(3, 20)
    # Creiamo alcune squadre che usano il metodo tradizionale e alcune il metodo gentile
    for i in range(0, 3):
        Squadra(i, s, usa_metodo_gentile=False).start()
    for i in range(3, 5):
        Squadra(i, s, usa_metodo_gentile=True).start()
