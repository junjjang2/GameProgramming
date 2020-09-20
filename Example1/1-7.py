def totalofdigits(num):
    print(num)
    if num <= 0:
        print("number is not natural number, try again")
        return
    total = 0
    while num:
        total += num % 10
        num = num//10
    print(total)


totalofdigits(0)
totalofdigits(-123)
totalofdigits(123)
totalofdigits(3)