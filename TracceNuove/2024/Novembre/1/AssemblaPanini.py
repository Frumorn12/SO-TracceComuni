import threading
import queue
import time
import random


"""
Punto 3 Crea un nuovo tipo di thread chiamato InviatoreOrdiniAvanzato. Questo thread invia ordini
come l’InviatoreOrdini già presente, ma poi si mette in attesa bloccante fino a quando l'ordine appena
inviato non viene completamente assemblato e stampato a video. Modifica il codice in modo appropriato per
supportare questa funzionalità.

"""


# Per risolvere il punto tre creiamo un lock dove il thread InviaOrdiniAvanzato si mette in attesa bloccante
# fino a quando non viene completato l'ordine e stampato a video. 

lock = threading.RLock()     # RLock per la mutua esclusione per il punto 3
conditionFineOrdine = threading.Condition(lock) # Condition per il punto 3 sempre




# Liste di code per ingredienti (codici da 0 a 6)
code_ingredienti = [queue.Queue() for _ in range(7)]
code_ingredienti_finiscono = [True for _ in range(7)]  # Lista per controllare se gli ingredienti finiscono 

#
# code_ingredienti[0] => Coda Lattuga
# code_ingredienti[1] => Coda Bacon
# code_ingredienti[2] => Coda Hamburger
# code_ingredienti[3] => Coda Formaggio
# code_ingredienti[4] => Coda Pomodoro
# code_ingredienti[5] => Coda Pane di sopra
# code_ingredienti[6] => Coda Pane di sotto


simboli = {
            0: "@@@@",  # Lattuga
            1: "====",  # Bacon
            2: "####",  # Hamburger
            3: "----",  # Formaggio
            4: "oooo",  # Pomodoro
            5: "/==\\", # Pane di sopra
            6: "\\==/"  # Pane di sotto
}


nomi = {
            0: "Lattuga",    # Lattuga
            1: "Bacon",      # Bacon
            2: "Hamburger",  # Hamburger
            3: "Formaggio",  # Formaggio
            4: "Pomodoro",   # Pomodoro
            5: "Pane di sopra", # Pane di sopra
            6: "Pane di sotto"  # Pane di sotto
}

# 
# Coda per gli ordini
#
coda_ordini = queue.Queue()

#
# Thread produttore di ingredienti
#
class ProduttoreIngredienti(threading.Thread):
    def __init__(self, codice_ingrediente):
        super().__init__()
        self.codice_ingrediente = codice_ingrediente
        self.count = 0 # Contatore degli ingredienti prodotti 
    
    def run(self): 
        while ((self.codice_ingrediente == 5 or self.codice_ingrediente == 6) and self.count <=20) or self.count <= 5:
            # Produce l'ingrediente e lo mette nella coda specifica
            ingrediente = f"Ingrediente {self.codice_ingrediente}"
            code_ingredienti[self.codice_ingrediente].put(ingrediente)
            print(f"Prodotto {nomi[self.codice_ingrediente]}")
            # Simula il tempo di produzione
            self.count+=1  # Incrementa il contatore degli ingredienti prodotti 
            time.sleep(random.uniform(0.5, 1.5))
        code_ingredienti_finiscono[self.codice_ingrediente] = False  # Ingrediente finito 

#
# Thread assemblatore di ordini
#

