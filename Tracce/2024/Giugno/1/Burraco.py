from threading import Thread, Lock, Condition
from queue import Queue, Empty
import time
from collections import defaultdict

class AmbienteGioco:
    def __init__(self, timeout=5, num_abbinatori=1):
        # Coda per le richieste di gioco divisa per dimensione del tavolo
        self.code_richieste = defaultdict(Queue)
        self.timeout = timeout

        # Lock e Condition per proteggere gli abbinamenti e sincronizzare
        self.lock = Lock()
        self.partita_pronta = Condition(self.lock)

        # Abbinamenti correnti dei giocatori, divisi per dimensione del tavolo
        self.abbinamenti_giocatori = defaultdict(list)

        # Avvio dei thread abbinatori
        self.thread_abbinatori = [ThreadAbbinatore(self) for _ in range(num_abbinatori)]
        for thread in self.thread_abbinatori:
            thread.start()

    def voglio_giocare(self, id, dim):
        # Aggiunge il giocatore alla coda specifica per la dimensione del tavolo
        self.code_richieste[dim].put(id)

        # Attende di essere abbinato alla squadra
        with self.lock:
            while id not in self.abbinamenti_giocatori[dim]:
                self.partita_pronta.wait()

        # Ritorna la squadra formata
        with self.lock:
            temp_squadra = self.abbinamenti_giocatori[dim][:]

        return temp_squadra

    def forma_una_squadra(self, dim):
        temp_giocatori = []

        # Preleva giocatori fino a quando non ha abbastanza giocatori per formare un tavolo
        for i in range(dim):
            try:
                giocatore = self.code_richieste[dim].get(timeout=self.timeout)
                temp_giocatori.append(giocatore)
            except Empty:
                temp_giocatori.append(-1 * (i + 1))  # Assegna ID fittizio se non ci sono abbastanza giocatori

        with self.lock:
            # Aggiorna gli abbinamenti per la dimensione del tavolo
            self.abbinamenti_giocatori[dim] = temp_giocatori
            self.partita_pronta.notify_all()

        # Pulizia degli abbinamenti per il prossimo tavolo
        with self.lock:
            self.abbinamenti_giocatori[dim] = []


class ThreadGiocatore(Thread):
    def __init__(self, id_giocatore, ambiente, dim_tavolo, tempo_gioco):
        super().__init__()
        self.id_giocatore = id_giocatore
        self.ambiente = ambiente
        self.dim_tavolo = dim_tavolo
        self.tempo_gioco = tempo_gioco

    def run(self):
        while True:
            print(f"Giocatore {self.id_giocatore} vuole giocare a un tavolo da {self.dim_tavolo} giocatori.")
            giocatori = self.ambiente.voglio_giocare(self.id_giocatore, self.dim_tavolo)
            print(f"Giocatore {self.id_giocatore} è stato abbinato in una partita con {giocatori}")
            time.sleep(self.tempo_gioco)


class ThreadAbbinatore(Thread):
    def __init__(self, ambiente):
        super().__init__()
        self.ambiente = ambiente

    def run(self):
        while True:
            # Controlla se ci sono richieste di gioco per varie dimensioni di tavolo
            for dim in list(self.ambiente.code_richieste.keys()):
                if not self.ambiente.code_richieste[dim].empty():
                    self.ambiente.forma_una_squadra(dim)
            time.sleep(0.1)


# Parametri personalizzabili
numero_giocatori = 50  # Numero di giocatori
tempo_di_gioco = 5  # Tempo di gioco per ciascun giocatore (in secondi)
timeout_attesa = 0  # Timeout per l'abbinatore
numero_abbinatori = 3  # Numero di abbinatori da avviare

# Creazione dell'ambiente di gioco
ambiente = AmbienteGioco(timeout_attesa, numero_abbinatori)

# Creazione e avvio dei thread giocatori con dimensioni del tavolo variabili
thread_giocatori = [
    ThreadGiocatore(id_giocatore, ambiente, dim_tavolo, tempo_di_gioco)
    for id_giocatore, dim_tavolo in [(1, 2), (2, 2), (3, 3), (4, 3), (5, 3), (6, 4), (7, 4), (8, 4)]
]
for thread in thread_giocatori:
    thread.start()
