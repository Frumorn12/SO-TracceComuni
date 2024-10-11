#!/usr/bin/python3

from threading import RLock, Condition, Thread, current_thread, get_ident
from time import sleep
from random import randint, random

#
# Funzione di stampa sincronizzata
#
plock = RLock()


def prints(s):
    plock.acquire()
    print(s)
    plock.release()


#
# Restituisce il Current THREAD ID (TID) di sistema formattato
#
def getThreadId():
    return f"{current_thread().ident:,d}"


#
# Errore WrongValue provocato se setDato imposta un valore negativo
#
class WrongValue(Exception):
    pass


class NoLockAcquired(Exception):
    pass


class ReadWriteLockEvoluto:
    #
    # Contatore necessario per assegnare un id a ciascun ReadWriteLockEvoluto
    #
    globalSerial = 0
    #
    # globalLock Ã¨ necessario per sincronizzare l'assegnazione dell'id nel costruttore, evitando che due istanze di classe prendano lo stesso seriale per via di una race condition tra due thread.
    # Bisogna usare un lock unico per qualunque thread invochi un costruttore, non va bene self.lockAusiliario poichÃ¨ quest'ultimo sarÃ  sempre diverso
    # per ogni istanza della classe.
    #
    # Esempio: thread1 invoca  a = ReadWriteLockCondiviso(), thread2 invoca b = ReadWriteLockCondiviso().  b e a hanno due diversi self.lockAusiliario, ma uno stesso globalLock.
    #
    #
    globalLock = RLock()

    def __init__(self):
        self.dato = 0
        # self.ceUnoScrittore = False, non serve, useremo self.scrittore
        # self.numLettori = 0 non serve , useremo self.lettori
        self.lockAusiliario = RLock() # Lock ausiliario per sincronizzare l'accesso a self.lettori e self.scrittore (Punto 3) #!/usr/bin/python3

from threading import RLock, Condition, Thread, current_thread, get_ident
from time import sleep
from random import randint, random

#
# Funzione di stampa sincronizzata
#
plock = RLock()


def prints(s):
    plock.acquire()
    print(s)
    plock.release()


#
# Restituisce il Current THREAD ID (TID) di sistema formattato
#
def getThreadId():
    return f"{current_thread().ident:,d}"


#
# Errore WrongValue provocato se setDato imposta un valore negativo
#
class WrongValue(Exception):
    pass


class NoLockAcquired(Exception):
    pass


