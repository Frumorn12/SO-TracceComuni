from threading import RLock, Thread, Condition
from queue import Queue, Empty
from random import random, randint
from time import sleep


# Classe Frame che rappresenta un frame con un MAC sorgente, un MAC destinazione e un messaggio
class Frame:
    def __init__(self, s, d, m):
        self.MAC_Sorgente = s
        self.MAC_Destinazione = d
        self.messaggio = m
        # Porta di provenienza del frame, impostata dal worker
        self.__provenienza = None


# Classe Porta che rappresenta una porta con un buffer di ingresso e un buffer di uscita
class Porta:
    def __init__(self):
        self.N = 20  # Dimensione del buffer
        self.in_ = Queue(self.N)  # Buffer di ingresso
        self.out = Queue(self.N)  # Buffer di uscita


# Classe Switch che rappresenta uno switch con più porte e una tabella di switch
class Switch:
    def __init__(self, NPorte, NWorker):
        self.switchTable = {}  # Tabella di switch (MAC -> Porta)
        self.lock = RLock()  # Lock per la sincronizzazione
        self.condition = Condition(self.lock)  # Condition per l'attesa bloccante
        self.porte = [Porta() for i in range(0, NPorte)]  # Inizializzazione delle porte
        self.workers = [Worker(self) for i in range(0, NWorker)]  # Creazione dei worker
        # Avvio dei thread worker
        for i in range(0, NWorker):
            self.workers[i].start()

    # Metodo per aggiornare la tabella di switch con una nuova chiave
    def __aggiornaChiave(self, s, p):
        with self.lock:
            self.switchTable[s] = p

    # Metodo per leggere una chiave dalla tabella di switch
    def __leggiChiave(self, s):
        with self.lock:
            return self.switchTable.get(s)

    # Metodo per inviare un frame su una determinata porta
    def sendFrame(self, f: Frame, p: Porta):
        with self.condition:
            p.in_.put(f)  # Inserisce il frame nel buffer di ingresso della porta
            self.condition.notify_all()  # Notifica i worker che un frame è disponibile

    # Metodo per ricevere un frame dal buffer di uscita della porta
    def receiveFrame(self, p: Porta):
        return p.out.get()  # Estrae il frame dal buffer di uscita

    # Metodo che gestisce l'instradamento del frame (unicast o broadcast)
    def __putFrame(self, f: Frame):
        port = self.__leggiChiave(f.MAC_Destinazione)  # Controlla se c'è una porta per il MAC di destinazione
        if port is not None:
            # Se esiste, esegue unicast
            port.out.put(f)
            print("UNICAST %s : %s->%s = %s" % (port, f.MAC_Sorgente, f.MAC_Destinazione, f.messaggio))
        else:
            # Se non esiste, esegue broadcast
            print("BROADCAST")
            for i in range(0, len(self.porte)):
                if self.porte[i] != f.__provenienza:  # Evita di ritrasmettere alla porta di provenienza
                    self.porte[i].out.put(f)
                    print("%s : %s->%s" % (self.porte[i], f.MAC_Sorgente, f.MAC_Destinazione))

    # Metodo per ottenere un frame da uno dei buffer di ingresso (attesa bloccante se vuoto)
    def __getFrame(self):
        with self.condition:
            while True:
                for i in range(0, len(self.porte)):
                    try:
                        f = self.porte[i].in_.get_nowait()  # Prova a ottenere un frame senza bloccare
                        if f is not None:
                            f.__provenienza = self.porte[i]  # Imposta la porta di provenienza
                            self.__aggiornaChiave(f.MAC_Sorgente, f.__provenienza)  # Aggiorna la tabella di switch
                            return f
                    except Empty:
                        pass
                # Se nessun frame è disponibile, attende finché non ne arriva uno
                self.condition.wait()


