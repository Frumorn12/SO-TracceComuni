import time
import random
from threading import Condition, RLock, Thread
from time import sleep

'''
    Una semplice classe blocking queue che implementa il metodo put e get in forma bloccante
    La dimensione della coda Ã¨ fissata in fase di inizializzazione
'''


class BlockingQueue:

    def __init__(self, size):

        # lista che contiene gli elementi inseriti nella coda
        self.elementi = []

        # dimensione massima della coda
        self.size = size

        # RLock che viene utilizzato per disciplinare le invocazioni simultanee ai metodi put e get
        self.lock = RLock()

        # Condizione che viene utilizzata per notificare i thread che attendono che la coda non sia piÃ¹ tutta piena
        self.conditionTuttoPieno = Condition(self.lock)

        # Condizione che viene utilizzata per notificare i thread che attendono che la coda non sia piÃ¹ tutta vuota
        self.conditionTuttoVuoto = Condition(self.lock)


        # Variabili per il logging
        self.logging = False # variabile che indica se il logging Ã¨ attivo o meno
        self.log = [] # lista che contiene i messaggi di log

        self.logMax = 0 # numero massimo di messaggi di log che possono essere memorizzati

    #
    # Inserisce un elemento nella coda
    # Se la coda Ã¨ piena, il thread che invoca il metodo put viene bloccato
    # Se la coda non Ã¨ piena, il thread che invoca il metodo put inserisce l'elemento nella coda e notifica un thread che attende che la coda non sia piÃ¹ tutta vuota
    #
    def put(self, t):
        with self.lock:
            #
            # Se non ci sono slot liberi, il thread che invoca il metodo put viene bloccato
            #
            while len(self.elementi) == self.size:
                self.conditionTuttoPieno.wait()
            #
            # Questo if serve per evitare notify ridondanti
            # Non ci possono essere consumatori in attesa a meno che, un attimo prima della append(t) la coda non fosse totalmente vuota
            # Se non ci sono consumatori in attesa, non c'Ã¨ bisogno di notificare nessuno
            # Il codice Ã¨ corretto anche senza questo if, ma ci saranno notify anche quando non necessari
            #
            if len(self.elementi) == 0:
                self.conditionTuttoVuoto.notify()
            self.elementi.append(t)
            self._log("put", t) # logga l'azione di inserimento

    #
    # Estrae un elemento dalla coda
    # Se la coda Ã¨ vuota, il thread che invoca il metodo get viene bloccato
    # Se la coda contiene almeno un elemento, il thread che invoca il metodo get estrae l'elemento dalla coda e notifica un thread che attende che la coda non sia piÃ¹ tutta piena
    #
    def get(self):
        with self.lock:
            #
            # Se non ci sono elementi da estrarre, il thread che invoca il metodo get viene bloccato
            #
            while len(self.elementi) == 0:
                self.conditionTuttoVuoto.wait()
            #
            # Questo if serve per evitare notify ridondanti
            # Non ci possono essere produttori in attesa a meno che, un attimo prima della pop(0) la coda non fosse totalmente piena
            # Se non ci sono produttori in attesa, non c'Ã¨ bisogno di notificare nessuno
            # Il codice Ã¨ corretto anche senza questo if, ma ci saranno notify anche quando non necessari
            #
            if len(self.elementi) == self.size:
                self.conditionTuttoPieno.notify()
            self._log("get", self.elementi[0])
            return self.elementi.pop(0)


    def start_logging(self, M):
        with self.lock:
            self.logging = True
            self.logMax = M

    def stop_logging(self):
        with self.lock:
            self.logging = False
            self.log = []

    def _log(self, action, element):
        with self.lock:
            if self.logging:
                self.log.append((action, element, time.time()))
                if len(self.log) > self.logMax:
                    self.log.pop(0)

    def read_get_log (self,o): #restituisce il tempo in cui l'oggetto o risulta essere stato prelevato per l'ultima volta dalla coda.
        with self.lock:
            if self.logging == False: raise Exception("Logging non attivo")
            for i in range(len(self.log)-1, -1, -1):
                if self.log[i][0] == "get" and self.log[i][1] == o:
                    return self.log[i][2]
            return 0

    def read_put_log (self,o): #restituisce il tempo in cui l'oggetto o risulta essere stato inserito per l'ultima volta nella coda.
        with self.lock:
            if self.logging == False: raise Exception("Logging non attivo")
            for i in range(len(self.log)-1, -1, -1):
                if self.log[i][0] == "put" and self.log[i][1] == o:
                    return self.log[i][2]
            return 0

    def read_diff_log(self,o):
        with self.lock:
            if self.logging == False: raise Exception("Logging non attivo")
            get = self.read_get_log(o)
            put = self.read_put_log(o)
            if get == 0 or put == 0: return -1
            return get-put





