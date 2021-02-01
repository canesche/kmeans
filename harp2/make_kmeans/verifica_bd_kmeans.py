open_file = open("/home/jeronimo/GIT/kmeans/USCensus1990.data.txt", "r")

dict = {}

cont = 100000

for line in open_file:
    values = line.split(',')
    for i in range(1, len(values)-4):
        if (values[i] in dict.keys()):
            dict[values[i]] = dict[values[i]] + 1
        else:
            dict[values[i]] = 1
    cont = cont - 1
    if cont == 0:
        break
open_file.close()

keys  = dict.keys()

for i in sorted(keys):
    print(i + " "+ str(dict[i]))