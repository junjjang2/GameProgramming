def celciustofahrenheit(degree):
    return degree * 9 / 5 +32

def fahrenheit(degree):
    return (degree - 32) * 5 / 9


cdegree = input("Enter Degree (Celcius to Fahrenheit)")
print(celciustofahrenheit(cdegree))