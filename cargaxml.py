import os
import xml.etree.ElementTree as ET
from estructuras import CampoAgricola


def cargar_xml(ruta: str):
    """
    Carga un archivo XML con la información de los campos agrícolas.
    Devuelve una lista enlazada de objetos CampoAgricola.
    """
    if not os.path.exists(ruta):
        print("Archivo no encontrado:", ruta)
        return None

    tree = ET.parse(ruta)
    root = tree.getroot()

    campos_ll = []

    for campo_el in root:
        if campo_el.tag != "campo":
            continue

        cid = campo_el.get("id") or ""
        cnombre = campo_el.get("nombre") or ""
        campo = CampoAgricola(cid, cnombre)

        #Estaciones base
        estaciones_el = campo_el.find("estacionesBase")
        if estaciones_el is not None:
            for e in estaciones_el:
                if e.tag != "estacion":
                    continue
                eid = e.get("id") or ""
                enombre = e.get("nombre") or eid
                campo.add_estacion(eid, enombre)

        #Sensores de suelo
        sensores_suelo_el = campo_el.find("sensoresSuelo")
        if sensores_suelo_el is not None:
            for s in sensores_suelo_el:
                if s.tag != "sensorS":
                    continue
                sid = s.get("id") or ""
                snombre = s.get("nombre") or sid
                campo.add_sensor_suelo(sid, snombre)
                for f in s:
                    if f.tag != "frecuencia":
                        continue
                    idE = f.get("idEstacion") or ""
                    val = int((f.text or "0").strip() or "0")
                    est = campo.get_or_create_estacion(idE, idE)
                    est.set_frecuencia_suelo(sid, val)

        #Sensores de cultivo
        sensores_cultivo_el = campo_el.find("sensoresCultivo")
        if sensores_cultivo_el is not None:
            for s in sensores_cultivo_el:
                if s.tag != "sensorT":
                    continue
                sid = s.get("id") or ""
                snombre = s.get("nombre") or sid
                campo.add_sensor_cultivo(sid, snombre)
                for f in s:
                    if f.tag != "frecuencia":
                        continue
                    idE = f.get("idEstacion") or ""
                    val = int((f.text or "0").strip() or "0")
                    est = campo.get_or_create_estacion(idE, idE)
                    est.set_frecuencia_cultivo(sid, val)

        campos_ll.append(campo)

    print("Archivo cargado correctamente:", ruta)
    return campos_ll
