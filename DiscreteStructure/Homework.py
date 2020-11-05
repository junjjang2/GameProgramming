import inspect

def div(n, d):
    return n//d


def mod(n, d):
    return n % d


print(div(54, 4), mod(54, 4))
print(divmod(54, 4))
print(div(-54, 4), mod(-54, 4))
print(divmod(-54, 4))
print(div(54, -4), mod(54, -4))
print(divmod(54, -4))
print(div(-54, -4), mod(-54, -4))
print(divmod(-54, -4))

help(divmod)