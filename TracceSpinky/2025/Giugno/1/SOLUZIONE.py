# Questo programma implementa un semplice gioco multithread chiamato "Numero Basso".
# Ogni thread-giocatore sceglie un numero casuale tra 1 e 10. Vince chi ha scelto
# il numero piÃ¹ basso che non Ã¨ stato scelto da nessun altro. Un thread "Monitor"
# osserva la partita e stampa in tempo reale l'identificatore dei thread che hanno
# effettuato una giocata. Tutta la sincronizzazione tra i thread Ã¨ gestita con
# RLock e Condition per coordinare l'avvio, l'esecuzione e la conclusione della partita.
# La partita viene lanciata nel blocco principale, che istanzia la classe "NumeroBasso"
# e chiama il metodo "gioca" specificando il numero di giocatori.



"""
Punto 1.  
Personalizza  la  libreria  di  gioco  facendo  in  modo  che  per  ogni  partita  si  possa  personalizzare  il  range  di  numeri 
ammissibili e il numero di giocate che deve fare ogni giocatore, che potrà dunque essere anche maggiore di 1. 
Punto 2. 
Introduci la possibilità per ciascun giocatore di “sbirciare”, ma solo una e una sola volta, quanti numeri hanno già 
registrato almeno  n giocate. Tale funzionalità deve essere realizzata con il metodo sbircia(n) che restituisce 
un  intero  corrispondente  a  quanti  numeri  hanno  già  registrato  n  giocate.  Se  uno  stesso  thread  chiama  questo 
metodo più di una volta nell’arco di una partita, viene squalificato. Non è necessario che tu garantisca che le giocate 
non  cambino  tra  una  invocazione di  sbircia(n)e una  invocazione di  puntaNumero.  Modifica  la  strategia  di 
gioco dei giocatori per sfruttare la possibilità di “sbirciare”. 
Punto 3. 
Introduci il metodo attendi_e_gioca(n). Tale metodo va in attesa bloccante fintantoché qualcuno non gioca 
il numero n+1, dopodichè gioca il numero n. 
  


"""
from threading import Thread, RLock, Condition, current_thread
from random import randint

# differenza Rlock con Lock:
# RLock permette a un thread di acquisire lo stesso lock piÃ¹ volte senza causare un deadlock.
# Mentre Lock non lo permette, e se un thread tenta di acquisire un Lock che giÃ possiede, va in deadlock.

# Classe Player: ogni thread rappresenta un giocatore che punta un numero casuale tra 1 e 10
class Player(Thread):
    def __init__(self, nb):
        super().__init__()
        self.nb = nb  # Riferimento all'oggetto NumeroBasso

    def run(self):


        for i in range(0, self.nb.numeroGiocate): 
            sbircio = randint(1,3) 
            numero = randint(1, 10)  # Sceglie un numero  da giocare tra 1 e 10 
            if sbircio == 1 and self.nb.sbircia(numero) > 0 : # Se il numero è stato già giocato
                numero = numero - 1 if numero > 1 else 2 # mi conviene puntare il numero piu basso possibile 
            
            if numero == 2 :
                self.nb.attendi_e_gioca(numero)
            else:  
                self.nb.puntaNumero(numero)  # Punta un numero casuale quando il thread parte

# Classe Monitor: thread separato che stampa le giocate mano a mano che vengono fatte
class Monitor(Thread):
    def __init__(self, nb):
        super().__init__()
        self.nb = nb  # Riferimento all'oggetto NumeroBasso

    def run(self):
        self.nb.monitoraPartita()  # Monitora l'andamento della partita
        print("Partita terminata")  # Messaggio a fine partita

