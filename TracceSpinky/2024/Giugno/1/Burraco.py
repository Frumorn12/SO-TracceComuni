from threading import Barrier, Thread, Lock, Condition
from queue import Queue
import time

'''
Il codice fornito Ã¨ ispirato al mondo dei giochi di carte online, come il Burraco. In questo genere di giochi, ogni giocatore che vuole fare una partita
puÃ² partecipare a un tavolo da 4 persone formato in base agli altri giocatori attualmente online che hanno fatto anch'essi richiesta di essere abbinati a un tavolo di gioco.

La classe AmbienteGioco gestisce le richieste di gioco dei giocatori, fornisce i metodi per abbinare i giocatori in squadre e sincronizza la formazione e la presa visione delle squadre. 
I giocatori, rappresentati dalla classe ThreadGiocatore, richiedono periodicamente di giocare e attendono di essere abbinati. 
La classe ThreadAbbinatore forma continuamente nuove squadre prelevando giocatori dalla coda delle richieste.
L'esecuzione principale crea un ambiente di gioco, avvia dei thread per ogni giocatore e un thread abbinatore.
'''

class AmbienteGioco:
    def __init__(self, num_giocatori=4):

        # Coda per le richieste di gioco
        self.coda_richieste_gioco = Queue()

        # code per punto 3 
        self.coda_richieste_gioco_2 = Queue()
        self.coda_richieste_gioco_3 = Queue()
        self.coda_richieste_gioco_4 = Queue()
        self.coda_richieste_gioco_5 = Queue()
         

        # Lock per proteggere self.abbinamenti_giocatori
        self.lock = Lock()

        # Condizione per segnalare quando una partita Ã¨ pronta
        self.partita_pronta = Condition(self.lock)

        #
        # Lista per memorizzare gli abbinamenti dei giocatori. 
        # In questa variabile vengono messi i partecipanti alla partita corrente
        # 
        self.abbinamenti_giocatori = []
        self.num_giocatori = num_giocatori 

        # Barriera per sincronizzare la presa visione della squadra da parte dei giocatori (4 giocatori + 1 ThreadAbbinatore)
        # self.barriera_presa_visione = Barrier(self.num_giocatori + 1) 

    #
    #  Il giocatore id invoca questo metodo quando vuole partecipare a una partita online con altri 3 giocatori.
    #  voglio_giocare restituisce l'elenco degli id dei giocatori che parteciperanno alla partita
    #

    def voglio_giocare(self, id, dimensione=-1): 
        if dimensione == -1:
            dimensione = self.num_giocatori 

        if dimensione == 2:
            self.coda_richieste_gioco_2.put(id)
        elif dimensione == 3:
            self.coda_richieste_gioco_3.put(id)
        elif dimensione == 4:
            self.coda_richieste_gioco_4.put(id)
        elif dimensione == 5:
            self.coda_richieste_gioco_5.put(id)
        else:
            self.coda_richieste_gioco.put(id)
        #
        # Fase 1: Aggiunge il giocatore alla coda delle richieste di gioco
        #

        #
        # Fase 2: il giocatore attende di comparire nell'elenco degli abbinamenti correnti
        #
        with self.lock:
            # Attende che il giocatore venga abbinato in una squadra
            while id not in self.abbinamenti_giocatori:
                self.partita_pronta.wait()

        #
        # Fase 3: il giocatore corrente Ã¨ negli abbinamenti, ricopio gli abbinamenti attuali, 
        # e poi attendo sulla barriera per segnalare che ho finito
        #
        temp_squadra = self.abbinamenti_giocatori
        # Aspetta che tutti i giocatori prendano visione della squadra
        self.barriera_presa_visione.wait()

        return temp_squadra

    #
    # Questo metodo Ã¨ invocato dal thread Abbinatore e serve a formare un tavolo di gioco a partire da quattro richieste di gioco
    # prelevate dalla coda delle richieste
    #
    def forma_una_squadra(self):
        
        # Lista temporanea per memorizzare i giocatori che formano una squadra
        temp_giocatori = []
        #
        # FASE 1: prelevo quattro richieste da quattro giocatori e formo una partita
        #

        # Punto 2
        for i in range (5):
            if (i == 0):
                try :
                    for i in range(self.num_giocatori): 
                        # Preleva 4 giocatori dalla coda delle richieste
                        temp_giocatori.append(self.coda_richieste_gioco_2.get(timeout=1))
                except Exception as e:
                    for i in range(2 - len(temp_giocatori)):
                        temp_giocatori.append(-i-1)
                with self.lock: 
                    for e in temp_giocatori:
                        self.abbinamenti_giocatori.append(e)
                    self.partita_pronta.notify_all()
                    

    
        try :
            for i in range(self.num_giocatori): 
                # Preleva 4 giocatori dalla coda delle richieste
                temp_giocatori.append(self.coda_richieste_gioco.get(timeout=1)) 
        except Exception as e:
            # Se non ci sono abbastanza giocatori, esce dal ciclo, e appendo numeri negativi crescenti
            # per indicare che non ci sono abbastanza giocatori
            for i in range(self.num_giocatori - len(temp_giocatori)):   
                temp_giocatori.append(-i-1) 
       

        #
        # FASE 2: aggiorno abbinamenti_giocatori e notifico che una partita Ã¨ pronta
        #
        with self.lock:
            # Aggiunge i giocatori alla lista degli abbinamenti
            for e in temp_giocatori:
                self.abbinamenti_giocatori.append(e)
            # Notifica tutti i giocatori in attesa
            self.partita_pronta.notify_all()

        # FASE 3: Aspetta che tutti i giocatori prendano visione della squadra
        self.barriera_presa_visione.wait()

        # FASE 4: Resetta la lista degli abbinamenti per la prossima partita
        with self.lock:
            self.abbinamenti_giocatori = []

        # Resetta la barriera per la prossima partita
        

class ThreadGiocatore(Thread):
    def __init__(self, id_giocatore, ambiente):
        super().__init__()
        self.id_giocatore = id_giocatore
        self.ambiente = ambiente

    def run(self):
        while True:
            print(f"Giocatore {self.id_giocatore} vuole giocare.")
            # Richiede di giocare e attende di essere abbinato in una squadra
            giocatori = self.ambiente.voglio_giocare(self.id_giocatore)
            print(f"Giocatore {self.id_giocatore} Ã¨ stato abbinato in una partita con {giocatori}")
            #
            # Fingo di giocare
            #
            time.sleep(5)

class ThreadAbbinatore(Thread):
    def __init__(self, ambiente):
        super().__init__()
        self.ambiente = ambiente

    def run(self):
        while True:
            # Forma una squadra di giocatori
            self.ambiente.forma_una_squadra()
            # Simula un ritardo tra la formazione di un tavolo di gioco e un altro
            time.sleep(5)

# Creazione dell'ambiente di gioco
ambiente = AmbienteGioco()
N = 20 
# Creazione e avvio dei thread giocatori
thread_giocatori = [ThreadGiocatore(id_giocatore, ambiente) for id_giocatore in range(1, N)]
for thread in thread_giocatori:
    thread.start()

# Creazione e avvio del thread abbinatore
thread_abbinatore = ThreadAbbinatore(ambiente)
thread_abbinatore.start()

