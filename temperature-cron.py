import os, sys, glob
from operator import itemgetter

# 1-wire initialisieren
os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

# Pfad für Temperatursensor-Daten
w1_dir = "/sys/bus/w1/devices/"
w1_devices = os.path.join(w1_dir, "28-*") # Devices (für DS18B20-Sensoren) fangen mit "28-" an
device_folder = glob.glob(w1_devices)[0]
device_file = os.path.join(device_folder, "w1_slave")

# Pfad+Einstellungen für "Ringspeicher"-Dateien
c_buf_path = "/home/user"
c_buf_dir = os.path.join(c_buf_path, "temp_c_buf")
c_buf_prefix = "temp_n-"
c_buf_suffix = ".ttxt"
c_buf_size = 10


try:
    # Temperatur-Datei/Daten einlesen
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()

    # Temperatur parsen
    temperature_c = float(lines[1].strip().split("t=")[1]) / 1000.0

    # Pfade zu bereits bestehenden Dateien aus "Ringspeicher" suchen
    c_buf_files = glob.glob(os.path.join(c_buf_dir, f"{c_buf_prefix}*"))

    # Zu Pfaden jeweils das Änderungsdatum hinzufügen
    c_buf_file_data = [(x, os.path.getmtime(x)) for x in c_buf_files]

    # Pfad-Datums-Liste nach Änderungsdatum aufsteigend sortieren
    c_buf_file_data = sorted(c_buf_file_data, key=itemgetter(1))

    # Neuer/nächster Datei-Pfad im "Ringspeicher"
    c_buf_filepath = os.path.join(c_buf_dir, f"{c_buf_prefix}1{c_buf_suffix}")
    if len(c_buf_file_data) < c_buf_size:
        # = Ringspeicher noch nicht auf Maximalgröße
        c_buf_filepath = os.path.join(c_buf_dir, f"{c_buf_prefix}{len(c_buf_file_data) + 1}{c_buf_suffix}")
    else:
        # = Ringspeicher auf Maximalgröße 
        # => älteste Datei (=> da aufsteigend sortiert, an erster Stelle) zum Überschreiben nehmen
        c_buf_filepath = c_buf_file_data[0][0]
    
    # Temperatur in ausgewählte "Ringspeicher"-Datei speichern
    c_buf_folder = os.path.dirname(c_buf_filepath)
    if not os.path.exists(c_buf_folder):
        os.makedirs(c_buf_folder)
    with open(c_buf_filepath, 'w') as c_buf_file:
        c_buf_file.write(f"{temperature_c}")

    sys.exit(0)

except Exception as e:
    print(f"Fehler beim Ausführen des Temp-Sensor-Skripts: {e}")
    sys.exit(1)
