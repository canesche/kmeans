arq_open = open("dataset.txt", "r")
arq_save = open("dataset_int.txt", "w")

for line in arq_open:
    arq_save.write(line.replace(".",""))

arq_open.close()
arq_save.close() 