class ReadWriteLockEvoluto:
    #
    # Contatore necessario per assegnare un id a ciascun ReadWriteLockEvoluto
    #
    globalSerial = 0
    #
    # globalLock Ã¨ necessario per sincronizzare l'assegnazione dell'id nel costruttore, evitando che due istanze di classe prendano lo stesso seriale per via di una race condition tra due thread.
    # Bisogna usare un lock unico per qualunque thread invochi un costruttore, non va bene self.lockAusiliario poichÃ¨ quest'ultimo sarÃ  sempre diverso
    # per ogni istanza della classe.
    #
    # Esempio: thread1 invoca  a = ReadWriteLockCondiviso(), thread2 invoca b = ReadWriteLockCondiviso().  b e a hanno due diversi self.lockAusiliario, ma uno stesso globalLock.
    #
    #
    globalLock = RLock()

    def __init__(self):
        self.dato = 0
        # self.ceUnoScrittore = False, non serve, useremo self.scrittore
        # self.numLettori = 0 non serve , useremo self.lettori
        self.lockAusiliario = RLock()
        self.conditionAusiliaria = Condition(self.lockAusiliario)
        self.max_readers = 10
        self.enable = True
        # Mi creo un seriale per ordinare l'acquisizione del lock
        with ReadWriteLockEvoluto.globalLock:
            ReadWriteLockEvoluto.globalSerial += 1
            self.serial = ReadWriteLockEvoluto.globalSerial
        #
        # Tengo traccia dei lettori attuali associando ad ogni lettore un numero di acquire
        #
        # Esempio: self.lettori[TID] = 3  ==> Il thread TID ha preso 3 volte il lock in lettura
        #
        # Utilizzeremo get_ident() per avere il TID del thread corrente.
        #
        self.lettori = {}
        # Tengo traccia del TID dello scrittore attuale
        self.scrittore = None
        # Questa variabile viene utilizzata per conteggiare quante volte lo scrittore corrente ha preso il lock
        self.num_volte_preso_lock_scrittore = 0

    def setReaders(self, max_readers: int):
        with self.lockAusiliario:
            #
            # Potrebbero esserci lettori in attesa che potrebbero sfruttare i nuovi posti.
            # Notifico questi eventuali lettori.
            #
            if max_readers > self.max_readers:
                self.conditionAusiliaria.notifyAll()
            self.max_readers = max_readers

    def enableWriters(self, enable: bool):
        with self.lockAusiliario:
            self.enable = enable
            #
            # Qualche scrittore che ha trovato il lock bloccato potrebbe
            # beneficiare dello sblocco. Notifica in accordo a questo.
            #
            if enable:
                self.conditionAusiliaria.notifyAll()

    #
    # Si noti che la condizione di accesso Ã¨ stata cambiata: se sei lo scrittore corrente oppure sei giÃ  un lettore, la wait() viene saltata, ma viene conteggiato
    # l'accesso aggiornando self.lettori
    #
    def acquireReadLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            #
            # In Python si puÃ² spezzare una espressione booleana su piÃ¹ righe se la si racchiude tra tonde
            #
            while (
                    (self.scrittore != TID or TID not in self.lettori) and
                    (self.scrittore != None or len(self.lettori) >= self.max_readers)
            ):
                self.conditionAusiliaria.wait()
            if TID not in self.lettori:
                self.lettori[TID] = 0
            self.lettori[TID] += 1

    def releaseReadLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            #
            # Controllo ausiliario non richiesto dalla traccia, ma utile: non puoi chiamare release se non sei giÃ  tra i lettori
            #
            if TID not in self.lettori:
                raise NoLockAcquired
            self.lettori[TID] -= 1
            if self.lettori[TID] == 0:
                del self.lettori[TID]
            if len(self.lettori) < self.max_readers:
                self.conditionAusiliaria.notifyAll()

    #
    # Si noti che la condizione di accesso Ã¨ stata cambiata: se sei lo scrittore corrente, la wait() viene saltata, ma viene conteggiato
    # l'accesso aggiornando self.lettori, cosÃ¬ risolvendo il Punto 3
    #
    def acquireWriteLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            while (
                    (self.scrittore != TID) and
                    (self.scrittore != None or len(self.lettori) > 0 or not self.enable) and
                    #
                    # Piccola accortezza aggiuntiva: se sono l'unico lettore posso prendere il lock in scrittura
                    #
                    not (len(self.lettori) == 1 and TID in self.lettori)
            ):
                self.conditionAusiliaria.wait()
            self.scrittore = TID
            self.num_volte_preso_lock_scrittore += 1

    #
    # Controllo ausiliario non richiesto dalla traccia, ma utile: non puoi chiamare release se non sei lo scrittore
    #
    def releaseWriteLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            if self.scrittore != TID:
                raise NoLockAcquired()
            self.conditionAusiliaria.notifyAll()
            self.num_volte_preso_lock_scrittore -= 1
            if self.num_volte_preso_lock_scrittore == 0:
                self.scrittore = None

    def getDato(self):
        TID = get_ident()
        #
        # Accediamo a self.lettori e self.scrittore che sono strutture dati interne al ReadWriteLock e dunque necessitano di sincronizzazione
        #
        with self.lockAusiliario:
            if not TID in self.lettori and TID != self.scrittore:
                raise NoLockAcquired()
        return self.dato

    def setDato(self, i):
        #
        # Dato puÃ² essere solo positivo
        #
        if i < 0:
            raise WrongValue
        TID = get_ident()
        with self.lockAusiliario:
            if TID != self.scrittore:
                raise NoLockAcquired()
        self.dato = i


