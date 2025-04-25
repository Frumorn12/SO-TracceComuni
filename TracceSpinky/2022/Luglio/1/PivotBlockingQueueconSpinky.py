from threading import Thread,RLock,Condition, get_ident
from time import sleep
from random import random,randint

'''
Il codice fornito implementa una struttura dati detta PivotBlockingQueue, simile alla Blocking Queue. 
La differenza principale sta nel fatto che l'operazione take() opera su due elementi. 
Quando si fa un prelievo, un certo elemento da individuare, detto PIVOT, viene eliminato dalla coda, 
mentre un altro elemento viene individuato secondo lâ€™usuale politica FIFO, quindi estratto dalla coda e restituito. 
Proprio come le code bloccanti standard, una PivotBlockingQueue puÃ² contenere al massimo N elementi, 
dove N Ã¨ specificato in fase di creazione della struttura dati. Le regole per determinare lâ€™elemento PIVOT
vengono scelte secondo un particolare criterio che Ã¨ possibile impostare con un metodo apposito.
'''

"""
Punto 1
Si deve modificare la classe PivotBlockingQueue in maniera tale da poter specificare quanti pivot ci sono in ciascun
momento. Per realizzare questo scopo, introduci il metodo setPivotNumber(self, n : int), che imposta il
numero di pivot al valore n (n deve essere almeno 1 e al massimo N-1, dove N è la dimensione della coda).
Il numero di pivot impostato in un certo momento influenza il numero di rimozioni di elementi prescritte. Dovrai fare in
modo che il cambio della quantità di pivot influenzi i metodi take() e put() per come spiegato di seguito. Facciamo un
esempio e supponiamo che il numero di pivot venga impostato a due, anziché uno come nel codice preesistente.
Se i pivot presenti vengono impostati a due, e non più a uno come nel codice esistente, dovrai fare in modo che take()
elimini due pivot prima di restituire l’elemento richiesto, e cioè il primo massimo/minimo e il secondo massimo/minimo.
take() dovrà invece bloccarsi fintantochè in coda non ci siano almeno tre elementi (i due pivot da rimuovere più
l’elemento da estrarre). L’operazione di put resta invece invariata e rimuove un solo pivot nel caso in cui la coda sia piena.
E’ a tuo carico stabilire come gestire opportunamente il caso in cui ci sono due o più pivot di valore uguale e cioè due o più
massimi/minimi di pari valore.
Punto 2
Si estenda la classe PivotBlockingQueue con il metodo doubleTake(). Tale metodo preleva e restituisce una
coppia di elementi anziché uno solo, e si blocca se in coda non sono presenti almeno due elementi + i pivot. Decidi tu
quale sia la codifica migliore per restituire una coppia di interi anziché un solo valore intero. Nota che per risolvere questo
punto è necessario aver implementato il punto 1.
Punto 3
Introduci un metodo waitFor(self, n) che va in attesa bloccante finché la somma degli elementi presenti nella coda
non supera il valore n specificato, uscendo se la condizione è invece verificata.
"""
class PivotBlockingQueue:
    def __init__(self,dim):
        self.dim = dim
        self.buffer = []
        self.criterio = True
        self.lock = RLock()
        self.condNewElement = Condition(self.lock)
        self.pivotNumber = 1 # numero di pivot da rimuovere 

    '''
    take(self) -> int: 

    individua lâ€™elemento PIVOT e lo elimina dalla coda; quindi estrae e restituisce un elemento 
    secondo il consueto ordine FIFO. Il metodo si pone in attesa bloccante se non sono presenti nella coda almeno due elementi.
    '''

    def take(self) -> int:
        with self.lock:
            while len(self.buffer) < self.pivotNumber + 1:
                self.condNewElement.wait()
                
            for i in range(self.pivotNumber):
                self.__removePivot__() 
            return self.buffer.pop(0)

    '''
    put(self,T : int)
    inserisce lâ€™elemento T nella Blocking Queue. Se la coda contiene giÃ  N elementi, 
    individua ed elimina lâ€™elemento PIVOT, quindi inserisce subito lâ€™elemento T. 
    Questo metodo dunque non Ã¨ mai bloccante, poichÃ© quando non si trova posto per T, 
    questo viene creato eliminando lâ€™elemento PIVOT.
    '''          

    def put(self,v : int):
        with self.lock:
            if len(self.buffer) == self.dim:
                self.__removePivot__()
            self.buffer.append(v)
            if len(self.buffer) == self.pivotNumber + 1:
                self.condNewElement.notify()
            self.condNewElement.notify_all() # notifica tutti i thread in attesa sopratuttotto serve per quelli in waitSum cazzi in culo

    '''
    setCriterioPivot(minMax : boolean)
    Definisce il criterio di scelta dellâ€™elemento PIVOT. Il criterio di scelta dellâ€™elemento PIVOT
    serve a definire come la coda individua lâ€™elemento PIVOT. Si puÃ² impostare la coda per prendere 
    il massimo oppure il minimo tra gli elementi attualmente presenti nella coda.
    Se minMax = True, al termine della chiamata il criterio di scelta dellâ€™elemento PIVOT diventerÃ  
    quello del minimo elemento tra quelli presenti nella coda. Se minMax = False, al termine della 
    chiamata il criterio di scelta dellâ€™elemento PIVOT diventerÃ  quello del massimo elemento tra quelli presenti. 
    Se ci sono piÃ¹ di un valore massimo (o piÃ¹ di un valore minimo), viene selezionato lâ€™elemento inserito piÃ¹ recentemente. 
    Inizialmente il criterio di scelta dellâ€™elemento PIVOT viene impostato su quello del minimo elemento.
    '''

    def setCriterioPivot(self,minMax : bool):
        with self.lock:
            self.criterio = minMax  # True min, False max 
    
    '''
        Funzione usata per definire il criterio di scelta del pivot (max o min)
    '''
    def __migliore__(self,a :int, b: int) -> bool:
    
        return a < b if self.criterio else a > b # True min, False max 
    
    '''
        Funzione privata che trova e rimuove il pivot secondo le regole stabilite.
        Si noti che non ci si aspetta che questa funzione venga chiamata direttamente essendo privata.
    '''


    def __removePivot__(self): # con __ __ si definisce un metodo privato 
        pivot = self.buffer[0]
        pivotMultipli = False
        for i in range(1,len(self.buffer)):
            if self.__migliore__(self.buffer[i],pivot):
                pivot = self.buffer[i]
                pivotMultipli = False
            elif self.buffer[i] == pivot:
                pivotMultipli = True

        self.buffer.remove(pivot) if not pivotMultipli else self.buffer.pop()

    '''
    Punto 1
    Si deve modificare la classe PivotBlockingQueue in maniera tale da poter specificare quanti pivot ci sono in ciascun
    momento. Per realizzare questo scopo, introduci il metodo setPivotNumber(self, n : int), che imposta il
    numero di pivot al valore n (n deve essere almeno 1 e al massimo N-1, dove N è la dimensione della coda).
    Il numero di pivot impostato in un certo momento influenza il numero di rimozioni di elementi prescritte. Dovrai fare in
    modo che il cambio della quantità di pivot influenzi i metodi take() e put() per come spiegato di seguito. Facciamo un
    esempio e supponiamo che il numero di pivot venga impostato a due, anziché uno come nel codice preesistente.
    Se i pivot presenti vengono impostati a due, e non più a uno come nel codice esistente, dovrai fare in modo che take()
    elimini due pivot prima di restituire l’elemento richiesto, e cioè il primo massimo/minimo e il secondo massimo/minimo.
    take() dovrà invece bloccarsi fintantochè in coda non ci siano almeno tre elementi (i due pivot da rimuovere più
    l’elemento da estrarre).  L’operazione di put resta invece invariata e rimuove un solo pivot nel caso in cui la coda sia piena.
    E’ a tuo carico stabilire come gestire opportunamente il caso in cui ci sono due o più pivot di valore uguale e cioè due o più
    massimi/minimi di pari valore
    '''
    def setPivotNumber(self,n):
        with self.lock:
            if n < 1 or n > self.dim -1:
                raise ValueError("Il numero di pivot deve essere compreso tra 1 e N-1")
                return
            self.pivotNumber = n
            self.condNewElement.notify_all() # notifica tutti i thread in attesa
    
    '''
    Punto 2
    Si estenda la classe PivotBlockingQueue con il metodo doubleTake(). Tale metodo preleva e restituisce una
    coppia di elementi anziché uno solo, e si blocca se in coda non sono presenti almeno due elementi + i pivot. Decidi tu
    quale sia la codifica migliore per restituire una coppia di interi anziché un solo valore intero. Nota che per risolvere questo
    punto è necessario aver implementato il punto 1
    '''

    def doubleTake(self):
        with self.lock:
            while len(self.buffer) < self.pivotNumber + 2:
                self.condNewElement.wait()
            
            for i in range(self.pivotNumber):
                self.__removePivot__()
                
            return (self.buffer.pop(0), self.buffer.pop(0)) # restituisce una tupla con i due valori estratti 
            

    '''
    Punto 3
    Introduci un metodo waitFor(self, n) che va in attesa bloccante finché la somma degli elementi presenti nella coda
    non supera il valore n specificato, uscendo se la condizione è invece verificata.
    '''

    def waitFor(self,n):
        with self.lock:
            while sum(self.buffer) < n:
                print(f"Il thread TID={get_ident()} è in attesa della somma {n} e la somma attuale è {sum(self.buffer)}")
                
                self.condNewElement.wait()
            return True
    
        