# Modificare questo per punto 1
class Assemblatore(threading.Thread):
    def __init__(self, ): 
        super().__init__() # Costruttore super init per costruttore di Thread 
        self.stringhe = [] 
 
    def run(self):
        while True:
            # Prende un ordine dalla coda degli ordini
            ordine_id, ordine = coda_ordini.get()

        
            if ordine is None:
                break  # Fine degli ordini

            assemblato = []
            print(f"Assemblaggio ordine {ordine_id}: {ordine}")

            # Ordine_id è l'identificativo dell'ordine 
            # ordine è una lista di codici di ingredienti da assemblare 


            # Punto 1 : Vedere se non  hanno il pane di inserirlo comunque.
            # Punto 2 : Inoltre se il pane è messo in altre posizione che non sia la prima e l'ultima, bisogna
            # mettere le posizioni dei pani in maniera giusta

            if 5 not in ordine:
                # devo mettere il pane di sopra all'inizio
                # e il pane di sotto alla fine
                ordine.insert(0, 5)
            elif 5 != ordine[0]:
                ordine.remove(5) 
                ordine.insert(0, 5) 
            if 6 not in ordine:
                ordine.append(6) 
            elif 6 != ordine[-1]:
                ordine.remove(6)
                ordine.append(6) 


            
            # Preleva gli ingredienti richiesti dall'ordine
            for codice_ingrediente in ordine:
                try: 
                    ingrediente_preso = code_ingredienti[codice_ingrediente].get(block=code_ingredienti_finiscono[codice_ingrediente])  # continua ad andare out of range
                    assemblato.append(ingrediente_preso)
                    print(f"Prelevato {ingrediente_preso} per l'ordine {ordine_id}")
                    self.stringhe.append(simboli[codice_ingrediente]) # Aggiunge il simbolo dell'ingrediente alla lista di stringhe 
                except queue.Empty:
                    print(f"Ingrediente {nomi[codice_ingrediente]} non disponibile per l'ordine {ordine_id}")
                    

                
                
            
            print(f"Ordine {ordine_id} completato: {assemblato}")
            self.stampa_assemblaggio()  # Stampa l'assemblaggio 

    def stampa_assemblaggio(self):
        stringa_totale = "\n".join(self.stringhe) 
        print(stringa_totale)
        self.stringhe = []  
        with lock:
            conditionFineOrdine.notify_all() # Notifica tutti i thread in attesa 

# Thread che genera gli ordini
class InviatoreOrdini(threading.Thread):
    def __init__(self, ordine_id, ordini):
        super().__init__()
        self.ordine_id = ordine_id
        self.ordini = ordini

    def run(self):
        for ordine in self.ordini:
            print(f"Thread {self.ordine_id} ha inviato ordine: {ordine}")
            coda_ordini.put((self.ordine_id, ordine))
            time.sleep(2)  # Tempo tra gli ordini


class InviatoreOrdiniAvanzato(threading.Thread):
    def __init__(self, ordine_id, ordini, ordiniAssemblati):  
        self.ordine_id = ordine_id
        self.ordini = ordini 
        self.ordiniAssemblati = ordiniAssemblati 
    
    def run (self):
        with lock :
            for ordine in self.ordini:
                print(f"Thread {self.ordine_id} ha inviato ordine: {ordine}")
                coda_ordini.put((self.ordine_id, ordine))
                while self.ordine_id not in self.ordiniAssemblati:
                    conditionFineOrdine.wait() 
# Avvio dei thread produttori per ciascun ingrediente
thread_ingredienti = []
for codice in range(7):
    thread = ProduttoreIngredienti(codice)
    thread.start()
    thread_ingredienti.append(thread)

ordiniAssemblati = [] # Lista degli ordini assemblati 

# Avvio dei thread assemblatori
pasquale_lassemblatore = Assemblatore()
pasquale_lassemblatore.start()

ciccio_lassemblatore = Assemblatore()
ciccio_lassemblatore.start()

liste_ordini = [
    [[0, 1, 2], [2, 3, 4]],                     # liste_ordini[0] => Ordini per il thread 1
    [[0, 4, 1, 3], [1, 2, 0]],                  # liste_ordini[1] => Ordini per il thread 2
    [[4,4,2,1], [0,0,1], [3,3,2]],              # liste_ordini[2] => Ordini per il thread 3
    [[0,0,1], [1,2,3,4], [4,0,4], [3,4,3,4,1]]  # liste_ordini[3] => Ordini per il thread 4
]

#
# Creo e avvio i thread che ordinano
# 
threads_ordini = []
i = 0
for ordini in liste_ordini:
    thread = InviatoreOrdini(i, ordini)
    thread.start()
    threads_ordini.append(thread)
    i += 1

