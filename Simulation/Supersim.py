import simpy
import random
import pandas as pd



def stundenZuSekunden(stundenzahl):
    return stundenzahl*3600
def minutenZuSekunden(minutenzahl):
    return minutenzahl*60
def sekundenZuStunden(sekundenzahl):
    return sekundenzahl/3600
def stunden_umrechnen(stunden):
    ganze_stunden = int(stunden)
    dezimal_teil = stunden - ganze_stunden
    minuten = round(dezimal_teil * 60)
    if minuten >= 10:
        return (f"{ganze_stunden}:{minuten} Uhr")
    else:
        return (f"{ganze_stunden}:0{minuten} Uhr")



class Supermarkt:
    def __init__(self, env, mitarbeiterzahl):
        self.env = env
        self.mitarbeiterzahl = mitarbeiterzahl
        self.kasse1 = simpy.PreemptiveResource(env, capacity = 1)
        self.kasse2 = simpy.PreemptiveResource(env, capacity = 1)
        self.kasse3 = simpy.PreemptiveResource(env, capacity = 1)
        if mitarbeiterzahl > 3:
            self.anderemitarbeiter = simpy.PreemptiveResource(env, capacity=mitarbeiterzahl-3)
        self.kunden_in_kasse = 5  # Mindestanzahl von Kunden, um Kasse 2 zu öffnen

        #Variablen für Auswertung
        global rollicount
        rollicount = []
        global freieZeit
        freieZeit = []

    def setMitarbeiterzahl(self,mitarbeiterzahl):
        self.mitarbeiterzahl = mitarbeiterzahl
        if mitarbeiterzahl > 3:
            self.anderemitarbeiter = simpy.PreemptiveResource(env, capacity=mitarbeiterzahl-3)
            

    def einkauf(self, kunID, einkaufszeit):
        schlange1 = self.kasse1.queue
        schlange2 = self.kasse2.queue
        #print(f"{self.env.now}: Kunde {kunID} betritt Markt")
        yield self.env.timeout(einkaufszeit)
        #print(f"{self.env.now}: Kunde {kunID} steht an Kasse")

        if len(schlange1)<=self.kunden_in_kasse:
            with self.kasse1.request(priority=1,preempt=True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 1 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")
        elif len(schlange2)<=self.kunden_in_kasse:
            with self.kasse2.request(priority=1, preempt= True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 2 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")
        else:
            with self.kasse3.request(priority=1,preempt= True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 3 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")

    def ware(self, rolliID,processtime):
        if len(self.kasse3.queue) == 0:
            with self.kasse3.request(priority=3,preempt=True) as req1:
                yield req1
                print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} wird angefangen")
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} ist fertig")
                    rollicount.append(rolliID)
                except simpy.Interrupt as interrupt:
                    restzeit = self.env.now - beginn
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Kasse 3 wird besetzt")
                    self.env.process(self.ware(rolliID,processtime-sekundenZuStunden(restzeit)))
        elif len(self.kasse2.queue) == 0:
            with self.kasse2.request(priority=3,preempt= True) as req2:
                yield req2
                print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} wird angefangen")
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} ist fertig")
                    rollicount.append(rolliID)
                except simpy.Interrupt as interrupt:
                    restzeit = self.env.now - beginn
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Kasse 2 wird besetzt")
                    self.env.process(self.ware(rolliID,processtime-sekundenZuStunden(restzeit)))
        else:
            if self.mitarbeiterzahl > 3:
                with self.anderemitarbeiter.request(priority=3,preempt=True) as req3:
                    yield req3
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} wird angefangen")
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{stunden_umrechnen(sekundenZuStunden(self.env.now))}: Rolli {rolliID} ist fertig")
                    rollicount.append(rolliID)

    def nixzutun(self):
        if len(self.kasse3.queue) == 0:
            with self.kasse3.request(priority=5,preempt=False) as freereq:
                yield freereq                
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(17))
                    freieZeit.append(self.env.now - beginn)
                except simpy.Interrupt as interrupt:
                    freieZeit.append(self.env.now - beginn)
                    self.env.process(self.nixzutun())

        elif len(self.kasse2.queue) == 0:
            with self.kasse2.request(priority=5,preempt= False) as req2:
                yield req2                
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(17))
                    freieZeit.append(self.env.now - beginn)
                except simpy.Interrupt as interrupt:
                    freieZeit.append(self.env.now - beginn)

        else:
            if self.mitarbeiterzahl > 3:
                with self.anderemitarbeiter.request(priority=5,preempt=False) as req3:
                    yield req3
                    beginn = self.env.now
                    try:
                        yield self.env.timeout(stundenZuSekunden(17))
                        freieZeit.append(self.env.now - beginn)
                    except simpy.Interrupt as interrupt:
                        freieZeit.append(self.env.now - beginn)
                        







            


