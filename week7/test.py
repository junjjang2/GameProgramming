def nested():
    print("nested")

    def inside():
        print("inside")
    inside()

def closure(str):
    print("closure", str)

    def closed(str2="hi"):
        print(str, str2)
    return closed

