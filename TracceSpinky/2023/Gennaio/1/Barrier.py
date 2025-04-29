

import math
import multiprocessing
from threading import Condition, Lock, Thread
import time
import random


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
    
    '''
    Punto 1
    Come primo requisito, la classe ExtendedBarrier dovrà estendere il codice iniziale di Barrier con i metodi
    finito e aspettaEbasta(self). Il primo metodo incrementa di uno i threadArrivati ed esce; il secondo metodo si
    mette in attesa che i threadArrivati raggiungano la soglia prescritta per poi uscire quando questa condizione si verifica, ma
    senza incrementare il numero di threadArrivati.
    '''
    def finito (self):
        with self.lock:
            self.threadArrivati += 1
            if self.threadArrivati == self.soglia:
                self.condition.notifyAll()
    
    def aspettaEbasta (self):
        with self.lock:
            while self.threadArrivati < self.soglia:
                self.condition.wait()
    
    '''
    Punto 2
    Sempre agendo sulla classe ExtendedBarrier, fattorizza il metodo wait, sfruttando i metodi finito e
    aspettaEbasta che hai appena implementato.
    Per fattorizzzare si intende l'ereditarietà della classe ExtendedBarrier dalla classe Barrier...
    '''
    def wait(self):
        # Qui non va messo il with self.lock perché va in deadlock perchè le funzioni che sto chiamando in questa funzione già prendono di per se il lock non è necessario quindi prenderlo di nuovo
        self.finito()
        self.aspettaEbasta()

'''
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
thread prescritti.
'''

class DoppiaBarriera:
    def __init__(self,n0,n1): #Costruttore
        self.barriere = [ExtendedBarrier(n0), ExtendedBarrier(n1)] 
    
    def finito(self,numSoglia):
        self.barriere[numSoglia].finito() #Incrementa i threadArrivati sulla soglia numSoglia 

    def aspettaEbasta(self,numSoglia):
        self.barriere[numSoglia].aspettaEbasta()
    
    def wait(self,numSoglia):
        self.barriere[numSoglia].wait()
    
    def waitAll(self):
        self.barriere[0].finito() #Incrementa i threadArrivati sulla soglia 0
        self.barriere[1].finito() #Incrementa i threadArrivati sulla soglia 1
        self.barriere[0].aspettaEbasta() #Attende che i thread arrivati su numSoglia 0 raggiungano la soglia impostata
        self.barriere[1].aspettaEbasta() #Attende che i thread arrivati su numSoglia 1 raggiungano la soglia impostata 

    
    
class ThreadBarrier(Thread):
    def __init__(self, barrier, numero):
        Thread. __init__(self)
        self.barrier = barrier
        self.numeroBarriera = numero #Soglia random 

    def run(self):
        print(f"Thread {self.name} in attesa")
        
        self.barrier.wait(self.numeroBarriera) 
        print(f"Thread {self.name} ha superato la barriera")
        time.sleep(1)
        print(f"Thread {self.name} ha terminato")
    
        
if __name__ == "__main__":
    n0 = 5
    n1 = 5
    barrier = DoppiaBarriera(n0, n1)
    
    threads = []
    for i in range(5):
        thread = ThreadBarrier(barrier, 0)
        thread.start()
        threads.append(thread)
    for i in range(5):
        thread = ThreadBarrier(barrier, 1)
        thread.start()
        threads.append(thread) 


    for thread in threads:
        thread.join() 
