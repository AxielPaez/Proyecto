import socket
from turtle import pu

import pandas as pd

import pymysql
import socket
import time   
import ipaddress

from sqlalchemy import create_engine   

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#config = configparser.ConfigParser()
#config.read('ConfigFile.properties')

ID_GETRECOMENDATION = 1
ID_GETSPEACHDATA = 2
ID_ADDUSUARIOCHARLA = 5
ID_DELUSUARIOCHARLA = 6
ID_GETHISTORY = 7

SERVER_PORT = 10000

def getData():

    connection_string = "mysql+pymysql://%s:%s@%s:%s/%s" % ('dba', 'dba', 'localhost', 3306, 'TED')
    sqlEngine = create_engine(connection_string)

    dbConnection = sqlEngine.connect()

    charlas = pd.read_sql("select * from charlas", dbConnection)

    start_server(charlas)

    return 1




def start_server(charlas):

    dirip = input("\n\nIntroduzca la direccion IP a la que se conectarán otros dispositivos para comunicase con este servidor (sin especificar puerto): ")

    while not isinstance(ipaddress.ip_address(dirip), ipaddress.IPv4Address):
        print("Dirección IP invalida")
        dirip = input("Introduzca la direccion IP a la que se conectarán otros dispositivos para comunicase con este servidor: ")

    transcripts = charlas['transcripcion']

    tfidf = TfidfVectorizer(stop_words='english')

    # Gener matriz TF-IDF
    tfidf_matrix = tfidf.fit_transform(transcripts)

    # Generar cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (dirip, SERVER_PORT)
    sock.bind(server_address)
    print('Servidor escuchando en {} puerto {}'.format(*server_address))

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('Esperando conexiones...')
        connection, client_address = sock.accept()
        try:

            while True:
                aux = connection.recv(1024)                
                if aux:
                    data = aux.decode('utf-8')
                    aux = connection.recv(1024).decode('utf-8')
                    while aux != "":
                        data = data + aux
                        aux = connection.recv(1024).decode('utf-8')
                    data = data.split(';')
                    id_request = int(data[0])

                    if(id_request == ID_GETRECOMENDATION):
                        print("Llega peticion de lista de recomendacion")
                        id_usuario = str(data[1])
                        respuesta = recomendationRequest(id_usuario, cosine_sim, charlas)
                        print("Respondo con:")
                        print(respuesta,"\n")
                        connection.sendall(respuesta.encode())
                        
                    elif(id_request == ID_GETSPEACHDATA):
                        print("Llega peticion de sobre detalle de charla")
                        id_charla = int(data[1])
                        respuesta = speachDataRequest(id_charla, charlas)
                        print("Respondo con:")
                        print(respuesta,"\n")
                        connection.sendall(respuesta.encode())
                    
                    elif(id_request == ID_ADDUSUARIOCHARLA):
                        print("Llega me gusta")
                        id_usuario = int(data[1])
                        id_charla = int(data[2])
                        add_usuario_charla(id_usuario, id_charla)
                        print("Anhadido a historial\n")

                    elif(id_request == ID_DELUSUARIOCHARLA):
                        print("Elimina me gusta")
                        id_usuario = int(data[1])
                        id_charla = int(data[2])
                        del_usuario_charla(id_usuario, id_charla)
                        print("Borrado de historial")

                    elif(id_request == ID_GETHISTORY):
                        print("Llega peticion de historial")
                        id_usuario = int(data[1])
                        respuesta = history_request(id_usuario,charlas)
                        connection.sendall(respuesta.encode())
                        print("Respondo con:")
                        print(respuesta,"\n")

                    
                    

                else:
                    break
                

        finally:
            # Clean up the connection
            connection.close()


