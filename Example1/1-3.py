whours = int(input("Working Hours = "))
hpay = int(input(("Hourly Pay = ")))

if whours > 40 :
    print("Total pay is ", ((whours-40) * hpay * 1.5) + hpay * 40)
else:
    print("Total pay is ", whours * hpay)