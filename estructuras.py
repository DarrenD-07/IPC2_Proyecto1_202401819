class Nodo:
    __slots__ = ("value", "next")
    def __init__(self, value):
        self.value = value
        self.next = None

class Lista:
    def __init__(self):
        self.head = None
        self.tail = None
        self._len = 0

    def append(self, value):
        new_node = Nodo(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._len += 1
        return new_node

    def __iter__(self):
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __len__(self):
        return self._len

    def find(self, predicate):
        cur = self.head
        while cur is not None:
            if predicate(cur.value):
                return cur.value
            cur = cur.next
        return None

    def clear(self):
        self.head = None
        self.tail = None
        self._len = 0


class FrequencyEntry:
    def __init__(self, sensor_id: str, value: int):
        self.sensor_id = sensor_id
        self.value = int(value)


class EstacionBase:
    def __init__(self, eid: str, nombre: str):
        self.id = eid
        self.nombre = nombre
        self.freq_suelo = Lista()
        self.freq_cultivo = Lista()
        self.pat_suelo = None
        self.pat_cultivo = None
        self.pat_combinado = None

    def set_frecuencia_suelo(self, sensor_id: str, value: int):
        existing = self.freq_suelo.find(lambda e: e.sensor_id == sensor_id)
        if existing is None:
            self.freq_suelo.append(FrequencyEntry(sensor_id, value))
        else:
            existing.value += int(value)

    def set_frecuencia_cultivo(self, sensor_id: str, value: int):
        existing = self.freq_cultivo.find(lambda e: e.sensor_id == sensor_id)
        if existing is None:
            self.freq_cultivo.append(FrequencyEntry(sensor_id, value))
        else:
            existing.value += int(value)


class Sensor:
    def __init__(self, sid: str, nombre: str):
        self.id = sid
        self.nombre = nombre


class CampoAgricola:
    def __init__(self, cid: str, nombre: str):
        self.id = cid
        self.nombre = nombre
        self.estaciones = Lista()
        self.sensores_suelo = Lista()
        self.sensores_cultivo = Lista()

    def get_or_create_estacion(self, eid: str, nombre: str = None):
        est = self.estaciones.find(lambda e: e.id == eid)
        if est is None:
            est = EstacionBase(eid, nombre if nombre else eid)
            self.estaciones.append(est)
        return est

    def add_estacion(self, eid: str, nombre: str):
        if self.estaciones.find(lambda e: e.id == eid) is None:
            self.estaciones.append(EstacionBase(eid, nombre))

    def add_sensor_suelo(self, sid: str, nombre: str):
        if self.sensores_suelo.find(lambda s: s.id == sid) is None:
            self.sensores_suelo.append(Sensor(sid, nombre))

    def add_sensor_cultivo(self, sid: str, nombre: str):
        if self.sensores_cultivo.find(lambda s: s.id == sid) is None:
            self.sensores_cultivo.append(Sensor(sid, nombre))
