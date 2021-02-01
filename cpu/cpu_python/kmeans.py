# ------------------------------
# instalar dependencias
# ------------------------------
# sudo apt install python3-pip
# pip3 install numpy
# pip3 install sklearn

from sklearn.cluster import KMeans 
import numpy as np
import sys
import time

def main():
    # ler as informacoes passadas via terminal 
    if len(sys.argv) > 5:
        num_points = int(sys.argv[1])
        num_clusters = int(sys.argv[2])
        max_iterations = int(sys.argv[3])
        num_dim = int(sys.argv[4])
        data_in_file_path = sys.argv[5]
        output_file = "./kmeans_" + str(num_points) + "_" + str(num_clusters) + "_" + str(num_dim) + "_out_python" + ".txt";
    else:
        print("invalid args!!!")
        print("usage: <num_points> <num_clusters> <max_iterations> <num_dim> <data_file>\n") 
        return

    input_file = open(data_in_file_path, "r")
    
    points = []
    counter_points = 0
    for line in input_file:
        
        line = line.replace(',',' ').split(' ')     
        
        # retira a primeira linha        
        del line[0]
        # deleta as dimensoes desnecessarias
        for i in range(len(line)-1, num_dim-1, -1):
            del line[i]        
        points.append(line)
        
        counter_points += 1
        if counter_points >= num_points :
            break
    
    points = np.asarray(points).astype('int')                    
    
    clusters = np.zeros((num_clusters, num_dim), dtype=int) 
    
    for i in range(num_clusters):
        for j in range(num_dim):
            value = 0            
            if j == 0:
                value = i
            clusters[i][j] = value
    
    tempo_final = 0
    
    for i in range(10):
        inicio = time.time()
        
        # k-Means
        kmeans = KMeans(n_clusters=num_clusters, init=clusters, n_init=1, max_iter=max_iterations, n_jobs=-1).fit(points)

        fim = time.time()
        tempo_total = fim - inicio
        if(i > 2):
            tempo_final += tempo_total*1000
    
    tempo_final /= 7
    data_out = open(output_file, "w")

    data_out.write("Break in iteration \n\n")
    data_out.write("Total Time: "+str(tempo_final)+"ms\n\n")
    
    cluster_finals = kmeans.cluster_centers_
    for i in range(num_clusters):
        data_out.write("Cluster values: ")        
        for j in range(num_dim):
             data_out.write(str(int(cluster_finals[i][j]))+" ")
        data_out.write("\n\n")
    
    print(sys.argv[0]+" Finishing...\n")
    
    # caso queira ver os resultados no terminal descomente as linhas abaixo
    #print(tempo_total)
    #print(clusters)
    #print(points)
    #print(kmeans.labels_)
    #print(kmeans.cluster_centers_)

if __name__ == "__main__":
    main()
