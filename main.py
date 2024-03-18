from helper.writeAJson import writeAJson
import threading
import random
import time
from pymongo import MongoClient
import json
import os
from bson import json_util

# Conexão com o banco de dados MongoDB
client = MongoClient('localhost', 27017)
db = client.bancoiot
sensores_collection = db.sensores


class SensorThread(threading.Thread):
    def __init__(self, nome_sensor):
        super(SensorThread, self).__init__()
        self.nome_sensor = nome_sensor
        self.sensor_alarmado = False

    def run(self):
        while True:
            if not self.sensor_alarmado:
                temperatura = random.uniform(30, 40)
                print(f"Sensor {self.nome_sensor}: {temperatura} C°")

                # Atualizar o banco de dados com a leitura do sensor
                sensor_data = {
                    "nomeSensor": self.nome_sensor,
                    "valorSensor": temperatura,
                    "unidadeMedida": "C°",
                    "sensorAlarmado": self.sensor_alarmado
                }
                sensores_collection.update_one({"nomeSensor": self.nome_sensor}, {"$set": sensor_data}, upsert=True)

                # Salvar em JSON
                writeAJson(sensor_data, self.nome_sensor)

                if temperatura > 38:
                    self.sensor_alarmado = True
                    print(f"Atenção! Temperatura muito alta! Verificar Sensor {self.nome_sensor}!")
            else:
                print(f"Sensor {self.nome_sensor} alarmado! Temperatura muito alta!")
                break

            time.sleep(random.randint(1, 5))  # Tempo aleatório para próxima leitura


# Criar documentos iniciais para os sensores
sensores_collection.insert_many([
    {"nomeSensor": "Temp1", "valorSensor": 0, "unidadeMedida": "C°", "sensorAlarmado": False},
    {"nomeSensor": "Temp2", "valorSensor": 0, "unidadeMedida": "C°", "sensorAlarmado": False},
    {"nomeSensor": "Temp3", "valorSensor": 0, "unidadeMedida": "C°", "sensorAlarmado": False}
])

# Criar e iniciar threads para cada sensor
sensores = ["Temp1", "Temp2", "Temp3"]
threads = []
for sensor in sensores:
    thread = SensorThread(sensor)
    thread.start()
    threads.append(thread)

# Aguardar que todas as threads terminem
for thread in threads:
    thread.join()