'''
    Thread di test
'''       
class Operator(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
             sleep(random())
             coda.put(randint(-100,100))
             coda.put(randint(-100,100))
             sleep(random())
             print (f"Il thread TID={get_ident()} ha estratto il valore {coda.take()}" )

class OperatorDouble(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
             sleep(random())
             coda.put(randint(-100,100))
             coda.put(randint(-100,100))
             sleep(random())
             print (f"Il thread TID={get_ident()} ha estratto i valori valore {coda.doubleTake()}" )


class OperatorOnlyPut(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
             sleep(random())
             coda.put(randint(-100,100))
             coda.put(randint(-100,100))
             sleep(random())
           
class OperatorOnlyWait(Thread):
    
    def __init__(self,c):
        super().__init__()
        self.coda = c
        
    def run(self):
        for i in range(1000):
             sleep(random())
             coda.waitFor(randint(-100,100))
             sleep(random())
             print (f"Il thread TID={get_ident()} ha estratto il valore {coda.take()}" )

if __name__ == '__main__':
            
    coda = PivotBlockingQueue(10)        
    operatori = [Operator(coda) for i in range(50)] 
    operatoriDouble = [OperatorDouble(coda) for i in range(50)]  
    operatoriOnlyPut = [OperatorOnlyPut(coda) for i in range(50)]
    operatoriOnlyWait = [OperatorOnlyWait(coda) for i in range(50)]

    for o in operatori:
        o.start()     
    for o in operatoriDouble:
        o.start()
    for o in operatoriOnlyPut:
        o.start()
    for o in operatoriOnlyWait:
        o.start()
    
         
    