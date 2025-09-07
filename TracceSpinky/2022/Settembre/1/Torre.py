from threading import Thread,Condition,RLock
from time import sleep

debug = True
#
# Funzione di stampa sincronizzata di debug
#
plock = RLock()
def prints(s):
    plock.acquire()
    if debug:
        print(s)
    plock.release()


class TorreInCostruzione:

    def __init__(self,H : int):
        self.altFinale = H
        self.larghezzaFinale = 3
        self.stratoAttuale = 0 # inizialmente la torre Ã¨ vuota
        self.tipiStrato = ['-','*','!']          # oscilleremo tra 0 e 1
        self.torre = ['']                    # il primo strato sarÃ  self.torre[0], inizialmente impostato a ''
        self.tipoStratoAttualmenteUsato = 0  # modalitÃ  iniziale = cemento, poichÃ¨ self.tipiStrato[0] = '-'
        self.terminato = False               # imposteremo self.terminato = True quando la Torre sarÃ  completa
        self.lock = RLock()
        '''
            Condizione su cui un operaio aspetta quando non tocca a lui,
            ad esempio quando sei un Cementatore ma attualmente Ã¨ in corso uno strato di mattoni
        '''
        self.attendiTurno = Condition(self.lock)
        '''
            Condizione su cui ci si mette in attesa quando si vuole esser svegliati solo se la Torre Ã¨ del tutto completa
        '''
        self.attendiFine = Condition(self.lock)
        self.siamoInUrgenza = False
        self.saveStrato = -1


    def printTorre(self):
        prints(self.torre)

    '''
        Metodo utilizzato dal main thread per non restituire la Torre prima che sia completata
    '''
    def attendiTerminazione(self):
        with self.lock:
            while not self.terminato:
                self.attendiFine.wait()
    '''
        addPezzo consente di aggiungere un pezzo alla torre in costruzione corrente.
        Quando la torre Ã¨ completa, addPezzo restituisce False. Il valore restituito da addPezzo Ã¨ usato dagli
        Operai per determinare quando Ã¨ necessario fermarsi poichÃ¨ la Torre Ã¨ completa
    '''
    def addPezzo(self,c) -> bool:
        with self.lock:




            '''
                Se non Ã¨ il mio turno AND la torre Ã¨ da finire -> aspetto
                Se Ã¨ il mio turno OR la torre Ã¨ finita -> non aspetto
                Dopo avere atteso, controllo se per caso non ci sono pezzetti da aggiungere: in tal caso pongo Terminato = True, esco e restituisco False;
                Altrimenti aggiungo il mio pezzetto e restituisco True


                STRATOATTUALE = - Infatti ...
                '''
            while self.tipiStrato[self.tipoStratoAttualmenteUsato] != c and not self.terminato and (not self.siamoInUrgenza and c == '!'):
                self.attendiTurno.wait()

            if (self.tipiStrato[2] == c and not self.siamoInUrgenza):
                return False

            if self.stratoAttuale == self.altFinale - 1 and len(self.torre[self.stratoAttuale]) == self.larghezzaFinale:
                #
                # Se siamo arrivati all'ultimo strato AND Ã¨ stato aggiunto l'ultimo pezzetto dell'ultimo strato, allora:
                #
                # non c'Ã¨ piÃ¹ lavoro per me nÃ¨ per nessuno
                #
                self.terminato = True
                #
                # Devo ricordarmi di svegliare tutti gli operai che aspettano per lavorare, e di svegliare il main Thread.
                #
                self.attendiTurno.notifyAll()
                self.attendiFine.notifyAll()
                return False
            #
            #   Aggiungo il mio pezzetto - nota che se arrivi su questo rigo non puÃ² essere che lo stratoAttuale sia completo
            #
            self.torre[self.stratoAttuale] = self.torre[self.stratoAttuale] + c

            #
            #  Se Ã¨ finito lo strato attuale, ma rimane almeno un altro strato da riempire: aggiorno lo stratoAttuale, e
            #  cambio il tipo di strato da Cemento a Mattoni, o viceversa
            #
            if len(self.torre[self.stratoAttuale]) == self.larghezzaFinale and self.stratoAttuale < self.altFinale - 1:


                self.stratoAttuale += 1
                self.torre.append( '' ) # predispongo il prossimo strato

                if self.tipoStratoAttualmenteUsato == 0 :
                    self.tipoStratoAttualmenteUsato = 1
                elif self.tipoStratoAttualmenteUsato == 1:
                    self.tipoStratoAttualmenteUsato = 0
                if (self.tipoStratoAttualmenteUsato == 2):
                    self.tipoStratoAttualmenteUsato = self.saveStrato
                    self.siamoInUrgenza = False
                    self.saveStrato = -1
                    self.attendiTurno.notifyAll()
                    return False
                if (self.siamoInUrgenza):
                    self.saveStrato = self.tipoStratoAttualmenteUsato
                    self.tipoStratoAttualmenteUsato = 2

                self.attendiTurno.notifyAll()

            # self.printTorre() Punto 2: Lo tolgo per non stampare ogni volta che un operaio aggiunge un pezzo

            return True

    '''
    Punto 1
    Arricchisci la classe TorreInCostruzione con il metodo waitForStrato(S : int). Tale metodo pone in
    attesa il thread chiamante fintantoché gli operai non completano lo strato S. Se S è maggiore dell’altezza finale H della
    torre, arrotonda S ad H
    '''

    def waitForStrato(self, S): # S è co se si intendesse l'altezza da raggiungere per far verificare la condizione
        with self.lock:
            if S > self.altFinale:
                S = self.altFinale
            while self.stratoAttuale < S:
                self.attendiTurno.wait()
            prints("Il thread %s ha finito l'attesa per lo strato %d" % (self, S))

    '''
    Punto 2
    Nota che il codice fornito stampa periodicamente l’intero array che rappresenta la Torre. Rimuovi questa stampa e
    introduci un Thread che, sfruttando il metodo waitForStrato, stampi periodicamente, a passi arrotondati al 10%,
    quanta percentuale della Torre è stata correntemente realizzata. Decidi tu come gestire gli arrotondamenti tra il numero di
    strati conclusi e la percentuale di completamento. L’output prodotto da questo thread deve essere una sequenza di linee
    che dicono “10% completato” - “20% completato” - “30% completato” ... ecc
    '''

    '''
    Punto 3
    Introduci il metodo aggiungiStratoUrgente(s : str). Tale metodo può essere invocato durante la
    costruzione di una Torre, e istanzia due nuovi Operai capaci di aggiungere il carattere s (con un ritardo di 100ms tra una
    posa e l’altra) a una TorreInCostruzione. I due nuovi operai dovranno lavorare insieme per aggiungere, non appena sia
    completo lo strato in corso, un nuovo strato fatto di s alla TorreInCostruzione, sospendendo la normale alternanza tra
    Mattonatori e Cementatori. I due nuovi thread dovranno poi terminare al completamento dello strato aggiuntivo, mentre
    la costruzione della torre deve riprendere normalmente. L’altezza finale della Torre sarà aumentata da H ad H+1.

    Un thread chiama aggiungiStratoUrgente, va in attesa fino a quando lo strato corrente non è completato.
    Dopo appena è completato TUTTI GLI ALTRI OPERAI DEVONO ASPETTARE.
    '''

    def aggiungiStratoUrgente(self, s):
        with self.lock:
            self.siamoInUrgenza = True
            self.altFinale += 1
            uno = Operaio(self, s, 100)
            due = Operaio(self, s, 100)
            uno.start()
            due.start()






