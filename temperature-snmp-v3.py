import os, sys, glob, time
from operator import itemgetter

retries = 10

# Pfad+Einstellungen für "Ringspeicher"-Dateien
c_buf_path = "/home/user"
c_buf_dir = os.path.join(c_buf_path, "temp_c_buf")
c_buf_prefix = "temp_n-*"


def try_method(method):
    count = 0
    output = None
    ex = None
    while(count < retries):
        try:
            output = method()
            break
        except Exception as e:
            ex = e
        count += 1
        time.sleep(1)
    
    if(count >= retries):
        raise Exception(f"Failed to run method {method}{f': {ex}' if ex else '.'}")
    else:
        return output
    
def get_c_buf_files():
    filepath_pattern = os.path.join(c_buf_dir, c_buf_prefix)
    output = glob.glob(filepath_pattern)
    if(len(output) < 5):
        raise Exception(f"Count of files with pattern {filepath_pattern} is not 5 or greater!")
    return output

def read_file_line(temp_path):
    f = open(temp_path, "r")
    lines = f.readline()
    f.close()
    return lines

try:
    # Pfade zu bereits bestehenden Dateien aus "Ringspeicher" suchen
    c_buf_files = try_method(get_c_buf_files)

    # Zu Pfaden jeweils das Änderungsdatum hinzufügen
    c_buf_file_data = [(x, os.path.getmtime(x)) for x in c_buf_files]

    # Pfad-Datums-Liste nach Änderungsdatum absteigend sortieren
    c_buf_file_data = sorted(c_buf_file_data, key=itemgetter(1), reverse=True)

    # Pfade zu den 5 neuesten Dateien
    temp_paths = [x[0] for x in c_buf_file_data[0:5]]
    
    # Temperaturdurchschnitt berechnen und ausgeben
    temps = []
    for temp_path in temp_paths:
        lines = try_method(lambda: read_file_line(temp_path))
        temps.append(float(lines))
    temp_avg = sum(temps) / (1.0 * len(temps))
    print(temp_avg)    
    sys.exit(0)

except Exception as e:
    print(f"Fehler beim Ausführen des Temp-Mittelwert-Skritps: {e}")
    sys.exit(1)