def recomendationRequest(id_usuario, cosine_sim, charlas):
    connection_string = "mysql+pymysql://%s:%s@%s:%s/%s" % ('root', 'root', 'localhost', 3306, 'TED')
    sqlEngine = create_engine(connection_string)

    dbConnection = sqlEngine.connect()

    charlasAsistidas = pd.read_sql(("select * from usuario_charla where id_usuario=%(user)s"), dbConnection, params={"user":id_usuario})

    respuestaTmp = []
    if not charlasAsistidas.empty:

        sim_scores=0
        inicializado = 0

        for i in range(len(charlasAsistidas)):

            id = charlasAsistidas.loc[i,'id_charla']
            if inicializado == 0:
                sim_scores = list(enumerate(cosine_sim[id]))
                inicializado = 1
                
            else:
                aux = list(enumerate(cosine_sim[id]))
                for e in range(len(sim_scores)):
                    sim_scores[e] = (e, sim_scores[e][1] + aux[e][1])

        charlasAsistidas = charlasAsistidas.sort_values(by=['id_charla'])
        
        for i in range(len(charlasAsistidas)):
            sim_scores.pop(charlasAsistidas.loc[len(charlasAsistidas)-1-i,'id_charla'])
        
        
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[0:10]

        for i in range(len(sim_scores)):
            id_charla = sim_scores[i][0]
            nombreCharla = charlas["titulo"][id_charla]
            puntuacioCharla = sim_scores[i][1]
            respuestaTmp.append((id_charla,nombreCharla, puntuacioCharla))

        respuesta = ";".join("%s;%s;%s" % tup for tup in respuestaTmp)
        respuesta= str(id_usuario)+";"+respuesta

    else:
        sim_scores = charlas.sort_values('visitas', ascending=False).head(10)

        column = sim_scores["visitas"]
        max_value = column. max()
        for i in range(len(sim_scores)):
            id_charla = sim_scores.iloc[i][0]
            nombreCharla = sim_scores.iloc[i]["titulo"]
            puntuacioCharla = sim_scores.iloc[i]["visitas"]/max_value
            respuestaTmp.append((id_charla,nombreCharla, puntuacioCharla))

        respuesta = ";".join("%s;%s;%s" % tup for tup in respuestaTmp)
        respuesta= str(id_usuario)+";"+respuesta

    return respuesta

def speachDataRequest(id_charla, charlas):
    duracion = str(charlas["duracion"][id_charla])
    visitas = str(charlas["visitas"][id_charla])
    url = str(charlas["url"][id_charla]).replace("\n", "")
    descripcion = str(charlas["descripcion"][id_charla])

    connection_string = "mysql+pymysql://%s:%s@%s:%s/%s" % ('root', 'root', 'localhost', 3306, 'TED')
    sqlEngine = create_engine(connection_string)

    dbConnection = sqlEngine.connect()

    evento_aux = pd.read_sql(("select nombre from eventos where id_evento=%(id_evento)s"), dbConnection, params={"id_evento":str(charlas["evento"][id_charla])})
    evento = str(evento_aux.iloc[0]['nombre'])

    ponente_aux = pd.read_sql(("select nombre from ponentes where id_ponente=%(id_ponente)s"), dbConnection, params={"id_ponente":str(charlas["ponente"][id_charla])})
    ponente = str(ponente_aux.iloc[0]['nombre'])

    respuesta = str(ponente+";"+evento+";"+duracion+";"+visitas+";"+url+";"+descripcion)

    return respuesta

def add_usuario_charla(id_usuario, id_charla):

    fecha_anadido = time.strftime('%Y-%m-%d %H:%M:%S')
    con = pymysql.connect(host='localhost', user='root', password='root', db='TED')

    try:
        with con.cursor() as cursor:
            sql = "insert into usuario_charla(id_usuario, id_charla,fecha_anadido) values (%s, %s, %s)"
            cursor.execute(sql, (id_usuario, id_charla, fecha_anadido))
            con.commit()

    finally:
        con.close()

def del_usuario_charla(id_usuario, id_charla):
    
    con = pymysql.connect(host='localhost', user='root', password='root', db='TED')

    try:
        with con.cursor() as cursor:
            sql = "delete from usuario_charla where (id_usuario, id_charla) in ((%s, %s))"
            cursor.execute(sql, (id_usuario, id_charla))
            con.commit()

    finally:
        con.close()

def history_request(id_usuario,charlas):

    connection_string = "mysql+pymysql://%s:%s@%s:%s/%s" % ('root', 'root', 'localhost', 3306, 'TED')
    sqlEngine = create_engine(connection_string)

    dbConnection = sqlEngine.connect()

    charlasAsistidas = pd.read_sql(("select * from usuario_charla where id_usuario=%(user)s"), dbConnection, params={"user":id_usuario})

    history = charlasAsistidas["id_charla"].to_list()

    respuesta = ""

    for i in range(len(history)):

        id_charla = history[i]
        respuesta = respuesta + str(id_charla)+";"+charlas["titulo"][id_charla]+";"

    respuesta = respuesta[:-1]

    return respuesta




def main():
    getData()

    

if __name__ == "__main__":
    main()