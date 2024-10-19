# !/usr/bin/env python

from threading import Thread, RLock, Barrier, Condition
from queue import Queue
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
    #
    #  vetture = Queue(10)
    #  Utilizziamo un vettore anzichÃ¨ una coda per potere indicizzare l'elemento 0
    #
    MAXSIZE = 10

    def __init__(self):
        super(SorgenteVetture, self).__init__()
        self.vetture = []
        self.lock = RLock()
        self.full = Condition(self.lock)
        self.empty = Condition(self.lock)
        self.running = True

    def __printPercheAspetto(self, size):
        print(f"WAIT. Running: {self.running}. Len: {len(self.vetture)}. Size: {size}")
        if len(self.vetture) > 0:
            print(f"   PRIMA VETTURA ATTUALE: {self.vetture[0].size}")

    #
    #  Questo metodo viene chiamato quando si vuol prendere una Vettura prodotta dalla SorgenteVettura
    #
    #  Soluzione: modificato per poter dire il tipo di vettura che si desidera
    #
    # Vecchia versione
    # def getVettura(self):
    #    return self.vetture.get()
    #
    # Nuova versione
    #
    def getVettura(self, size=0):

        with self.lock:
            while (self.running and
                   (len(self.vetture) == 0 or (size != 0) and self.vetture[0].size != size)):
                self.__printPercheAspetto(size)
                self.empty.wait()
            self.full.notify()
            #
            # Potrei avere liberato una macchina o un autobus in seconda posizione che adesso va in prima
            #
            self.empty.notify()
            #
            # Il traghetto risulta in partenza, la get fallisce
            #
            if not self.running:
                return None
            print(f"Qualcuno preleva {type(self.vetture[0])}")
            return self.vetture.pop(0)

            #

    #  Sostituisce la semplice put dentro quella che precedentemente era una queue.
    #
    def putVettura(self, v):
        with self.lock:
            while self.running and len(self.vetture) == self.MAXSIZE:
                self.full.wait()
            self.empty.notify()
            #
            # Il traghetto risulta in partenza, la put fallisce
            #
            if not self.running:
                return False
            self.vetture.append(v)
            return True

    def getAutomobile(self):
        return self.getVettura(2)

    def getAutobus(self):
        return self.getVettura(4)

    #
    # Questo metodo si assicura che se il traghetto Ã¨ ormai carico, tutti i thread, anche quelli eventualmente bloccati su put o get
    # vengano risvegliati e terminano correttamente
    #
    def fermaTutto(self):
        with self.lock:
            print("Ferma TUTTO!")
            self.running = False
            #
            # Sveglia qualsiasi thread in attesa su put o get, segnalando che le attivitÃ  sono terminate
            #
            self.empty.notifyAll()
            self.full.notifyAll()

    def run(self):
        # while True:
        #
        # Si noti che 'ancora' Ã¨ una variabile locale, non in accesso condiviso
        #
        ancora = True
        while ancora:
            sleep(random() * 0.2)
            #  Genera una vettura a intervalli casuali
            v = Automobile() if randint(0, 1) == 0 else Autobus()
            # self.vetture.put(v)
            print(f"Genera {type(v)}")
            ancora = self.putVettura(v)
        print("Sorgente TERMINATA.")


class Striscia(object):

    def __init__(self):
        self.size = 50
        self.l = RLock()

    def put(self, v):
        self.size -= v.size

    def getPostiLiberi(self):
        return self.size

    #
    #  Data una vettura v, prova a posizionarla in questa striscia.
    #  Restituisce true se operazione avvenuta con successo.
    #
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
        print(f"START Parcheggiatore {self.id}")

    def getVettura(self):
        return self.traghetto.sorgente.getVettura()

    def run(self):
        possoParcheggiare = True
        while possoParcheggiare:
            v = self.getVettura()
            trovato = False
            if v != None:
                for i in range(6):
                    #
                    # Ogni parcheggiatore ha una sua striscia preferita che dipende da self.id
                    # La striscia preferita viene provata prima di tutte le altre
                    #
                    if self.traghetto.strisce[(i + self.id) % 6].provaAInserire(v):
                        trovato = True
                        print(f"S:{(i + self.id) % 6}-{str(self.id) * v.size}")
                        break
            #
            # Un parcheggiatore che non trova posto non parcheggia la vettura corrente
            # e cessa tutte le attivitÃ .
            #
            # In questa soluzione, il primo parcheggiatore che non trova posto ferma comunque il processo di carico,
            # anche se potrebbe esserci spazio residuo (esempio: non c'Ã¨ spazio per un autobus, ma magari per qualche automobile sÃ¬)
            #
            if not trovato:
                possoParcheggiare = False
                self.traghetto.sorgente.fermaTutto()
        print(f"END Parcheggiatore {self.id}")
        self.traghetto.b.wait()


class ParcheggiaAutobus(Parcheggiatore):

    def __init__(self, t, id):
        super(ParcheggiaAutobus, self).__init__(t, id)

    def getVettura(self):
        return self.traghetto.sorgente.getAutobus()


class ParcheggiaAutomobile(Parcheggiatore):

    def __init__(self, t, id):
        super(ParcheggiaAutomobile, self).__init__(t, id)

    def getVettura(self):
        return self.traghetto.sorgente.getAutomobile()


class Traghetto:

    def __init__(self):
        self.sorgente = SorgenteVetture()
        self.b = Barrier(5)
        self.strisce = [Striscia() for _ in range(6)]

    def caricaTraghetto(self):
        self.sorgente.start()
        #        for i in range(4):
        #            Parcheggiatore(self, i).start()
        for i in range(2):
            ParcheggiaAutobus(self, i).start()
        for i in range(2, 4):
            ParcheggiaAutomobile(self, i).start()

        self.b.wait()
        self.sorgente.fermaTutto()


if __name__ == '__main__':
    siremarOne = Traghetto()
    siremarOne.caricaTraghetto()

