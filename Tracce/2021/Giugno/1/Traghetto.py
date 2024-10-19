#!/usr/bin/env python
from threading import Thread, RLock, Barrier, Condition
from queue import Queue, Empty
from time import sleep
from random import random, randint

class Vettura(object):
    def __init__(self):
        self.size = 0

    def printSize(self):
        print(self.size)

class Automobile(Vettura):
    def __init__(self):
        super(Automobile, self).__init__()
        self.size = 2

class Autobus(Vettura):
    def __init__(self):
        super(Autobus, self).__init__()
        self.size = 4

class SorgenteVetture(Thread):
    vetture = Queue(10)

    def __init__(self):
        super(SorgenteVetture, self).__init__()
        self.cond = Condition()
        self.running = True  # Flag per controllare se il thread deve continuare a generare vetture

    def getVettura(self):
        return self.vetture.get()

    def getAutobus(self):
        with self.cond:
            while self.running or not self.vetture.empty():
                if not self.vetture.empty():
                    v = self.vetture.queue[0]  # Controlliamo il primo elemento
                    if isinstance(v, Autobus):  # Verifica se è un Autobus
                        return self.vetture.get()
                self.cond.wait()  # Aspetta finché non arriva un Autobus
        raise Empty  # Solleva un'eccezione se la coda è vuota e il thread è fermo

    def getAutomobile(self):
        with self.cond:
            while self.running or not self.vetture.empty():
                if not self.vetture.empty():
                    v = self.vetture.queue[0]  # Controlliamo il primo elemento
                    if isinstance(v, Automobile):  # Verifica se è un'Automobile
                        return self.vetture.get()
                self.cond.wait()  # Aspetta finché non arriva un'Automobile
        raise Empty  # Solleva un'eccezione se la coda è vuota e il thread è fermo

    def run(self):
        while self.running:
            sleep(random() * 2)
            v = Automobile() if randint(0, 1) == 0 else Autobus()
            with self.cond:
                self.vetture.put(v)
                self.cond.notify_all()  # Notifica tutti i thread in attesa

    def stop(self):
        with self.cond:
            self.running = False  # Imposta il flag per fermare il thread
            self.cond.notify_all()  # Risveglia tutti i thread bloccati per controllare la chiusura

class Striscia(object):
    def __init__(self):
        self.size = 50
        self.l = RLock()

    def put(self, v):
        self.size -= v.size

    def getPostiLiberi(self):
        return self.size

    def provaAInserire(self, v):
        with self.l:
            if self.getPostiLiberi() >= v.size:
                self.put(v)
                return True
            else:
                return False

class Parcheggiatore(Thread):
    def __init__(self, t, id):
        super(Parcheggiatore, self).__init__()
        self.traghetto = t
        self.id = id
        print(f"Parcheggiatore {self.id} pronto")

    def run(self):
        pass

class ParcheggiaAutobus(Parcheggiatore):
    def run(self):
        possoParcheggiare = True
        while possoParcheggiare:
            try:
                v = self.traghetto.sorgente.getAutobus()
            except Empty:
                break
            trovato = False
            for i in range(6):
                if self.traghetto.strisce[(i + self.id) % 6].provaAInserire(v):
                    trovato = True
                    print(f"S:{(i+self.id)%6}-AUTOBUS-{self.id}")
                    break
            if not trovato:
                possoParcheggiare = False
        self.traghetto.b.wait()

class ParcheggiaAutomobili(Parcheggiatore):
    def run(self):
        possoParcheggiare = True
        while possoParcheggiare:
            try:
                v = self.traghetto.sorgente.getAutomobile()
            except Empty:
                break
            trovato = False
            for i in range(6):
                if self.traghetto.strisce[(i + self.id) % 6].provaAInserire(v):
                    trovato = True
                    print(f"S:{(i+self.id)%6}-AUTO-{self.id}")
                    break
            if not trovato:
                possoParcheggiare = False
        self.traghetto.b.wait()

class Traghetto:
    def __init__(self):
        self.sorgente = SorgenteVetture()
        self.b = Barrier(5)
        self.strisce = [Striscia() for _ in range(6)]

    def caricaTraghetto(self):
        self.sorgente.start()
        for i in range(2):
            ParcheggiaAutobus(self, i).start()
        for i in range(2, 4):
            ParcheggiaAutomobili(self, i).start()
        self.b.wait()
        self.sorgente.stop()  # Ferma il thread SorgenteVetture
        self.sorgente.join()  # Attende che il thread SorgenteVetture termini

if __name__ == '__main__':
    siremarOne = Traghetto()
    siremarOne.caricaTraghetto()
