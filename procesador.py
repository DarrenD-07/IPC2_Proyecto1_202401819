import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from estructuras import Lista, FrequencyEntry, EstacionBase


class SistemaAgricola:
    def __init__(self):
        self.campos = Lista()
        self._procesado = False
        self._cache_reducidas = None

    # Construcción de Patrones
    def _build(self, estacion: EstacionBase, tipo: str, sensores_ll: Lista):

        builder = ""
        first = True
        acc = estacion.freq_suelo if tipo == "suelo" else estacion.freq_cultivo

        for s in sensores_ll:
            entry = acc.find(lambda e: e.sensor_id == s.id and e.value > 0)
            bit = "1" if entry is not None else "0"
            if first:
                builder = bit
                first = False
            else:
                builder = builder + "," + bit
        return builder

    def construir_patrones(self):
        print("→ Construyendo patrones de estaciones...")
        for campo in self.campos:
            print(f"  ▸ Campo {campo.id}: {campo.nombre}")
            for est in campo.estaciones:
                est.pat_suelo = self._build(est, "suelo", campo.sensores_suelo)
                est.pat_cultivo = self._build(est, "cultivo", campo.sensores_cultivo)
                est.pat_combinado = est.pat_suelo + "|" + est.pat_cultivo
                print(f"    - Estación {est.id}: patrón suelo={est.pat_suelo}, "
                    f"cultivo={est.pat_cultivo}, combinado={est.pat_combinado}")

    # Reducción de Estaciones
    class Grupo:
        def __init__(self, patron):
            self.patron = patron
            self.miembros = Lista()

    def _sumar_frecuencias(self, estaciones_ll: Lista, tipo: str, sensores_ll: Lista):
        result = Lista()
        for s in sensores_ll:
            suma = 0
            for est in estaciones_ll:
                acc = est.freq_suelo if tipo == "suelo" else est.freq_cultivo
                entry = acc.find(lambda e: e.sensor_id == s.id)
                if entry is not None:
                    suma += entry.value
            if suma > 0:
                result.append(FrequencyEntry(s.id, suma))
        return result

    def reducir_estaciones(self, campo):
        print(f"→ Reduciendo estaciones del campo {campo.id}...")
        grupos = Lista()

        # Clasificar estaciones en grupos
        for est in campo.estaciones:
            g = grupos.find(lambda gr: gr.patron == est.pat_combinado)
            if g is None:
                g = SistemaAgricola.Grupo(est.pat_combinado)
                grupos.append(g)
                print(f"  ▸ Nuevo grupo con patrón: {est.pat_combinado}")
            g.miembros.append(est)
            print(f"    + Estación {est.id} añadida al grupo.")

        # Construir estaciones reducidas
        estaciones_reducidas = Lista()
        for g in grupos:
            primero = g.miembros.head.value if g.miembros.head is not None else None
            if primero is None:
                continue

            # Concatenar nombres
            nombres_concat = ""
            first = True
            for m in g.miembros:
                if first:
                    nombres_concat = m.nombre
                    first = False
                else:
                    nombres_concat += ", " + m.nombre

            # Crear estación reducida
            est_r = EstacionBase(primero.id, nombres_concat)
            est_r.freq_suelo = self._sumar_frecuencias(g.miembros, "suelo", campo.sensores_suelo)
            est_r.freq_cultivo = self._sumar_frecuencias(g.miembros, "cultivo", campo.sensores_cultivo)
            estaciones_reducidas.append(est_r)

            print(f"Estación reducida creada: {est_r.nombre}")

        return estaciones_reducidas

    # Control del procesamiento
    def procesar(self):
        if self.campos.head is None:
            print("No hay campos cargados.")
            return
        print("INICIO DEL PROCESAMIENTO")
        self.construir_patrones()

        self._cache_reducidas = Lista()
        for campo in self.campos:
            print(f"--- Procesando campo {campo.id} ({campo.nombre}) ---")
            reducidas = self.reducir_estaciones(campo)
            self._cache_reducidas.append((campo.id, reducidas))
        self._procesado = True
        print("=== PROCESAMIENTO FINALIZADO ===")

    # Escritura de XML de salida
    def escribir_salida(self, ruta: str):
        if not self._procesado:
            print("Debe procesar los datos antes de escribir salida.")
            return

        root = ET.Element("camposAgricolas")

        for campo in self.campos:
            campo_el = ET.Element("campo", {"id": campo.id, "nombre": campo.nombre})
            root.append(campo_el)

            # estaciones reducidas
            estaciones_el = ET.Element("estacionesBaseReducidas")
            campo_el.append(estaciones_el)

            reducidas = None
            for cid, est_ll in self._cache_reducidas:
                if cid == campo.id:
                    reducidas = est_ll
                    break

            if reducidas is not None:
                for est in reducidas:
                    est_el = ET.Element("estacion", {"id": est.id, "nombre": est.nombre})
                    estaciones_el.append(est_el)

            # Sensores de suelo
            sensores_suelo_el = ET.Element("sensoresSuelo")
            campo_el.append(sensores_suelo_el)

            for s in campo.sensores_suelo:
                sensor_el = ET.Element("sensorS", {"id": s.id, "nombre": s.nombre})
                sensores_suelo_el.append(sensor_el)

                # buscar frecuencias reducidas en estaciones
                for est in reducidas:
                    entry = est.freq_suelo.find(lambda e: e.sensor_id == s.id)
                    if entry is not None:
                        freq_el = ET.Element("frecuencia", {"idEstacion": est.id})
                        freq_el.text = str(entry.value)
                        sensor_el.append(freq_el)

            # Sensores de cultivo
            sensores_cultivo_el = ET.Element("sensoresCultivo")
            campo_el.append(sensores_cultivo_el)

            for s in campo.sensores_cultivo:
                sensor_el = ET.Element("sensorT", {"id": s.id, "nombre": s.nombre})
                sensores_cultivo_el.append(sensor_el)

                for est in reducidas:
                    entry = est.freq_cultivo.find(lambda e: e.sensor_id == s.id)
                    if entry is not None:
                        freq_el = ET.Element("frecuencia", {"idEstacion": est.id})
                        freq_el.text = str(entry.value)
                        sensor_el.append(freq_el)

        # Guardar con pretty print
        xml_str = ET.tostring(root, encoding="utf-8")
        parsed = md.parseString(xml_str)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(parsed.toprettyxml(indent="  "))

        print("Archivo de salida generado en:", ruta)
