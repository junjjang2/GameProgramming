
class iotest:
    var1=1
    var2="string"
    var3=0.4

    def printall(self):
        print(self.var1, self.var2, self.var3)

    def __str__(self):
        return "%s %s %s" % (self.var1, self.var2, self.var3)


if __name__ == "__main__":
    f = open("classIO.txt", "w")
    c = iotest()
    print(c)
    f.write(c.__str__())
    f.close()