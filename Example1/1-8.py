def makeMagicSquare(n):
    arr = [[0 for i in range(n)] for j in range(n)]
    x = 0
    y = int(n/2)
    for i in range(1, n*n+1):
        arr[x][y] = i
        if i == n*n:
            break
        x-=1
        y-=1
        while 1:
            if x < 0:
                x = n-1
            if y < 0:
                y = n-1
            if arr[x][y] != 0:
                y += 1
                if y >= n:
                    y = 0
                x += 1
                if x >= n:
                    x = 0
                x += 1
                if x >= n:
                    x = 0
            else:
                break

    print("size:",n)
    for row in arr:
        for col in row:
            print(col, end=" ")
        print()


makeMagicSquare(3)
makeMagicSquare(5)
makeMagicSquare(7)