class Display(Thread):
    def __init__(self, t: TorreInCostruzione):
        super().__init__()
        self.torre = t
        self.percentuale = 0

    def run(self):
        prints("%d%% completato" % self.percentuale)
        while not self.torre.terminato:
            self.percentuale += 10
            #sleep(0.5)
            self.torre.waitForStrato(self.percentuale)
            prints("%d%% completato" % self.percentuale)
        self.percentuale += 10
        if self.percentuale > 100:
                self.percentuale = 100
        print(("%d%% completato" % self.percentuale) + " - TORRE COMPLETA")


class Operaio(Thread):


    '''
        Un Operaio Ã¨ un thread che aggiunge pezzi generici a una torre data.
        t = torre da costruire
        tp = simbolo che aggiunge questo operaio, es. tp= '*', oppure tp = '-', ecc. ecc.
        d = durata che ci vuole per aggiungere un simbolo. es. d=25ms, oppure d=50ms ecc. ecc.
    '''
    def __init__(self,t : TorreInCostruzione, tp : str, d:int):
        super().__init__()
        self.torre = t
        self.tipo = tp
        self.durata = d

    def run(self):
        '''
            Ciclo in cui un operaio aggiunge un pezzo per volta
        '''

        while(self.torre.addPezzo(self.tipo) ):
            sleep(self.durata/1000)
        prints("Thread di tipo: '%s' finito" % self.tipo)





class Cementatore(Operaio):
    '''
        Un cementatore Ã¨ un Operaio che usa il simbolo '-' e ha una cadenza di un pezzo ogni 25ms
    '''
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'-',25)

class Mattonatore(Operaio):

    '''
        Un Mattonatore Ã¨ un Operaio che usa il simbolo '*' e ha una cadenza di un pezzo ogni 50ms
    '''
    def __init__(self, t: TorreInCostruzione):
        super().__init__(t,'*',50)


class Torre:

    def __init__(self):
        pass


    def makeTorre(self,H:int, M:int, C:int):
        t = TorreInCostruzione(H)
        Display(t).start()
        Mattonatori = [Mattonatore(t) for _ in range(M)]
        Cementatori = [Cementatore(t) for _ in range(C)]
        for m in Mattonatori:
            m.start()
        for c in Cementatori:
            c.start()
        t.attendiTerminazione()
        return t.torre

if __name__ == '__main__':
    T = Torre()

    print (T.makeTorre(90,4,7))
    prints("TORRE FINITA")
