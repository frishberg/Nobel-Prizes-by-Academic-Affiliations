s = ""
f = open("universities.txt", "r")

for line in f:
    if (len(line) > 20) :
        s += line
    else :
        print(line)

for line in f:
    if ("university" not in line.lower() and "college" not in line.lower() and "institute" not in line.lower()):
        print(line)
    else :
        s += line

s+='"/wiki/ETH_Zurich",\n'

f.close()
f = open("universities.txt", "w")
f.write(s)
f.close()