class Scrittore(Thread):
    maxIterations = 1000

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Lo scrittore %s chiede di scrivere." % getThreadId())
            #
            # Raddoppio aggiunto per testare la rientranza (Punto 3)
            #
            self.dc.acquireWriteLock()
            self.dc.acquireWriteLock()
            prints("Lo scrittore %s comincia a scrivere." % getThreadId())
            sleep(random())
            v = random() * 10
            self.dc.setDato(v)
            prints(f"Lo scrittore {getThreadId()} ha scritto il valore {v:.2f} su {self.dc}")
            self.dc.acquireWriteLock()
            self.dc.releaseWriteLock()
            prints("Lo scrittore %s termina di scrivere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1


class Lettore(Thread):
    maxIterations = 100

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Il lettore %s Chiede di leggere." % getThreadId())
            #
            # Raddoppio aggiunto per testare la rientranza (Punto 3)
            #
            self.dc.acquireReadLock()
            self.dc.acquireReadLock()
            prints("Il lettore %s Comincia a leggere." % getThreadId())
            sleep(random())
            prints(f"Il lettore {getThreadId} legge {self.dc.getDato()} da {self.dc}")
            self.dc.releaseReadLock()
            self.dc.releaseReadLock()
            prints("Il lettore %s termina di leggere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1


#
# Codici ANSI per avere le scritte colorate su stampa console
#
redANSIcode = '\033[31m'
blueANSIcode = '\033[34m'
greenANSIcode = '\033[32m'
resetANSIcode = '\033[0m'


class TestaMetodi(Thread):
    maxIterations = 500

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = self.maxIterations

    def run(self):
        enable = True
        while self.iterations > 0:
            sleep(random() * 2)
            self.dc.enableWriters(enable)
            prints(f"{redANSIcode}SCRITTORI ABILITATI su DATO:{self.dc}: {enable:d}{resetANSIcode}")
            #
            # Inverte il valore di enable, cosÃ¬ al prossimo giro imposta False se a questo
            # giro Ã¨ stato impostato True. E viceversa
            #
            enable = not enable
            sleep(random() * 2)
            #
            # Imposta i readers a un valore random.
            # Si noti che max_readers = 0 => nessun lettore
            # puÃ² accedere.
            #
            v = randint(0, 10)
            self.dc.setReaders(v)
            prints(f"{blueANSIcode}LETTORI ABILITATI su DATO:{self.dc}: {v}{resetANSIcode}")

            self.iterations -= 1


class Copiatore(Thread):

    def __init__(self, dc: ReadWriteLockEvoluto, dc2: ReadWriteLockEvoluto):
        super().__init__()
        #
        # Torna utile che dc corrisponda a self.dati[0], mentre dc2 corrisponderÃ  a self.dati[1]
        #
        self.dati = [dc, dc2]

    def run(self):

        while True:
            # sleep(randint(0,5)/10)

            #
            # Sorteggia quale tra DC e DC2 devono essere sorgente o destinazione.
            #

            source = randint(0, 1)
            destination = 1 - source
            datoSorgente = self.dati[source]
            datoDestinazione = self.dati[destination]
            #
            # Uso trucco dell'ordinamento lessicografico per garantire che non ci sia deadlock
            #
            if datoSorgente.serial < datoDestinazione.serial:
                datoSorgente.acquireReadLock()
                datoDestinazione.acquireWriteLock()
            else:
                datoDestinazione.acquireWriteLock()
                datoSorgente.acquireReadLock()

            prints(f"{greenANSIcode}Copia {datoSorgente.getDato()} -> {datoDestinazione.getDato()}{resetANSIcode}")
            datoDestinazione.setDato(datoSorgente.getDato())

            datoSorgente.releaseReadLock()
            datoDestinazione.releaseWriteLock()


if __name__ == '__main__':
    dc = ReadWriteLockEvoluto()
    dc2 = ReadWriteLockEvoluto()

    NUMS = 5
    NUML = 10

    scrittori = [Scrittore(dc) for i in range(NUMS)]
    lettori = [Lettore(dc) for i in range(NUML)]
    for s in scrittori:
        s.start()
    for l in lettori:
        l.start()

    #
    # Simuliamo la presenza di lettori e scrittori che lavorino su dc2
    #
    scrittori2 = [Scrittore(dc2) for i in range(NUMS)]
    lettori2 = [Lettore(dc2) for i in range(NUML)]
    for s in scrittori2:
        s.start()
    for l in lettori2:
        l.start()

        # Lancia due istanze di TestaMetodi anonime

    TestaMetodi(dc).start()
    TestaMetodi(dc2).start()
    copiatori = [Copiatore(dc, dc2) for _ in range(10)]
    for c in copiatori:
        c.start()


        self.conditionAusiliaria = Condition(self.lockAusiliario)
        self.max_readers = 10
        self.enable = True
        # Mi creo un seriale per ordinare l'acquisizione del lock
        with ReadWriteLockEvoluto.globalLock:
            ReadWriteLockEvoluto.globalSerial += 1
            self.serial = ReadWriteLockEvoluto.globalSerial
        #
        # Tengo traccia dei lettori attuali associando ad ogni lettore un numero di acquire
        #
        # Esempio: self.lettori[TID] = 3  ==> Il thread TID ha preso 3 volte il lock in lettura
        #
        # Utilizzeremo get_ident() per avere il TID del thread corrente.
        #
        self.lettori = {}
        # Tengo traccia del TID dello scrittore attuale
        self.scrittore = None
        # Questa variabile viene utilizzata per conteggiare quante volte lo scrittore corrente ha preso il lock
        self.num_volte_preso_lock_scrittore = 0

    def setReaders(self, max_readers: int):
        with self.lockAusiliario:
            #
            # Potrebbero esserci lettori in attesa che potrebbero sfruttare i nuovi posti.
            # Notifico questi eventuali lettori.
            #
            if max_readers > self.max_readers:
                self.conditionAusiliaria.notifyAll()
            self.max_readers = max_readers

    def enableWriters(self, enable: bool):
        with self.lockAusiliario:
            self.enable = enable
            #
            # Qualche scrittore che ha trovato il lock bloccato potrebbe
            # beneficiare dello sblocco. Notifica in accordo a questo.
            #
            if enable:
                self.conditionAusiliaria.notifyAll()

    #
    # Si noti che la condizione di accesso Ã¨ stata cambiata: se sei lo scrittore corrente oppure sei giÃ  un lettore, la wait() viene saltata, ma viene conteggiato
    # l'accesso aggiornando self.lettori
    #
    def acquireReadLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            #
            # In Python si puÃ² spezzare una espressione booleana su piÃ¹ righe se la si racchiude tra tonde
            #
            while (
                    (self.scrittore != TID or TID not in self.lettori) and
                    (self.scrittore != None or len(self.lettori) >= self.max_readers)
            ):
                self.conditionAusiliaria.wait()
            if TID not in self.lettori:
                self.lettori[TID] = 0
            self.lettori[TID] += 1

    def releaseReadLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            #
            # Controllo ausiliario non richiesto dalla traccia, ma utile: non puoi chiamare release se non sei giÃ  tra i lettori
            #
            if TID not in self.lettori:
                raise NoLockAcquired
            self.lettori[TID] -= 1
            if self.lettori[TID] == 0:
                del self.lettori[TID]
            if len(self.lettori) < self.max_readers:
                self.conditionAusiliaria.notifyAll()

    #
    # Si noti che la condizione di accesso Ã¨ stata cambiata: se sei lo scrittore corrente, la wait() viene saltata, ma viene conteggiato
    # l'accesso aggiornando self.lettori, cosÃ¬ risolvendo il Punto 3
    #
    def acquireWriteLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            while (
                    (self.scrittore != TID) and
                    (self.scrittore != None or len(self.lettori) > 0 or not self.enable) and
                    #
                    # Piccola accortezza aggiuntiva: se sono l'unico lettore posso prendere il lock in scrittura
                    #
                    not (len(self.lettori) == 1 and TID in self.lettori)
            ):
                self.conditionAusiliaria.wait()
            self.scrittore = TID
            self.num_volte_preso_lock_scrittore += 1

    #
    # Controllo ausiliario non richiesto dalla traccia, ma utile: non puoi chiamare release se non sei lo scrittore
    #
    def releaseWriteLock(self):
        TID = get_ident()
        with self.lockAusiliario:
            if self.scrittore != TID:
                raise NoLockAcquired()
            self.conditionAusiliaria.notifyAll()
            self.num_volte_preso_lock_scrittore -= 1
            if self.num_volte_preso_lock_scrittore == 0:
                self.scrittore = None

    def getDato(self):
        TID = get_ident()
        #
        # Accediamo a self.lettori e self.scrittore che sono strutture dati interne al ReadWriteLock e dunque necessitano di sincronizzazione
        #
        with self.lockAusiliario:
            if not TID in self.lettori and TID != self.scrittore:
                raise NoLockAcquired()
        return self.dato

    def setDato(self, i):
        #
        # Dato puÃ² essere solo positivo
        #
        if i < 0:
            raise WrongValue
        TID = get_ident()
        with self.lockAusiliario:
            if TID != self.scrittore:
                raise NoLockAcquired()
        self.dato = i


class Scrittore(Thread):
    maxIterations = 1000

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Lo scrittore %s chiede di scrivere." % getThreadId())
            #
            # Raddoppio aggiunto per testare la rientranza (Punto 3)
            #
            self.dc.acquireWriteLock()
            self.dc.acquireWriteLock()
            prints("Lo scrittore %s comincia a scrivere." % getThreadId())
            sleep(random())
            v = random() * 10
            self.dc.setDato(v)
            prints(f"Lo scrittore {getThreadId()} ha scritto il valore {v:.2f} su {self.dc}")
            self.dc.acquireWriteLock()
            self.dc.releaseWriteLock()
            prints("Lo scrittore %s termina di scrivere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1


class Lettore(Thread):
    maxIterations = 100

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            prints("Il lettore %s Chiede di leggere." % getThreadId())
            #
            # Raddoppio aggiunto per testare la rientranza (Punto 3)
            #
            self.dc.acquireReadLock()
            self.dc.acquireReadLock()
            prints("Il lettore %s Comincia a leggere." % getThreadId())
            sleep(random())
            prints(f"Il lettore {getThreadId} legge {self.dc.getDato()} da {self.dc}")
            self.dc.releaseReadLock()
            self.dc.releaseReadLock()
            prints("Il lettore %s termina di leggere." % getThreadId())
            sleep(random() * 5)
            self.iterations += 1


#
# Codici ANSI per avere le scritte colorate su stampa console
#
redANSIcode = '\033[31m'
blueANSIcode = '\033[34m'
greenANSIcode = '\033[32m'
resetANSIcode = '\033[0m'


class TestaMetodi(Thread):
    maxIterations = 500

    def __init__(self, dc):
        super().__init__()
        self.dc = dc
        self.iterations = self.maxIterations

    def run(self):
        enable = True
        while self.iterations > 0:
            sleep(random() * 2)
            self.dc.enableWriters(enable)
            prints(f"{redANSIcode}SCRITTORI ABILITATI su DATO:{self.dc}: {enable:d}{resetANSIcode}")
            #
            # Inverte il valore di enable, cosÃ¬ al prossimo giro imposta False se a questo
            # giro Ã¨ stato impostato True. E viceversa
            #
            enable = not enable
            sleep(random() * 2)
            #
            # Imposta i readers a un valore random.
            # Si noti che max_readers = 0 => nessun lettore
            # puÃ² accedere.
            #
            v = randint(0, 10)
            self.dc.setReaders(v)
            prints(f"{blueANSIcode}LETTORI ABILITATI su DATO:{self.dc}: {v}{resetANSIcode}")

            self.iterations -= 1


class Copiatore(Thread):

    def __init__(self, dc: ReadWriteLockEvoluto, dc2: ReadWriteLockEvoluto):
        super().__init__()
        #
        # Torna utile che dc corrisponda a self.dati[0], mentre dc2 corrisponderÃ  a self.dati[1]
        #
        self.dati = [dc, dc2]

    def run(self):

        while True:
            # sleep(randint(0,5)/10)

            #
            # Sorteggia quale tra DC e DC2 devono essere sorgente o destinazione.
            #

            source = randint(0, 1)
            destination = 1 - source
            datoSorgente = self.dati[source]
            datoDestinazione = self.dati[destination]
            #
            # Uso trucco dell'ordinamento lessicografico per garantire che non ci sia deadlock
            #
            if datoSorgente.serial < datoDestinazione.serial:
                datoSorgente.acquireReadLock()
                datoDestinazione.acquireWriteLock()
            else:
                datoDestinazione.acquireWriteLock()
                datoSorgente.acquireReadLock()

            prints(f"{greenANSIcode}Copia {datoSorgente.getDato()} -> {datoDestinazione.getDato()}{resetANSIcode}")
            datoDestinazione.setDato(datoSorgente.getDato())

            datoSorgente.releaseReadLock()
            datoDestinazione.releaseWriteLock()


if __name__ == '__main__':
    dc = ReadWriteLockEvoluto()
    dc2 = ReadWriteLockEvoluto()

    NUMS = 5
    NUML = 10

    scrittori = [Scrittore(dc) for i in range(NUMS)]
    lettori = [Lettore(dc) for i in range(NUML)]
    for s in scrittori:
        s.start()
    for l in lettori:
        l.start()

    #
    # Simuliamo la presenza di lettori e scrittori che lavorino su dc2
    #
    scrittori2 = [Scrittore(dc2) for i in range(NUMS)]
    lettori2 = [Lettore(dc2) for i in range(NUML)]
    for s in scrittori2:
        s.start()
    for l in lettori2:
        l.start()

        # Lancia due istanze di TestaMetodi anonime

    TestaMetodi(dc).start()
    TestaMetodi(dc2).start()
    copiatori = [Copiatore(dc, dc2) for _ in range(10)]
    for c in copiatori:
        c.start()

