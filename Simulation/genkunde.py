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