from queue import Queue
from threading import Thread, RLock, Condition, current_thread
import random
from time import sleep, time

# Funzione di stampa sincronizzata, utile per il debug
plock = RLock()
debug = True

def dprint(s):
    if debug:
        plock.acquire()
        print(s)
        plock.release()

class DatoCondiviso():
    def __init__(self, v):
        self.dato = v
        self.numLettori = 0
        self.numLockScrittura = 0
        self.currentWriter = None
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def getDato(self):
        return self.dato

    def setDato(self, i):
        self.dato = i

    def acquireReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in lettura")
        while self.numLockScrittura > 0 and self.currentWriter != current_thread():
            dprint(f"Il thread {current_thread().name} attende lo scrittore {self.currentWriter}.")
            self.condition.wait()
        self.numLettori += 1
        dprint(f"Il thread {current_thread().name} prende il lock in lettura")
        self.lock.release()

    def releaseReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} rilascia il lock in lettura")
        self.numLettori -= 1
        if self.numLettori == 0:
            self.condition.notify()
        self.lock.release()

    def acquireWriteLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in scrittura")
        while self.numLettori > 0 or self.numLockScrittura > 0 and self.currentWriter != current_thread():
            dprint(f"Il thread {current_thread().name} attende di scrivere su {self}.")
            self.condition.wait()
        self.numLockScrittura += 1
        self.currentWriter = current_thread()
        dprint(f"Il thread {current_thread().name} acquisisce il lock in scrittura")
        self.lock.release()

    def releaseWriteLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} rilascia il lock in scrittura")
        self.numLockScrittura -= 1
        if self.numLockScrittura == 0:
            self.currentWriter = None
        self.condition.notify_all()
        self.lock.release()

class BlockingQueue:
    def __init__(self, dim):
        self.lock = RLock()
        self.full_condition = Condition(self.lock)
        self.empty_condition = Condition(self.lock)
        self.ins = 0
        self.out = 0
        self.slotPieni = 0
        self.dim = dim
        self.thebuffer = [None] * dim

    def put(self, c):
        self.lock.acquire()

        while self.slotPieni == len(self.thebuffer):
            self.full_condition.wait()

        self.thebuffer[self.ins] = c
        self.ins = (self.ins + 1) % len(self.thebuffer)

        self.empty_condition.notifyAll()

        self.slotPieni += 1
        self.lock.release()

    def get(self):
        self.lock.acquire()
        try:
            while self.slotPieni == 0:
                self.empty_condition.wait()

            returnValue = self.thebuffer[self.out]
            self.out = (self.out + 1) % len(self.thebuffer)

            self.full_condition.notifyAll()

            self.slotPieni -= 1
            return returnValue
        finally:
            self.lock.release()

import operator

class InteriCombinati:
    def __init__(self):
        self.V = [DatoCondiviso(0) for _ in range(10)]  # Inizializza l'array di interi
        self.operazioni = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '%': operator.mod}
        self.statistiche = {'+': 0, '-': 0, '*': 0, '/': 0, '%': 0}
        self.element_stats = [0] * 10  # Statistiche per ogni elemento dell'array V

    def calcola(self, i, j, op):
        for indice in sorted([i, j]):
            self.V[indice].acquireReadLock()

        try:
            if op in ['/', '%'] and self.V[j].getDato() == 0:
                dprint(f"Divisione per zero: non eseguo l'operazione {op} su V[{i}] e V[{j}]")
                raise ZeroDivisionError()
            else:
                return self.operazioni[op](self.V[i].getDato(), self.V[j].getDato())

        finally:
            self.V[i].releaseReadLock()
            self.V[j].releaseReadLock()

    def aggiorna(self, i, j, k, op):
        indici_ordinati = sorted([i, j, k])
        for indice in indici_ordinati:
            if indice == k:
                self.V[indice].acquireWriteLock()
            else:
                self.V[indice].acquireReadLock()
        try:
            self.V[k].setDato(self.calcola(i, j, op))
            self.statistiche[op] += 1
            self.element_stats[k] += 1  # Aggiorna statistiche per elemento
        except ZeroDivisionError:
            dprint(f"Thread {current_thread()}: salto una operazione di divisione per zero")
        finally:
            for indice in indici_ordinati:
                if indice == k:
                    self.V[indice].releaseWriteLock()
                else:
                    self.V[indice].releaseReadLock()

    def stampa_statistiche(self):
        dprint("Statistiche operazioni:")
        for op, count in self.statistiche.items():
            dprint(f"Operazione {op}: {count} volte")
        dprint("Statistiche elementi:")
        for i, count in enumerate(self.element_stats):
            dprint(f"Elemento V[{i}]: aggiornato {count} volte")

    def azzera_statistiche(self):
        self.statistiche = {op: 0 for op in self.statistiche}
        self.element_stats = [0] * 10

class Calcolatrice:
    def __init__(self):
        self.IC = InteriCombinati()
        self.B = BlockingQueue(10)
        self.elaboratori = [Thread(target=self.elabora) for _ in range(4)]
        self.produttori = [Thread(target=self.produce) for _ in range(2)]
        self.running = True  # Variabile di controllo per arrestare i thread

        for thread in self.elaboratori + self.produttori:
            thread.start()

    def elabora(self):
        while self.running:
            try:
                i, j, k, op = self.B.get()  # Estraiamo l'operazione
                self.IC.aggiorna(i, j, k, op)
            except Queue.Empty:
                pass

    def produce(self):
        ops = ['+', '-', '*', '/', '%']
        while self.running:
            i, j, k = random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)
            op = random.choice(ops)
            self.B.put((i, j, k, op))  # Inseriamo l'operazione

    def stop(self):
        self.running = False
        for thread in self.elaboratori + self.produttori:
            thread.join()  # Attendiamo la terminazione di tutti i thread

# Esempio di uso
calcolatrice = Calcolatrice()

# Arresta l'esecuzione dopo un po'
sleep(5)
calcolatrice.stop()

# Stampa le statistiche
calcolatrice.IC.stampa_statistiche()

# Azzera le statistiche
calcolatrice.IC.azzera_statistiche()