def genKunden(env, supermarkt):
    yield env.timeout(stundenZuSekunden(2))
    global kunID
    kunID = 0
    while True:
        
        if 7 <= sekundenZuStunden(env.now) < 8:      # 7-8 Uhr
            frequenzzeit = random.uniform(1.9, 2.1)
        elif 8 <= sekundenZuStunden(env.now) < 10:   # 8-10 Uhr
            frequenzzeit = random.uniform(1.4, 1.6)
        elif 10 <= sekundenZuStunden(env.now) < 15:  # 10-15 Uhr
            frequenzzeit = random.uniform(0.9, 1.1)
        elif 15 <= sekundenZuStunden(env.now) < 20:  # 15-20 Uhr
            frequenzzeit = random.uniform(0.4, 0.6)
        elif 20 <= sekundenZuStunden(env.now) < 22:  # 20-22 Uhr
            frequenzzeit = random.uniform(0.9, 1.1)
        else:                                        # nach 22 Uhr 
            frequenzzeit = 1

        kunID+=1
        
        env.process(supermarkt.einkauf(kunID,minutenZuSekunden(random.uniform(13, 17))))
        yield env.timeout(minutenZuSekunden(frequenzzeit))



def genWareKommt(env, supermarkt):
    global rolliID
    rolliID = 1
    while rolliID <= 4:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)
    yield env.timeout(stundenZuSekunden(5))
    while rolliID <= 16:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)
    yield env.timeout(stundenZuSekunden(9))
    while rolliID <= 19:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)

def genWareKommtNicht(env, supermarkt):
    global rolliID
    rolliID = 1
    while rolliID <= 4:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)
    yield env.timeout(stundenZuSekunden(5))
    while rolliID <= 12:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)
    yield env.timeout(stundenZuSekunden(9))
    while rolliID <=15:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)
    

def genNixzutun(env,supermarkt):
    
        env.process(supermarkt.nixzutun())
        yield env.timeout(0)








def tagWoWareKommt(env, supermarkt):
    env.process(genKunden(env,supermarkt))
    env.process(genWareKommt(env,supermarkt))
    env.process(genNixzutun(env,supermarkt))
    if sekundenZuStunden(env.now)>(7):
        supermarkt.setMitarbeiterzahl(7)
    if sekundenZuStunden(env.now)>(14):
        supermarkt.setMitarbeiterzahl(6)
    if sekundenZuStunden(env.now)>(20):
        supermarkt.setMitarbeiterzahl(2)
    yield env.timeout(0)


def tagWoWareNichtKommt(env, supermarkt):
    env.process(genKunden(env,supermarkt))
    env.process(genWareKommtNicht(env,supermarkt))
    env.process(genNixzutun(env,supermarkt))
    if sekundenZuStunden(env.now)>(7):
        supermarkt.setMitarbeiterzahl(4)
    elif sekundenZuStunden(env.now)>(12):
        supermarkt.setMitarbeiterzahl(7)
    elif sekundenZuStunden(env.now)>(14):
        supermarkt.setMitarbeiterzahl(5)
    elif sekundenZuStunden(env.now)>(20):
        supermarkt.setMitarbeiterzahl(3)
    elif sekundenZuStunden(env.now)>(21):
        supermarkt.setMitarbeiterzahl(2)


    yield env.timeout(0)

listKundenzahl = ["Kunden am Tag"]
listrollizahl = ["Zu verräumende Rollis am Tag"]
listgeschaffterollis = ["Verräumte Rollis"]
listfreieZeit = ["Zeit für andere Aufgaben"]
#Woche
#Montag
print ("===================Montag===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4) #Es sind nur drei Mitarbeiter da, da Kasse 1 aber eine Resource ist die nur für die Kasse zuständig ist, wird ein Mitarbeiter mehr simuliert, da vor 7:00 Uhr keiner an der Kasse steht
env.process(tagWoWareNichtKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))


#Dienstag
print ("===================Dienstag===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4)
env.process(tagWoWareKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))


#Mittwoch
print ("===================Mittwoch===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4)
env.process(tagWoWareNichtKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))

#Donnerstag
print ("===================Donnerstag===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4)
env.process(tagWoWareKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))

#Freitag
print ("===================Freitag===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4)
env.process(tagWoWareNichtKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))

#Samstag
print ("===================Samstag===================")    
env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)   
supermarkt = Supermarkt(env,4)
env.process(tagWoWareNichtKommt(env,supermarkt))
env.run(until=stundenZuSekunden(22))
print ("===================Tag vorbei===================")
print(f"Anzahl Kunden: {kunID}")
print(f"Anzahl zuverräumende Rollis: {rolliID-1}")
print(f"Anzahl verräumte Rollis: {len(rollicount)}")
print(f"Freie Zeit von Mitarbeitern: {sekundenZuStunden(sum(freieZeit))}")
listKundenzahl.append(kunID)
listrollizahl.append(rolliID-1)
listgeschaffterollis.append(len(rollicount))
listfreieZeit.append(sekundenZuStunden(sum(freieZeit)))

spalten = ["","Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
daten = [listKundenzahl,listrollizahl, listgeschaffterollis,listfreieZeit]
df = pd.DataFrame(daten,columns=spalten)
df.to_csv('Analyse.csv', index=False)



        








    








