def printInReverse(n):
    print(n)
    if n <= 0:
        print("Number is not natural number, try again")
        return
    while n:
        print(n % 10)
        n = n // 10

printInReverse(321)
printInReverse(1)
printInReverse(-1231231)
printInReverse(12346)
printInReverse(0)