def genKunden(env, supermarkt):
    yield env.timeout(stundenZuSekunden(2))
    global kunID
    kunID = 0
    while True:
        
        if 7 <= sekundenZuStunden(env.now) < 8:      # 7-8 Uhr
            frequenzzeit = 1
        elif 8 <= sekundenZuStunden(env.now) < 10:   # 8-10 Uhr
            frequenzzeit = 0.75
        elif 10 <= sekundenZuStunden(env.now) < 12:  # 10-15 Uhr
            frequenzzeit = 0.5
        elif 12 <= sekundenZuStunden(env.now) < 18:  # 15-20 Uhr
            frequenzzeit = 0.25
        elif 18 <= sekundenZuStunden(env.now) < 20:  # 20-22 Uhr
            frequenzzeit = 0.5
        else:                                        # nach 22 Uhr 
            frequenzzeit = 1

        kunID+=1
        
        env.process(supermarkt.einkauf(kunID,minutenZuSekunden(random.uniform(13, 17))))
        yield env.timeout(minutenZuSekunden(frequenzzeit))