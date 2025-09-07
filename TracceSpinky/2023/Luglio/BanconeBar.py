import threading
import random
import time
import string
#
#   BANCONE DEL BAR
#
#   Questo codice simula il workflow tipico dell'arrivo dei clienti in un bar
#   e la loro gestione da parte del barista.
#
#   Il bancone del bar Ã¨ rappresentato da un vettore di liste, dove ogni lista
#   rappresenta una "colonna" del bancone e cioÃ¨ un certo numero di clienti che si accodano sulla stessa fila
#   Ogni colonna puÃ² contenere al massimo 
#   un numero di elementi pari al numero di "righe" del bancone.
#
#   I clienti che arrivano al bar vengono inseriti in una delle colonne del bancone
#   tra quelle che hanno meno elementi. Se ci sono piÃ¹ colonne con lo stesso
#   numero minimo di elementi, viene scelta una di queste a caso. Se il bancone Ã¨ pieno,
#   la procedura di inserimento viene messa in attesa.
#
#   Il barista, quando Ã¨ libero, prende un cliente a caso che trova sulla fila 0
#   e lo serve.  Se non ci sono clienti, la procedura di estrazione viene posta in attesa.
#
#  Ad esempio, lo stato del bancone in un certo momento potrebbe essere:
#
#   OOOOO
#   OO-OO
#   OO--O    
#   -O--O
# 
#  dove O indica che c'Ã¨ un cliente e - indica che la posizione corrispondente Ã¨ vuota. Il barista
#  serve prima i clienti sulla prima riga, scegliendo a caso tra quelli che trova.
#  
#  I clienti in arrivo preferiscono accodarsi sulle colonne che hanno meno elementi.  
#    

#
# Classe di supporto per la gestione di un elemento del bancone. 
#

"""
Punto 1. 
Implementa il metodo imposta_colonna_prioritaria(i). Questo metodo specifica una colonna i.
Dal momento in cui tale metodo viene invocato, l’ordine di estrazione dal bancone bar presente nell’implementazione di
get deve privilegiare la colonna i nell’ordine di estrazione degli elementi. Quando i è completamente vuota va
applicata la strategia di estrazione pre-esistente. Se il valore di i è fuori dall’intervallo dei valori ammissibili, la strategia di
estrazione deve tornare a essere quella pre-esistente.

Punto 2. 
Implementa la funzione attendi_invisibile(self). Il thread che invoca questo metodo va in attesa
bloccante fintantochè non viene estratto un elemento invisibile.

Punto 3. 
Progetta la classe bancone_combinato. Tale classe incapsula due istanze di banconebar B1 e B2 e un thread
S. Il costruttore della classe inizializza B1, B2 e crea ed avvia S. I metodi pubblici di tale classe devono essere gli stessi di
bancone bar, ma così ridefiniti:
    -get: estrae un elemento da B1;
    -put: inserisce un elemento in B2;
    -attendiElemento: attende che un elemento sia complessivamente 
                        estratto dal bancone_combinato;
Il thread S deve prelevare periodicamente elementi da B2 depositarli in B1.
Non è necessario implementare printBancone e miglioraPosizione.
Punto 4. Scrivi del codice multi-threaded che testi tutti i metodi di cui sopra. Assicurati che il tuo codice non si inceppi per
via di errori di sintassi o altri problemi tecnici.

"""
class DatiElemento:
    def __init__(self, invisibile, elemento, condition):
        self.invisibile = invisibile
        self.elemento = elemento
        self.condition = None
        self.monitorato = False 
        self.estratto = False
    
 

