from threading import RLock,Condition, Thread
import random
import time

"""
Nel codice della classe `BlockingStack`, ci sono due condizioni principali: `conditionTuttoPieno` e `conditionTuttoVuoto`. Queste condizioni vengono utilizzate per sincronizzare i thread che interagiscono con lo stack, garantendo che le operazioni di inserimento e prelievo siano sicure e rispettino i vincoli dello stack (dimensione massima e non vuoto).

### 1. **`conditionTuttoPieno`**
   - **Scopo**: Questa condizione viene utilizzata per gestire i thread che vogliono aggiungere elementi allo stack (`put` o `putN`) ma trovano lo stack pieno.
   - **Quando viene usata**:
     - Nei metodi come `put` e `putN`, i thread verificano se lo stack ha raggiunto la dimensione massima (`self.size`). Se lo stack è pieno, i thread si mettono in attesa su questa condizione con `self.conditionTuttoPieno.wait()`.
   - **Quando viene notificata**:
     - Quando lo stack non è più pieno (ad esempio, dopo un'operazione di prelievo con `take` o dopo un `flush`), viene chiamato `self.conditionTuttoPieno.notify()` o `notify_all()` per svegliare i thread in attesa.
   - **Esempio**:
     - Un produttore vuole aggiungere un elemento, ma lo stack è pieno. Si blocca in attesa finché un consumatore non preleva un elemento, liberando spazio.

---

### 2. **`conditionTuttoVuoto`**
   - **Scopo**: Questa condizione viene utilizzata per gestire i thread che vogliono prelevare elementi dallo stack (`take`) ma trovano lo stack vuoto.
   - **Quando viene usata**:
     - Nei metodi come `take`, i thread verificano se lo stack è vuoto (`len(self.elementi) == 0`). Se lo stack è vuoto, i thread si mettono in attesa su questa condizione con `self.conditionTuttoVuoto.wait()`.
   - **Quando viene notificata**:
     - Quando lo stack non è più vuoto (ad esempio, dopo un'operazione di inserimento con `put` o `putN`), viene chiamato `self.conditionTuttoVuoto.notify()` o `notify_all()` per svegliare i thread in attesa.
   - **Esempio**:
     - Un consumatore vuole prelevare un elemento, ma lo stack è vuoto. Si blocca in attesa finché un produttore non aggiunge un elemento.

---

### Perché sono necessarie entrambe?
- **`conditionTuttoPieno`** e **`conditionTuttoVuoto`** servono a gestire due situazioni opposte:
  - `conditionTuttoPieno` si occupa di sincronizzare i produttori quando lo stack è pieno.
  - `conditionTuttoVuoto` si occupa di sincronizzare i consumatori quando lo stack è vuoto.
- Senza queste condizioni, i thread potrebbero continuare a eseguire operazioni non valide (ad esempio, aggiungere elementi a uno stack pieno o prelevare da uno stack vuoto), causando errori o comportamenti indesiderati.

---

### Come funzionano insieme?
1. **Produttore**:
   - Se lo stack è pieno, si blocca su `conditionTuttoPieno`.
   - Quando un consumatore preleva un elemento, il produttore viene notificato e può aggiungere nuovi elementi.

2. **Consumatore**:
   - Se lo stack è vuoto, si blocca su `conditionTuttoVuoto`.
   - Quando un produttore aggiunge un elemento, il consumatore viene notificato e può prelevare l'elemento.

Questa sincronizzazione garantisce che i produttori e i consumatori lavorino in modo coordinato, rispettando i limiti dello stack.
"""

class BlockingStack:
    
    def __init__(self,size):
        self.size = size
        self.elementi = []
        self.lock = RLock()
        self.conditionTuttoPieno = Condition(self.lock) 
        self.conditionTuttoVuoto = Condition(self.lock)
        self.fifo = False 
    
    '''
    Punto 1
    Aggiungi alla struttura dati BlockingStack il metodo flush(self). Tale metodo elimina tutti gli elementi
    attualmente presenti nel BlockingStack. (Capire le condition)
    '''
    def flush(self):
        with self.lock:
            while len(self.elementi) > 0:
                self.elementi.pop()
            self.conditionTuttoVuoto.notify_all()
            self.conditionTuttoPieno.notify_all()
    
    """
    Punto 2
    Aggiungi alla struttura dati BlockingStack il metodo putN(self,L : List). Tale metodo inserisce tutti gli
    elementi della lista L all’interno di self. Se self non dispone di almeno len(L) posti liberi, ci si pone in attesa
    bloccante finché tali posti non si rendano disponibili, effettuando a seguire l’inserimento degli elementi di L.
    """
    
    def putN(self,L):
        with self.lock:
            while len(self.elementi) + len(L) > self.size: # controllo se ci sono abbastanza posti 
                self.conditionTuttoPieno.wait()
            for i in L:
                self.elementi.append(i)
            self.conditionTuttoVuoto.notify_all()

    '''
    Punto 3
    Dal momento che un BlockingStack è basato su una politica di inserimento ed estrazione di tipo LIFO, è evidente che
    esso soffre di problemi di starvation. Introduci dunque il metodo setFIFO(self,onOff : bool). Quando onOff
    = True, il BlockingStack corrente deve cominciare a funzionare come una BlockingQueue, e cioè con politica di
    inserimento ed estrazione FIFO. Se invece onOff = False, il BlockingStack deve tornare a funzionare come uno stack
    LIFO. L’invocazione di setFIFO deve avere effetto anche sull’ordine di estrazione degli elementi ormai già inseriti.
    '''

    def setFIFO(self,onOff):
        with self.lock:
            self.fifo = onOff 
    



        
    def __find(self,t):
        try:
            # .index restituisce l'indice dell'elemento t nella lista self.elementi
            if self.elementi.index(t) >= 0: # se l'elemento non è presente l'eccezione ValueError viene sollevata
                return True
        except(ValueError):
            return False
    
    def put(self,t):
    
        self.lock.acquire()
        while len(self.elementi) == self.size:
            self.conditionTuttoPieno.wait()
        self.conditionTuttoVuoto.notify_all()
        self.elementi.append(t)
        self.lock.release()
    
    
    def take(self,t=None):
        self.lock.acquire() # Non faccio with perchè non voglio che il lock venga rilasciato in caso di eccezione
        try:
            if t == None:
                while len(self.elementi) == 0:
                    self.conditionTuttoVuoto.wait()
                
                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()
                if self.fifo:
                    t = self.elementi[0]
                    self.elementi.remove(t)
                else:
                    t = self.elementi[-1]
                    self.elementi.remove(t) 
            else:
                while not self.__find(t):
                    self.conditionTuttoVuoto.wait()
                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()
                self.elementi.remove(t)    
                return t    
        finally:
            self.lock.release()
    
    

class Consumer(Thread): 
    
    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random()*2)
            print(f"Estratto elemento {self.queue.take()}")
            


class Producer(Thread):

    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self): 
        while True:
            time.sleep(random.random() * 2)
            self.queue.put(self.name)
            
#  Main
#
buffer = BlockingStack(10)

producers = [Producer(buffer) for x in range(5)]
consumers = [Consumer(buffer) for x in range(3)]

for p in producers:
    p.start()

for c in consumers:
    c.start()
    
