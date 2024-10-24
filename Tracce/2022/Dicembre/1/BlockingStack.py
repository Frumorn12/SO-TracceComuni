from threading import RLock, Condition, Thread
import random
import time


class BlockingStack:

    def __init__(self, size):
        self.size = size
        self.elementi = []
        self.lock = RLock()
        self.conditionTuttoPieno = Condition(self.lock)
        self.conditionTuttoVuoto = Condition(self.lock)
        self.fifo_mode = False  # Variabile per controllare se FIFO è attivo o meno

    def __find(self, t):
        try:
            if self.elementi.index(t) >= 0:
                return True
        except(ValueError):
            return False

    def put(self, t):
        self.lock.acquire()
        while len(self.elementi) == self.size:
            self.conditionTuttoPieno.wait()
        self.conditionTuttoVuoto.notify_all()
        self.elementi.append(t)
        self.lock.release()

    def take(self, t=None):
        self.lock.acquire()
        try:
            if t is None:
                while len(self.elementi) == 0:
                    self.conditionTuttoVuoto.wait()

                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()

                # Controlla se siamo in modalità FIFO
                if self.fifo_mode:
                    return self.elementi.pop(0)  # Estrazione FIFO: primo elemento
                else:
                    return self.elementi.pop()  # Estrazione LIFO: ultimo elemento

            else:
                while not self.__find(t):
                    self.conditionTuttoVuoto.wait()
                if len(self.elementi) == self.size:
                    self.conditionTuttoPieno.notify()
                self.elementi.remove(t)
                return t
        finally:
            self.lock.release()

    # Metodo flush per eliminare tutti gli elementi
    def flush(self):
        self.lock.acquire()
        self.elementi = []
        self.lock.release()

    # Metodo per inserire una lista di elementi, bloccandosi se necessario
    def putN(self, L):
        self.lock.acquire()
        while len(self.elementi) + len(L) > self.size:
            self.conditionTuttoPieno.wait()
        for x in L:
            self.elementi.append(x)
        self.conditionTuttoVuoto.notify_all()
        self.lock.release()

    # Metodo per attivare/disattivare la modalità FIFO
    def setFIFO(self, onOff: bool):
        self.lock.acquire()
        self.fifo_mode = onOff
        self.lock.release()


class Consumer(Thread):

    def __init__(self, buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random() * 2)
            print(f"Estratto elemento {self.queue.take()}")


class Producer(Thread):

    def __init__(self, buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random() * 2)
            self.queue.put(self.name)


#  Main
#
buffer = BlockingStack(10)

# Imposta FIFO su True o False per testare i due comportamenti
buffer.setFIFO(True)  # Per abilitare FIFO
# buffer.setFIFO(False)  # Per abilitare LIFO

producers = [Producer(buffer) for x in range(5)]
consumers = [Consumer(buffer) for x in range(3)]

for p in producers:
    p.start()

for c in consumers:
    c.start()
