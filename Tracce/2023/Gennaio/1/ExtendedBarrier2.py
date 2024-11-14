

import math
import multiprocessing
from threading import Condition, Lock, Thread
import time


class Barrier:

    def __init__(self,n):

        self.soglia = n
        self.threadArrivati = 0
        self.lock = Lock()
        self.condition = Condition(self.lock)

    def wait(self):
        with self.lock:
            self.threadArrivati += 1

            if self.threadArrivati == self.soglia:
                self.condition.notifyAll()

            while self.threadArrivati < self.soglia:
                self.condition.wait()

class ExtendedBarrier(Barrier):
    """
    Punto 1
    Come primo requisito, la classe ExtendedBarrier dovrà estendere il codice iniziale di Barrier con i metodi
    finito e aspettaEbasta(self). Il primo metodo incrementa di uno i threadArrivati ed esce; il secondo metodo si
    mette in attesa che i threadArrivati raggiungano la soglia prescritta per poi uscire quando questa condizione si verifica, ma
    senza incrementare il numero di threadArrivati.

    """
    def finito(self):
        with self.lock:
            self.threadArrivati += 1

    def aspettaEbasta(self):
        with self.lock:
            while self.threadArrivati < self.soglia:
                self.condition.wait()

    """ 
    Punto 2
    Sempre agendo sulla classe ExtendedBarrier, fattorizza il metodo wait, sfruttando i metodi finito e
    aspettaEbasta che hai appena implementato
    
    
    """

    def wait(self):
        self.finito()
        if self.threadArrivati == self.soglia:
            self.condition.notify_all()
        self.aspettaEbasta()

"""
Punto 3
Progetta e implementa la classe DoppiaBarriera. La classe deve consentire di incrementare e attendere due soglie in
contemporanea: la soglia S0 e la soglia S1. Il costruttore di DoppiaBarriera riceve due valori di soglia n0 e n1 che
saranno rispettivamente associati alla soglia S0 e alla soglia S1.
In altre parole questa classe deve fornire i metodi:
finito(self,numSoglia)
Incrementa i threadArrivati sulla soglia numSoglia, dove numSoglia può valere 0 oppure 1 a seconda che si voglia
scegliere la soglia S0 o la soglia S1.
aspettaEbasta(self,numSoglia)
Attende che i thread arrivati su numSoglia raggiungano la soglia impostata, dove numSoglia può valere 0 oppure 1,
per poi uscire.
wait(self,numSoglia)
Incrementa i threadArrivati associati alla soglia numSoglia, quindi attende che i thread arrivati su numSoglia
raggiungano la soglia prescritta per poi uscire.
waitAll(self)
Incrementa di uno i thread arrivati su entrambe le soglie e aspetta che entrambe le soglie siano raggiunte dal numero di
thread prescritti
"""

class DoppiaBarriera:
    def __init__(self,n0,n1):
        self.soglia0 = n0
        self.soglia1 = n1
        self.threadArrivati0 = 0
        self.threadArrivati1 = 0
        self.lock = Lock()
        self.condition = Condition(self.lock)


