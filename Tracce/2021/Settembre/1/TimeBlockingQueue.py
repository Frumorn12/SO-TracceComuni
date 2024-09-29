import random, time, traceback, sys
from threading import Thread, RLock, Condition, get_ident

debug = False


def printDebug():
    if debug:
        print("DEBUG %d" % get_ident())


'''
    I thread di tipo Timer si occupano di eliminare gli elementi che sono giunti a scadenza
'''


class Timer(Thread):
    def __init__(self, t, timedQueue, e):
        Thread.__init__(self)
        self.t = t
        self.timedQueue = timedQueue
        self.e = e

    def run(self):
        time.sleep(self.t)

        self.timedQueue._TimedBlockingQueue__remove(self.e)
        print("PUFF! Time out scaduto per elemento %r" % self.e)



class TimedBlockingQueue:
    def __init__(self, dim):
        self.lock = RLock()
        '''
            Condizione per gestire thread che non possono inserire nuovi elementi per via del buffer pieno
        '''
        self.full_condition = Condition(self.lock)
        '''
            Condizione per gestire thread che non possono estrarre nuovi elementi per via del buffer vuoto
        '''
        self.empty_condition = Condition(self.lock)
        '''
            Condizione per gestire thread che attendono che determinati elementi vengano processati (waitFor)
        '''
        self.timerCondition = Condition(self.lock)
        self.ins = 0
        self.out = 0
        self.slotPieni = 0
        self.dim = dim
        self.thebuffer = []
        '''
            In questo array tengo traccia degli elementi che sono usciti dalla coda
            a causa di una scadenza
        '''
        self.scaduti = []
        '''
            Contatore che tiene traccia di quanti thread aspettano su waitFor
        '''
        self.inWait = 0


        # Dizionario per tenere traccia dei tempi di scadenza
        self.timers = {}


    def put(self, c):
        with self.lock:
            while self.slotPieni == self.dim:
                self.full_condition.wait()

            if self.slotPieni == 0:
                self.empty_condition.notify_all()

            self.thebuffer.append(c)
            self.slotPieni += 1

    '''
        timedPut funziona come put, ma si noti che viene avviata una istanza di Timer, che rimuoverÃ  c alla scadenza.
        si noti che self.lock viene preso due volte di fila: una volta dentro timedPut e subito dopo dentro il codice si self.put
        La cosa non crea problemi poichÃ¨ self.lock Ã¨ un RLock()
    '''

    def timedPut(self, c, time):
        with self.lock:
            self.put(c)
            expiration = time + time.time()
            self.timers[c] = expiration
            timer = Timer(time, self, c)
            timer.start()

    def waitFor(self, e):
        with self.lock:
            self.inWait += 1
            try:
                if e in self.thebuffer:
                    while e in self.thebuffer:
                        self.timerCondition.wait()
                    '''
                        Come faccio a sapere se l'elemento 'e' Ã¨ sparito da self.thebuffer
                        per via di una scadenza, o per via di una get?
                        Dipende da se l'elemento e si trova in self.scaduti oppure no.
                    '''
                    return not e in self.scaduti
                else:
                    '''
                        Caso in cui l'elemento e non Ã¨ in self.thebuffer 
                        e (probabilmente) non c'Ã¨ mai stato
                    '''
                    return False
            finally:
                self.inWait -= 1
                '''
                    Tutte le volte che i thread in attesa su waitFor vanno a 0, 
                    ripulisco self.scaduti, poichÃ¨ le scadenze passate non mi servono piÃ¹
                '''
                if self.inWait == 0:
                    self.scaduti.clear()

    def get(self):

        with self.lock:
            while self.slotPieni == 0:
                self.empty_condition.wait()

            returnValue = self.thebuffer.pop(0)

            if self.slotPieni == self.dim:
                self.full_condition.notifyAll()

            self.slotPieni -= 1
            self.timerCondition.notifyAll()

            return returnValue

    '''
        Rimuove dalla coda uno specifico elemento e. Notifica eventuali thread che aspettavano con waitFor
        e siccome si libera un posto, notifica anche su full_condition. Se l'elemento non c'Ã¨, remove non fa nulla senza dare errori.
        Questo metodo Ã¨ privato ed Ã¨ usato solo per gestire la rimozione in caso di scadenza
    '''

    def __remove(self, e):
        with self.lock:
            if e in self.thebuffer:
                ''' Si sta liberando finalmente un posto passando dallo stato di "coda piena" allo stato di "coda con qualche slot libero?"'''
                if self.slotPieni == self.dim:
                    self.full_condition.notifyAll()

                self.thebuffer.remove(e)
                self.slotPieni -= 1
                self.scaduti.append(e)
            self.timerCondition.notifyAll()

    '''
        Mostra il contenuto della coda
    '''

    def show(self):

        with self.lock:
            print("[" + "_**_".join(self.thebuffer) + "]")

    def getExpiryTime(self, e):
        with self.lock:
            if e in self.timers:
                time_left = self.timers[e] - time.time()
                return max(0, time_left)
            return -1

    def getNextTimeoutElement(self):
        with self.lock:
            if len(self.timers) == 0:
                return -1
            # Devo retituire il riferimento al prossimo elemento di e di cui scade il tempo
            min_time = float('inf')
            next_element = None
            for e in self.timers:
                time_left = self.timers[e] - time.time()
                if time_left < min_time:
                    min_time = time_left
                    next_element = e

            return next_element





'''
    Classe Consumer di test
'''


class Consumer(Thread):

    def __init__(self, buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            printDebug()
            time.sleep(random.random() * 2)
            self.queue.get()
            self.queue.show()


'''
    Classe producer di test
'''


class Producer(Thread):

    def __init__(self, buffer):
        self.queue = buffer
        self.counter = 0
        Thread.__init__(self)

    def run(self):
        while True:
            printDebug()
            s = "TO-%s-%d" % (self.name, self.counter)
            self.queue.timedPut(s, random.random() * 2)
            time.sleep(random.random())
            print("Esito attesa %r" % self.queue.waitFor(s))
            self.queue.put("NO-%s-%d" % (self.name, self.counter))
            self.queue.show()
            self.counter += 1


#
#  Main di prova
#
buffer = TimedBlockingQueue(10)

producers = [Producer(buffer) for _ in range(5)]
consumers = [Consumer(buffer) for _ in range(5)]

for p in producers:
    p.start()

for c in consumers:
    c.start()