# Classe Worker che esegue l'elaborazione dei frame prelevati dallo switch
class Worker(Thread):
    def __init__(self, s: Switch):
        super(Worker, self).__init__()
        self.s = s  # Lo switch a cui è associato il worker

    def run(self):
        while True:
            # Preleva un frame dallo switch
            f = self.s._Switch__getFrame()
            if f is not None:
                # Esegue il routing del frame
                self.s._Switch__putFrame(f)


# Classe LinkSimulator che simula un link fisico tra due switch
class LinkSimulator(Thread):
    def __init__(self, S1: Switch, P1: Porta, S2: Switch, P2: Porta):
        super(LinkSimulator, self).__init__()
        self.S1 = S1  # Primo switch
        self.P1 = P1  # Porta sul primo switch
        self.S2 = S2  # Secondo switch
        self.P2 = P2  # Porta sul secondo switch

    def run(self):
        while True:
            try:
                # Prende un frame da P1 di S1 e lo inserisce in P2 di S2
                frame1 = self.S1.receiveFrame(self.P1)
                self.S2.sendFrame(frame1, self.P2)

                # Prende un frame da P2 di S2 e lo inserisce in P1 di S1
                frame2 = self.S2.receiveFrame(self.P2)
                self.S1.sendFrame(frame2, self.P1)

            except Empty:
                pass
            sleep(random())  # Simula latenza di rete


# Classe EndPointSimulator che simula un endpoint connesso a una porta dello switch
class EndPointSimulator(Thread):
    def __init__(self, S: Switch, porta: Porta, MAC: str):
        super(EndPointSimulator, self).__init__()
        self.S = S  # Switch a cui è connesso l'endpoint
        self.porta = porta  # Porta fisica di connessione
        self.MAC = MAC  # MAC address dell'endpoint

    def run(self):
        while True:
            # Genera un frame con un MAC di destinazione casuale
            destinazione = destinations[randint(0, len(destinations) - 1)]
            frame = Frame(self.MAC, destinazione, "Message from " + self.MAC)

            # Invia il frame attraverso lo switch
            self.S.sendFrame(frame, self.porta)

            # Prova a ricevere i frame destinati a questo endpoint
            try:
                received_frame = self.S.receiveFrame(self.porta)
                if received_frame:
                    print("Received at {}: {} -> {} : {}".format(
                        self.MAC, received_frame.MAC_Sorgente,
                        received_frame.MAC_Destinazione, received_frame.messaggio))
            except Empty:
                pass

            sleep(random())  # Simula attività di rete casuale


# Lista di destinazioni (MAC addresses) simulate
destinations = [
    "01:01:01:01:01:01",
    "01:01:01:01:01:02",
    "01:01:01:01:01:03",
    "01:01:01:01:01:04",
    "01:01:01:01:01:05"
]


# Classe FrameGenerator che genera frame casuali e li invia a una porta dello switch
class FrameGenerator(Thread):
    def __init__(self, s: Switch, porta: Porta, mac: str):
        super(FrameGenerator, self).__init__()
        self.porta = porta
        self.mac = mac
        self.s = s

    def run(self):
        while (True):
            sleep(random())
            # Genera e invia un frame con un MAC casuale di destinazione
            self.s.sendFrame(Frame(self.mac, destinations[randint(0, 4)], "Lorem Ipsum:" + chr(randint(64, 84))),
                             self.porta)


# Funzione principale che avvia la simulazione
if __name__ == '__main__':
    # Inizializza uno switch con 5 porte e 2 worker
    cisco2900 = Switch(5, 2)

    # Crea e avvia generatori di frame su ciascuna porta
    generators = [FrameGenerator(cisco2900, cisco2900.porte[i], "01:01:01:01:01:0" + chr(ord("1") + i)) for i in
                  range(0, 5)]
    for gen in generators:
        gen.start()

    # Simulazione di un collegamento tra due switch
    S2 = Switch(5, 2)
    link_simulator = LinkSimulator(cisco2900, cisco2900.porte[0], S2, S2.porte[0])
    link_simulator.start()

    # Simulazione di un endpoint conness