#
# Esperimento di utilizzo della classe BlockingQueue
#
cuochi_e_piatti = {
    "Cannavacciuolo": ["Pizza", "Pasta", "Tiramisu", "Carbonara"],
    "Frankie": ["Hamburger", "Patatine", "Frappe"],
    "Sakura": ["Sushi", "Tempura", "Zuppa di Miso"],
}


#
# Il cuoco svolge il ruolo di produttore
#
class Cuoco(Thread):

    def __init__(self, q, nome):
        super().__init__()
        self.nastroPiatti = q
        self.name = nome

    #
    # Il ciclo di lavoro del Cuoco prevede che ogni 0.1 secondi inserisca un piatto nella coda
    #
    def run(self):
        numIterazioni = 50
        while numIterazioni > 0:
            numIterazioni -= 1
            sleep(0.1)
            listaPiattiDiQuestoCuoco = cuochi_e_piatti[self.name]
            piattoProdotto = listaPiattiDiQuestoCuoco[numIterazioni % len(listaPiattiDiQuestoCuoco)]
            self.nastroPiatti.put(piattoProdotto)
            self.nastroPiatti.read_put_log(piattoProdotto) # per testare il metodo read_put_log
            print(f"Cuoco {self.name} ha inserito CIBA: {piattoProdotto}")


#
# Il thread Cameriere svolge il ruolo di consumatore
#
class Cameriere(Thread):

    def __init__(self, q, nome):
        super().__init__()
        self.nastroPiatti = q
        self.name = nome

    #
    # Il ciclo di lavoro del Cameriere prevede che ogni 1 secondo si prelevi un piatto dalla coda
    #
    def run(self):
        numIterazioni = 50
        while numIterazioni > 0:
            numIterazioni -= 1
            sleep(1)
            piatto = self.nastroPiatti.get()
            self.nastroPiatti.get() # per testare il metodo get che restituisce l'elemento
            self.nastroPiatti.read_get_log(piatto) # per testare il metodo read_get_log
            print(f"Cameriere {self.name} ha prelevato CIBA: {piatto}")


def main():
    # Crea la coda con una dimensione di 5
    coda = BlockingQueue(5)

    # Crea cuochi e camerieri
    cuoco1 = Cuoco(coda, "Cannavacciuolo")
    cuoco2 = Cuoco(coda, "Frankie")
    cameriere1 = Cameriere(coda, "Mario")
    cameriere2 = Cameriere(coda, "Luigi")

    # Avvia i thread
    cuoco1.start()
    cuoco2.start()
    cameriere1.start()
    cameriere2.start()

    # Attiva e disattiva il logging casualmente durante l'esecuzione
    for _ in range(20):  # Esegui 20 cambiamenti casuali
        sleep(random.uniform(0.5, 2))  # Aspetta un intervallo di tempo casuale
        if random.choice([True, False]):
            # Attiva il logging
            M = random.randint(1, 10)  # Numero massimo di log
            coda.start_logging(M)
            print("Logging attivato con dimensione massima:", M)
        else:
            # Disattiva il logging
            coda.stop_logging()
            print("Logging disattivato")

    # Attendi che i thread finiscano
    cuoco1.join()
    cuoco2.join()
    cameriere1.join()
    cameriere2.join()

    # Mostra il log finale
    print("Log finale:", coda.log)


if __name__ == "__main__":
    main()