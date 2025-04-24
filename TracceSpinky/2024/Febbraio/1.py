from threading import Condition, RLock, Thread
from time import sleep, time 

'''
    Una semplice classe blocking queue che implementa il metodo put e get in forma bloccante
    La dimensione della coda Ã¨ fissata in fase di inizializzazione
'''
class BlockingQueue:

    def __init__(self,size):

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

        # Lista che contiene le operazioni di put e get eseguite (Punto 1)
        # esempio di cosa puo contenere : self. log = [("put", "Pasta", 19.20), ("get", "Pizza", 20.50), ("put", "Tiramisu", 10), ("get", "Hamburger")]
        self.log = [] 
        self.dimMassimaLog = 0 # dimensione massima del log 
        self.isLogging = False # flag per sapere se il logging Ã¨ attivo o meno 

    #
    # Inserisce un elemento nella coda
    # Se la coda Ã¨ piena, il thread che invoca il metodo put viene bloccato
    # Se la coda non Ã¨ piena, il thread che invoca il metodo put inserisce l'elemento nella coda e notifica un thread che attende che la coda non sia piÃ¹ tutta vuota
    #
    def put(self,t):
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

            if self.isLogging:
                # Se il log Ã¨ pieno, rimuovo la prima operazione
                if len(self.log) == self.dimMassimaLog:
                    self.log.pop(0)
                # Aggiungo l'operazione al log
                self.log.append(("put", self.elementi[0], time()))     
            self.elementi.append(t)

            

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
            
            if self.isLogging:
                # Se il log Ã¨ pieno, rimuovo la prima operazione
                if len(self.log) == self.dimMassimaLog:
                    self.log.pop(0)
                # Aggiungo l'operazione al log
                self.log.append(("get", self.elementi[0], time())) 

            return self.elementi.pop(0)
            



    # Punto 1 
    """
    start_logging(self,M). Dal momento in cui questa operazione viene chiamata ogni operazione di put e get viene registrata per come
    prescritto, fino ad un massimo di M operazioni. Le operazioni più vecchie devono essere via via cancellate: in altre parole bisogna conservare
    traccia solo delle ultime M operazioni.
    """
    
    def start_logging(self, M):
        with self.lock:
            self.dimMassimaLog = M
            self.log = []
            self.isLogging = True 
            print(f"Log avviato con dimensione massima {M}") 
    
    # Punto 2
    """
    stop_logging(self). Termina il logging e cancella tutto il diario delle operazioni precedentemente registrate.
    """

    def stop_logging(self):
        with self.lock:
            self.log = [] #Resetto la lista
            self.dimMassimaLog = 0 # Resetto la dimensione massima del log 
            self.isLogging = False #Imposto a False lo stato del logging
            print(f"Log terminato")
    
    '''
    # Punto 3
    read_get_log(self,o) -> float. Restituisce il tempo in cui l’oggetto o risulta essere stato prelevato per l’ultima volta dalla coda.
    Genera un'eccezione se il logger è disattivo, mentre restituisce 0 se nessun prelievo dell’oggetto risulta nel log.
    '''
    def read_get_log(self,o):
        with self.lock:
            if not self.isLogging:
                raise Exception("Logger disattivo")
            # Scorro il log al contrario per trovare l'oggetto
            tempo = 0
            for i in range(len(self.log)):
                if (self.log[i][0] == "get" and self.log[i][1] == o):
                    if tempo < self.log[i][2]:
                        tempo = self.log[i][2] 
            if tempo == 0:
                return 0 
            return tempo     
            
    def read_put_log(self,o):
        with self.lock:
            if not self.isLogging:
                raise Exception("Logger disattivo")
            # Scorro il log al contrario per trovare l'oggetto
            tempo = 9999999999999
            for i in range(len(self.log)):
                if (self.log[i][0] == "put" and self.log[i][1] == o):
                    if tempo > self.log[i][2]:
                        tempo = self.log[i][2] 
            
            if tempo == 9999999999999:
                return 0
            return tempo
    """
    read_diff_log(self,o) -> float. Restituisce la differenza temporale tra l’ultima volta in cui l’oggetto o è stato prelevato e quella
    in cui è stato inserito. Genera una eccezione se il logger è disattivo, mentre restituisce -1 se uno dei due tempi non risulta nel log.
    """
    def read_diff_log(self):
        with self.lock:
            if not self.isLogging:
                raise Exception("Logger disattivo")
            # Scorro il log al contrario per trovare l'oggetto
            tempo = 0
            for i in range(len(self.log)):
                if (self.log[i][0] == "get" and self.log[i][1] == o):
                    tempo = self.log[i][2]
                    break
            tempo2 = 0
            for i in range(len(self.log)):
                if (self.log[i][0] == "put" and self.log[i][1] == o):
                    tempo2 = self.log[i][2]
                    break
            if tempo == 0 or tempo2 == 0:
                return -1
            else:
                return tempo - tempo2  

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

    def __init__(self,q,nome):
        super().__init__()
        self.nastroPiatti = q
        self.name = nome
    #
    # Il ciclo di lavoro del Cuoco prevede che ogni 0.1 secondi inserisca un piatto nella coda
    #
    def run(self):

        numIterazioni = 500
        while numIterazioni > 0:
            numIterazioni -= 1
            sleep(0.1)
            listaPiattiDiQuestoCuoco = cuochi_e_piatti[self.name]
            piattoProdotto = listaPiattiDiQuestoCuoco[numIterazioni % len(listaPiattiDiQuestoCuoco)]
            self.nastroPiatti.put(piattoProdotto)
            print (f"Cuoco {self.name} ha inserito CIBA:{piattoProdotto}")
            
#
# Il thread Cameriere svolge il ruolo di consumatore
#
class Cameriere(Thread):

    def __init__(self,q,nome):
        super().__init__()
        self.nastroPiatti = q
        self.name = nome

    #
    # Il ciclo di lavoro del Cameriere prevede che ogni 1 secondo si prelevi un piatto dalla coda
    #
    def run(self):

        numIterazioni = 500
        while numIterazioni > 0:
            numIterazioni -= 1
            sleep(1)
            piatto = self.nastroPiatti.get()
            print (f"Cameriere {self.name} ha prelevato CIBA:{piatto}")

#
# Codice main di prova
# Questo if consente di evitare che il codice venga eseguito quando il modulo viene importato
# Il codice viene eseguito solo quando il modulo viene eseguito come programma principale
# 
if __name__ == "__main__":
    
    # crea una coda di dimensione 10
    q = BlockingQueue(10)
    
    #
    # Crea i cuochi in base a come sono definiti in cuochi_e_piatti e li avvia
    #
    for c in cuochi_e_piatti:
        newCuoco = Cuoco(q,c)
        newCuoco.start()
    #
    # Crea 10 camerieri e li avvia
    #
    for c in range(0,10):
        newCameriere = Cameriere(q,f"Cameriere-{c}")
        newCameriere.start()

