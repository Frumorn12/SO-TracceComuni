#!/usr/bin/env python
from threading import Thread, Condition, RLock, get_ident


class IllegalMonitorStateException(Exception):
    pass


globalInternalLock = RLock()


class FriendlyLock:
    internalSerialCounter = 0

    def __init__(self):
        super(FriendlyLock, self).__init__()
        self.internalLock = globalInternalLock
        self.internalCondition = Condition(self.internalLock)
        FriendlyLock.internalSerialCounter += 1
        self.serial = FriendlyLock.internalSerialCounter
        self.currentHolder = None
        self.holds = 0

    def acquire(self, l=None):
        if type(l) == FriendlyLock:
            if self.serial < l.serial:
                self.acquire()
                l.acquire()
            else:
                l.acquire()
                self.acquire()
        else:
            self.internalLock.acquire()
            while self.currentHolder is not None and self.currentHolder != get_ident():
                self.internalCondition.wait()
            self.currentHolder = get_ident()
            self.holds += 1
            self.internalLock.release()

    def release(self, l=None):
        if type(l) == FriendlyLock:
            self.release()
            l.release()
        else:
            self.internalLock.acquire()
            try:
                if self.currentHolder == get_ident():
                    self.holds -= 1
                    if self.holds == 0:
                        self.currentHolder = None
                        self.internalCondition.notify()
                else:
                    raise IllegalMonitorStateException()
            finally:
                self.internalLock.release()


class FriendlyCondition:
    def __init__(self, l):
        super(FriendlyCondition, self).__init__()
        self.joinedLocks = list()
        self.joinedLocks.append(l)
        self.internalLock = globalInternalLock
        self.internalConditions = list()

    def join(self, l):
        self.internalLock.acquire()
        self.joinedLocks.append(l)
        self.internalLock.release()

    def unjoin(self, l: FriendlyLock):
        self.internalLock.acquire()
        self.joinedLocks.remove(l)
        self.internalLock.release()

    def wait(self):
        self.internalLock.acquire()
        for i in self.joinedLocks:
            i.release()
        myCondition = Condition(self.internalLock)
        self.internalConditions.append(myCondition)
        myCondition.wait()
        for i in self.joinedLocks:
            i.acquire()
        self.internalLock.release()

    def notify(self):
        self.internalLock.acquire()
        toDelete = None
        for cond in self.internalConditions:
            cond.notify()
            toDelete = cond
            break
        if toDelete is not None:
            self.internalConditions.remove(toDelete)
        self.internalLock.release()

    def notifyAll(self):
        self.internalLock.acquire()
        for cond in self.internalConditions:
            cond.notify()
        self.internalConditions = list()
        self.internalLock.release()


class Attesa:
    serialCounter = 0

    def __init__(self, i, c):
        self.c = c
        self.soglia = i
        Attesa.serialCounter += 1
        self.serial = Attesa.serialCounter

    def __lt__(self, other):
        return self.soglia < other.soglia if self.soglia != other.soglia else self.serial < other.serial


class SharedInteger(object):

    def __init__(self):
        self.value = 0
        self.attese = list()
        self.lock = FriendlyLock()

    def signalWaiters(self):
        for a in self.attese:
            if self.value >= a.soglia:
                a.c.notifyAll()
            else:
                break

    def get(self):
        self.lock.acquire()
        try:
            return self.value
        finally:
            self.lock.release()

    def set(self, i):
        self.lock.acquire()
        self.value = i
        self.signalWaiters()
        self.lock.release()

    def inc(self, I):
        self.lock.acquire(I.lock)
        self.value += I.value
        self.signalWaiters()
        self.lock.release(I.lock)

    def inc_int(self, i: int):
        self.lock.acquire()
        self.value += i
        self.signalWaiters()
        self.lock.release()

    def waitForAtLeast(self, soglia):
        self.lock.acquire()
        try:
            cond = FriendlyCondition(self.lock)
            att = Attesa(soglia, cond)
            self.attese.append(att)
            self.attese = sorted(self.attese)
            while self.value < soglia:
                cond.wait()
            self.attese.remove(att)
            return self.value
        finally:
            self.lock.release()

    def setInTheFuture(self, I, soglia, valore):
        self.lock.acquire(I.lock)
        cond = FriendlyCondition(self.lock)
        cond.join(I.lock)
        att = Attesa(soglia, cond)
        I.attese.append(att)
        I.attese = sorted(I.attese)
        while I.value < soglia:
            cond.wait()
        I.attese.remove(att)
        self.value = valore
        self.signalWaiters()
        self.lock.release(I.lock)

    def sposta(self, I2, I3):
        """Sposta il valore di I3 da self a I2"""
        self.lock.acquire(I2.lock)
        I3.lock.acquire()
        try:
            if self.value >= I3.value:
                self.value -= I3.value
                I2.value += I3.value
                print(f"Ho spostato {I3.value} da self a I2. Self ora vale: {self.value}, I2 ora vale: {I2.value}")
            else:
                print(f"Non posso spostare {I3.value} perché self ha solo {self.value}")
            self.signalWaiters()
            I2.signalWaiters()
        finally:
            I3.lock.release()
            self.lock.release(I2.lock)


# Test del metodo sposta
def test_sposta():
    a = SharedInteger()
    b = SharedInteger()
    c = SharedInteger()

    a.set(1000)  # Impostiamo il valore iniziale di a
    b.set(500)  # Impostiamo il valore iniziale di b
    c.set(300)  # Impostiamo il valore iniziale di c

    print(f"Valori iniziali: a = {a.get()}, b = {b.get()}, c = {c.get()}")

    class ThreadSposta(Thread):
        def __init__(self):
            Thread.__init__(self)

        def run(self):
            print(f"Sono il thread {get_ident()} e sposterò il valore di C da A a B.")
            a.sposta(b, c)
            print(f"Thread {get_ident()}: A = {a.get()}, B = {b.get()}, C = {c.get()}")

    sposta_thread = ThreadSposta()
    sposta_thread.start()
    sposta_thread.join()

    print(f"Valori finali: a = {a.get()}, b = {b.get()}, c = {c.get()}")


test_sposta()