# Classe principale che gestisce la logica del gioco "Numero Basso"
class NumeroBasso:
    def __init__(self):
        self.giocate = []  # Inizializzato temporaneamente, sarÃ  un dizionario
        self.lock = RLock()  # Lock rientrante per proteggere le sezioni critiche
        self.threadGioca = Condition(self.lock)  # Condition per coordinare le giocate
        self.ultimeGiocate = []  # Lista dei thread che hanno appena giocato
        self.partitaInCorso = False  # Flag per indicare se la partita Ã¨ attiva
        self.nGiocate = 0  # Contatore delle giocate effettuate
        self.numeroGiocate = 0 # Numero di giocate per ogni giocatore PUNTO 1
        self.endGame = Condition(self.lock)  # Condition per notificare la fine partita ai player
        self.vincitore = None  # ID del thread vincitore
        self.giocatePlayer = []  # Dizionario per tenere traccia delle giocate di ogni player (PUNTO 1) 
        self.sbirciate = [] # PUNTO 2 Lista per tenere traccia dei thread che hanno giÃ  sbirciato 
        self.squalifica = [] # PUNTO 2 Lista squalificati
        self.nGiocateSqualificati = 0 # PUNTO 2 Contatore dei giocatori squalificati 
        self.databasa = [] # PUNTO 3 lista per tenere traccia delle giocate effettuate 
    
    # aggiunto per il PUNTO 1 G
    # quel = 1 è un controllino in piu. Significa che se io non metto il parametro G significa che fa 1 giocata.
    # Rende piu flessibile la funzione gioca che funziona anche con il vecchio formato 
    
    def gioca(self, N: int, G: int = 1) -> int:
        with self.lock:
            self.giocate = {}  # Dizionario: chiave = numero scelto, valore = lista di thread
            self.nGiocate = 0  # Azzeramento giocate
            self.nGiocateSqualificati = 0 # PUNTO 2 azzeramento contatore squalificati   
            self.numeroGiocate = G  # Numero di giocate per ogni giocatore PUNTO 1 
            self.partitaInCorso = True  # Inizio partita
            self.giocatePlayer = {}  # Inizializza il dizionario delle giocate dei player (PUNTO 1) 
            Monitor(self).start()  # Avvia un unico thread monitor

            for _ in range(0, N):  # Avvia N thread giocatori
                Player(self).start()

            # PUNTO 1. 
            # We have a problem guysssss
            # Le nGiocate < N non contano che i player posso fare piu di una giocata.
            # una soluzione potrebbe essere nGiocate < N * G 
            while (self.nGiocate + self.nGiocateSqualificati) < (N * self.numeroGiocate):  # Attende che tutti i giocatori abbiano giocato
                self.threadGioca.wait()

            self.partitaInCorso = False  # Fine della partita
            self.threadGioca.notify_all()  # Risveglia il monitor, se in attesa

            self.endGame.notify_all()  # Risveglia tutti i giocatori bloccati in attesa
            
            # Debug: stampa lo stato finale delle giocate 
            # print("GIOCATE")  # Stampa lo stato finale delle giocate 
            # for k in sorted(self.giocate):
            #     print(f"Numero {k} puntato da {len(self.giocate[k])} giocatori: {self.giocate[k]}") 
            # print("Non ci sono vincitori")  # Nessun numero Ã¨ stato puntato da un solo giocatore   
            # Determina il vincitore: primo numero con una sola puntata (piÃ¹ basso)
            for k in sorted(self.giocate):
                if len(self.giocate[k]) == 1: # Se per quel numro il numero di thread che hanno puntato è 1
                    print(f"Il vincitore Ã¨ il thread {self.giocate[k][0]} che ha puntato il numero {k}")
                    self.vincitore = self.giocate[k][0]
                    return self.vincitore
                
            
            return 0

    # Metodo chiamato da ogni thread giocatore per puntare un numero
    def puntaNumero(self, n: int): 
        with self.lock:
            if current_thread().ident in self.squalifica: # Se il thread è squalificato non può giocare 
                print(f"Thread {current_thread().ident} è squalificato e non può giocare")
                self.nGiocateSqualificati += 1 
                return
            # currentthread associa il thread corrente al numero puntato (Il thread può andare da 0-31)
            self.giocate.setdefault(n, []).append(current_thread().ident)  # Registra la puntata. Il setdefault serve per inizializzare la lista se il numero non Ã¨ ancora presente come chiave
            self.giocatePlayer.setdefault(current_thread().ident, []).append(n)  # Registra la giocata del player (PUNTO 1) 
            self.nGiocate += 1  # Incrementa il conteggio delle giocate
            self.threadGioca.notify_all()  # Notifica che una nuova giocata Ã¨ avvenuta
            self.ultimeGiocate.append(current_thread().ident)  # Registra lâ€™identificatore del thread
            # PUNTO 1 se il current thread ancora deve fare giocate, returno direttamente
            if len(self.giocatePlayer[current_thread().ident]) < self.numeroGiocate: 
                return # Torna subito se il player deve ancora fare giocate 
            
            print (f"Thread {current_thread().ident} ha finito le sue giocate e aspetta la fine della partita" )
            
            # Ogni Thread si fa le sue giocate, si ferma e non termina, aspetta la fine della partita, momento in cui tutti i thread hanno giocato si determina il vincitore e terminano.
            while self.partitaInCorso:  # Attende la fine della partita
                self.endGame.wait()

            return self.vincitore == current_thread().ident  # Ritorna True se il thread ha vinto

    def monitoraPartita(self):
        with self.lock:
            conta = 0  # Contatore giocate stampate
            while len(self.ultimeGiocate) == 0 and self.partitaInCorso: # perchè ultimeGiocate può essere vuoto? perchè il monitor parte prima che i player abbiano giocato 
                self.threadGioca.wait()  # Aspetta che almeno una giocata venga fatta
                while len(self.ultimeGiocate) > 0:
                    print(f"Ha appena giocato il Thread {self.ultimeGiocate.pop()}")  # Stampa thread
                    conta += 1
                    print(f"N.{conta}. NSq. {self.nGiocateSqualificati} G:{self.nGiocate}")  # Mostra quante giocate sono state fatte
                if not self.partitaInCorso:
                    return  # Esce quando la partita Ã¨ finita
    
    def sbircia(self, n: int) -> int:
        with self.lock:
            if current_thread().ident in self.sbirciate: # Se il thread ha giÃ  sbirciato
                print(f"Thread {current_thread().ident} ha giÃ  sbirciato ed Ã¨ squalificato")
                self.squalifica() # lo squalifico 
                return 
            self.sbirciate.append(current_thread().ident)
            for k in self.giocate:
                if k == n: 
                    return len(self.giocate[k]) # Restituisco quante giocate ha quel numero 
    def squalifica(self):
        self.squalifica.append(current_thread().ident) 
        # eliminare tutte le giocate del thread che ha sbirciato piu di una volta 
        for k in self.giocate:
            while current_thread().ident in self.giocate[k]: # finche il thread è presente in quella lista lo elimina 
                self.giocate[k].remove(current_thread().ident) 
    def attendi_e_gioca(self, n: int):
        pass # PUNTO 3 da implementare 

# Punto di ingresso del programma
if __name__ == '__main__':
    gameManager = NumeroBasso()  # Crea il gestore della partita
    v = gameManager.gioca(10, 3)  # Avvia una partita con 10 giocatori