class BanconeBar:
    def __init__(self, righe, colonne):
        self.righe = righe
        self.colonne = colonne
        self.bancone = [[] for _ in range(colonne)]
        self.lock = threading.Lock()
        self.ceElemento = threading.Condition(self.lock)
        self.cePostoLibero = threading.Condition(self.lock)
        self.indice_colonna_prioritaria = None
        self.attendi_invisibile = threading.Condition(self.lock)
        self.attesa_invisibile = False 

    def __cisonoElementi(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) > 0:
                return True
        return False
    
    def __tuttoPieno(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) < self.righe:
                return False
        return True
    
    def __getIndiciFilaPiuCorta(self):
        minimo = len(self.bancone[0])
        for i in range(1, self.colonne):
            if len(self.bancone[i]) < minimo:
                minimo = len(self.bancone[i])
        return [i for i in range(self.colonne) if len(self.bancone[i]) == minimo]

   

    def put(self, elemento):
        with self.lock:
            while self.__tuttoPieno():
                self.cePostoLibero.wait()
            #
            # Per gestire l'invisibilitÃ  casuale e i meccanismi di attesa legati al Punto 3, incapsulo l'elemento in un oggetto DatiElemento
            # In questa maniera tutti questi aspetti saranno del tutto trasparenti al codice che usa la classe BanconeBar
            #
            d = DatiElemento(True if random.random() >= 0.9 else False, elemento, threading.Condition(self.lock))    
            self.bancone[random.choice(self.__getIndiciFilaPiuCorta())].append(d)
            self.ceElemento.notify_all()
        
    def get(self):
        with self.lock:
            while not self.__cisonoElementi():
                self.ceElemento.wait()
            #
            # Esploro la situazione in prima fila, raccogliendo prima la posizione dei visibili ed eventualmente quella degli invisibili
            #
            indiciDaCuiScegliere = [i for i in range(self.colonne) if len(self.bancone[i]) > 0 and not self.bancone[i][0].invisibile]
            #
            # Se non ci sono elementi visibili, prendo quelli invisibili
            #
            if len(indiciDaCuiScegliere) == 0:
                indiciDaCuiScegliere = [i for i in range(self.colonne) if len(self.bancone[i]) > 0 and self.bancone[i][0].invisibile]
            
            
            indice_scelto = random.choice(indiciDaCuiScegliere)

            # Punto 1
            # Se è invisibile ma è nella colonna prioritaria lo prendo lo stesso
            if self.indice_colonna_prioritaria is not None:
                # Se la colonna prioritaria Ã¨ vuota, la ignoro
                if len(self.bancone[self.indice_colonna_prioritaria]) == 0:
                    self.indice_colonna_prioritaria = None
                else:
                    # Se la colonna prioritaria non Ã¨ vuota, la uso
                    indice_scelto = self.indice_colonna_prioritaria

            #Punto 2
            if self.bancone[indice_scelto][0].invisibile:
                self.attesa_invisibile = True 
                self.attendi_invisibile.notify_all() 
                
            datiElemento = self.bancone[indice_scelto].pop(0)
            self.cePostoLibero.notify_all()
            datiElemento.estratto = True
            if datiElemento.monitorato:
                datiElemento.condition.notify_all()

            return datiElemento.elemento
    
    #Punto 1
    def imposta_colonna_prioritaria(self, i):
        with self.lock:
            if 0 <= i < self.colonne:
                self.indice_colonna_prioritaria = i
            else:
                self.indice_colonna_prioritaria = None

    # Punto 2
    def attendi_invisibile(self):
        with self.lock:
            while not self.attesa_invisibile:
                self.attendi_invisibile.wait()
            print("Attesa invisibile terminata")
            self.attesa_invisibile = False

    
    

            
    
    def print_bancone(self):
        with self.lock:
            for r in range(self.righe):
                for c in range(self.colonne):
                    if len(self.bancone[c]) >= r+1:
                        toPrint = self.bancone[c][r].elemento
                        #
                        # Se l'elemento Ã¨ invisibile, lo stampo in minuscolo
                        #
                        if self.bancone[c][r].invisibile:
                            toPrint = toPrint.lower()
                    else:
                        toPrint = '-'
                    print(toPrint, end = '') 
                print()

    def miglioraPosizione(self,r,c):
        with self.lock:
            #
            # Controllo che la posizione r,c sia valida
            #
            if 0 <= r < len(self.bancone[c]) and 0 <= c <= self.colonne:
                colonnaMigliore = c
                #
                # Verifico se conviene spostarmi a sinistra. 
                # La colonna adiacente deve avere almeno due elementi in meno perchÃ¨ possa convenire lo spostamento
                # Esempio: se sono quarto nella mia colonna, e ci sono tre elementi nella colonna adiacente, non conviene spostarsi, resterei sempre quarto
                #
                if c > 0 and len(self.bancone[c-1]) + 1 < r:
                    colonnaMigliore = c-1
                #
                # Verifico se conviene spostarmi a destra rispetto alla posizione corrente ma anche rispetto a un eventuale spostamento a sinistra
                #
                if ( c < self.colonne-1 and 
                    len(self.bancone[c+1])+1 < r and
                    (c>0 and len(self.bancone[c+1]) < len(self.bancone[c-1]) )):
                    colonnaMigliore = c+1
                #
                # Se tra le adiacenti ho trovato una colonna migliore, sposto l'elemento
                #
                if colonnaMigliore != c:
                    self.bancone[colonnaMigliore].append(self.bancone[c].pop(r))

    def attendiServizio(self,E):
        with self.lock:
            #
            # Cerco la posizione dell'elemento che voglio monitorare
            #
            trovato = False
            for c in range(self.colonne):
                for r in range(len(self.bancone[c])):
                    #
                    # Preferisco usare 'is' a '==' perchÃ¨ mi interessa che sia proprio lo stesso oggetto a essere presente. 
                    # Ad esempio, voglio poter distinguere due istanze diverse di 'A'.
                    #
                    if self.bancone[c][r].elemento is E:
                        elementoDaAttendere = self.bancone[c][r]
                        trovato = True
                        break
            if not trovato:
                return False
            elementoDaAttendere.monitorato = True
            elementoDaAttendere.condition = threading.Condition(self.lock)
            while not elementoDaAttendere.estratto:
                elementoDaAttendere.condition.wait()
            return True

def prendi_elementi(bancone):
    while True:
        elemento = bancone.get()
        print("Elemento prelevato:", elemento)
        time.sleep(1)  # Simula un tempo di elaborazione

def inserisci_elementi(bancone):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone.put(elemento)
        print(f"Elemento inserito: {elemento}")
        if random.random() >= 0.95:
            r = random.randint(0, bancone.righe-1)
            c = random.randint(0, bancone.colonne-1)
            print(f"Provo a migliorare posizione ({r},{c})")
            bancone.miglioraPosizione(r,c)
        if random.random() >= 0.95:
            print(f"Attendo che venga servito elemento {elemento}")
            if bancone.attendiServizio(elemento):
                out = ""
            else: 
                out = "giÃ  "
            print(f"Fine attesa elemento {out}servito:", elemento)
        time.sleep(0.5)  # Simula un tempo di elaborazione

def stampa_bancone(bancone):
    while True:
        bancone.print_bancone()
        time.sleep(1)

bancone = BanconeBar(7, 5)


#
# Un modo diverso per creare i thread senza dovere dichiarare una classe a parte,
# consiste nel passare come target una funzione che si vuole eseguire al posto del metodo run
#
thread_barista = threading.Thread(target=prendi_elementi, args=(bancone,))
thread_barista.start()

thread_creaClienti = threading.Thread(target=inserisci_elementi, args=(bancone,))
thread_creaClienti.start()


thread_stampab = threading.Thread(target=stampa_bancone, args=(bancone,))
thread_stampab.start()

