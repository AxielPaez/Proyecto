import configparser

import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine   



connection_string = "mysql+pymysql://%s:%s@%s:%s/%s" % ('root', 'root', 'localhost', 3306, 'TED')


def getDataSet():

    print("Leo los csv")
    tmp = pd.read_csv('dataset/ted_main.csv')
    tmp2 = pd.read_csv('dataset/transcripts.csv')

    print("Elimino columnas innecesarias")
    tmp = pd.DataFrame(tmp.drop(["name"], axis=1))
    tmp = pd.DataFrame(tmp.drop(["related_talks"], axis=1))

    print("Anhado la transcripcion")
    charlas = pd.merge(tmp, tmp2, on="url")
    #data=data.assign(transcript=tmp2["transcript"])

    print("Cambio los nombres a las columnas")
    charlas.columns = ["ncomentarios","descripcion","duracion","evento","fechaPonencia","idiomas","ponente","nponente","fechaPublicacion","calificaciones","ocupacionPonente","tags","titulo","url","visitas","transcripcion"]
    charlas.index.name='id_charla'

    ids = []
    column_names = ["id_calificacion", "nombre"]
    calificaciones = pd.DataFrame(columns = column_names)

    column_names = ["id_charla", "id_calificacion", "count"]
    calificaciones_charla = pd.DataFrame(columns = column_names)

    tags = []
    id_tag = 0

    column_names = ["id_charla", "id_tag"]
    tags_charla = pd.DataFrame(columns = column_names)

    eventos = []
    id_evento = 0

    ponentes = []
    id_ponente = 0

    ocupaciones = []
    id_ocupacion = 0

    column_names = ["id_ocupacion", "id_ponente"]
    ocupacion_ponente = pd.DataFrame(columns = column_names)


    print("Procesando datos, espere...")
    for index, row in charlas.iterrows():
        calificacionesCharlaStr = row["calificaciones"]
        calificacionesCharlaStr = calificacionesCharlaStr.split(",")

        aux = 0
        id = -1
        nombre = ""
        count = -1
        for c in calificacionesCharlaStr:
            if(aux == 0):
                id = int(c.split(":")[1])
            if(aux == 1):
                nombre = c.split(":")[1].replace("\'","")
            if(aux == 2):
                if(id not in ids):
                    ids.append(id)
                    calificaciones.loc[len(calificaciones.index)] = [id, nombre]
                count = int(re.search(r'\d+', c.split(":")[1]).group())
                calificaciones_charla.loc[len(calificaciones_charla.index)] = [index, id, count]
                
            aux = (aux +1) % 3

        tagsCharlaStr = row["tags"]
        tagsCharlaStr = tagsCharlaStr.replace(" ","")
        tagsCharlaStr = tagsCharlaStr.replace("\'","")
        tagsCharlaStr = tagsCharlaStr.replace("[","")
        tagsCharlaStr = tagsCharlaStr.replace("]","")
        tagsCharlaStr = tagsCharlaStr.split(",")   
        for t in tagsCharlaStr:
            if (t not in tags):
                tags.append(t)
                id_tag = id_tag + 1
            tags_charla.loc[len(tags_charla.index)] = [index, tags.index(t)]

        if(row["evento"] not in eventos):
            eventos.append(row["evento"])
            id_evento = id_evento + 1
        charlas.at[index,"evento"] = eventos.index(row["evento"])

        if(row["ponente"] not in ponentes):
            ponentes.append(row["ponente"])
            id_ponente = id_ponente + 1
        charlas.at[index,"ponente"] = ponentes.index(row["ponente"])

        if(row["ocupacionPonente"] not in ocupaciones):
            ocupaciones.append(row["ocupacionPonente"])
            id_ocupacion = id_ocupacion + 1
        ocupacion_ponente.loc[len(ocupacion_ponente.index)] = [ocupaciones.index(row["ocupacionPonente"]), ponentes.index(row["ponente"])]

    charlas = pd.DataFrame(charlas.drop(["calificaciones"], axis=1))
    charlas = pd.DataFrame(charlas.drop(["tags"], axis=1))
    charlas = pd.DataFrame(charlas.drop(["ocupacionPonente"], axis=1))
    charlas = pd.DataFrame(charlas.drop(["nponente"], axis=1))

    tags_df = pd.DataFrame (tags, columns = ['nombre'])
    tags_df.index.name='id_tag'

    eventos_df = pd.DataFrame (eventos, columns = ['nombre'])
    eventos_df.index.name = "id_evento"
    charlas["evento"]= charlas["evento"].astype(np.int64)

    ponentes_df = pd.DataFrame (ponentes, columns = ['nombre'])
    ponentes_df.index.name = "id_ponente"
    charlas["ponente"]= charlas["ponente"].astype(np.int64)

    ocupaciones_df = pd.DataFrame (ocupaciones, columns = ['nombre'])
    ocupaciones_df.index.name = "id_ocupacion"

    ocupacion_ponente = ocupacion_ponente.drop_duplicates(keep='first')

    print("Guardo los datos en un csv")
    charlas.to_csv("dataset/filteredDataSet.csv") 
    
    print("Almaceno los datos en la BBDD")
    
    dbConnection = create_engine(connection_string)

    calificaciones.to_sql("calificaciones", dbConnection, if_exists='append', index=False)
    tags_df.to_sql("tags", dbConnection, if_exists='append')
    eventos_df.to_sql("eventos", dbConnection, if_exists='append')
    ponentes_df.to_sql("ponentes", dbConnection, if_exists='append')
    ocupaciones_df.to_sql("ocupaciones", dbConnection, if_exists='append')
    charlas.to_sql("charlas", dbConnection, if_exists='append')
    calificaciones_charla.to_sql("calificacion_charla", dbConnection, if_exists='append', index=False)
    tags_charla.to_sql("tag_charla", dbConnection, if_exists='append', index=False)
    ocupacion_ponente.to_sql("ocupacion_ponente", dbConnection, if_exists='append', index=False)
    

    return 1


def main():
    data = getDataSet()
    

    

if __name__ == "__main__":
    main()