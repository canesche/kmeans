import os, sys

arq_open = open("../master/USCensus1990.data.txt","r")

# verifica se o arquivo existe, caso exista exclua
if os.path.exists('teste.txt'):
    os.remove('teste.txt')

if len(sys.argv) == 1 :
	print("invalid entry!")
	print("Entry valid below:")
	print("python3 generate_data.py <dimension>")
else:
	dim = int(sys.argv[1])
	count_line = 2000000

	arq_exit = open("teste.txt", "a")
	count = 0
	for line in arq_open:

		line = line.split(",")
		
		dims = 0
		for i in range(len(line)):
		    if i < 0:
		        # pula a linha
		        continue
		    elif i < dim :
		        arq_exit.write(str(line[i])+" ")
		    elif i == dim :
		        arq_exit.write(str(line[i])+"\n")
		    else :
		        break
		
		count += 1
		if(count >= count_line):
		    break;
