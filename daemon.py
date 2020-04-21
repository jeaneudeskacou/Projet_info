"""ce module lit la table de routage et ecrit les données dans des fichiers
comme ceci.
{1587496787.5253153:
 {'ligne 1': {'DESTINATION': '0.0.0.0', 'PASSERELLE': '192.168.117.2', 'GENMASK': '0.0.0.0', 'INDIC': 'UG', 'METRIC': '100', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'},
  'ligne 2': {'DESTINATION': '169.254.0.0', 'PASSERELLE': '0.0.0.0', 'GENMASK': '255.255.0.0', 'INDIC': 'U', 'METRIC': '1000', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'},
  'ligne 3': {'DESTINATION': '192.168.117.0', 'PASSERELLE': '0.0.0.0', 'GENMASK': '255.255.255.0', 'INDIC': 'U', 'METRIC': '100', 'REF': '0', 'USE': '0', 'IFACE': 'ens33'}
  }
}
dans sa presente version, le module produit 2 fichiers, un fichier binaire contenant la donnée sous forme d'objet (donc facilement exploitable par l'ordinateur mais
illisible pour l'homme)
un fichier .txt destiné à etre lu par l'homme.
"""
import os
import time
import pickle
import struct
#import serial

OUTPUT_DIR_NAME = "Experiment_outputs"
OUTPUT_DIR_PATH = os.path.join(os.getenv("HOME"), OUTPUT_DIR_NAME)
META_FILE = os.path.join(OUTPUT_DIR_PATH, "meta.txt")
TABLE = os.path.join(OUTPUT_DIR_PATH, "table.tmp")

def initialization():
    """Fonction pour creer le dossier où seront stockées les sorties
    ainsi qu'un fichier servant a retrouver le nombre d'experiences réalisée
    Leur donner les droits necessaire etc. Si le dossier existe deja, on lit juste le
    fichier meta.txt et on renvoi la valeur lu"""
    if os.path.exists(OUTPUT_DIR_PATH) :
        if os.path.exists(META_FILE):
            with open(META_FILE, "rb") as meta_file:
                number = struct.unpack("i", meta_file.read(4))
                for i in number:
                    result = i+1
                    break
            with open(META_FILE, "wb") as meta_file:
                meta_file.write(struct.pack("i", result))
            return result
        else:
            create_meta = "touch " + META_FILE
            os.system(create_meta)
            chmod_META = "chmod a+w " + META_FILE
            os.system(chmod_META)
            with open(META_FILE, "wb") as meta_file:
                meta_file.write(struct.pack("i", 0))
            return 1
    else:
        os.mkdir(OUTPUT_DIR_PATH)
        create_meta = "touch "+ META_FILE
        os.system(create_meta)
        chmod_META = "chmod a+w " +META_FILE
        os.system(chmod_META)
        with open(META_FILE, "wb") as meta_file:
            meta_file.write(struct.pack("i", 0))
        return 1


def new_Experiment():
    """Fonction pour creer les fichiers necessaires pour une nouvelle experience
    notamment le fichier de sorties. Elle reinitialise aussi le fichier intermediaire
    comme le TABLE"""

    xp_number = initialization()
    OUTPUT = os.path.join(OUTPUT_DIR_PATH, "experiment_" + str(xp_number)+".txt" )
    BINARY = os.path.join(OUTPUT_DIR_PATH, "experiment_" + str(xp_number)+".binary")

    init_TABLE = "touch " + TABLE
    init_BINARY = "touch " + BINARY
    init_OUTPUT = "touch " + OUTPUT
    chmod_TABLE = "chmod a+w " + TABLE
    chmod_BINARY = "chmod a+w " + BINARY
    chmod_OUTPUT = "chmod a+w " + OUTPUT
    os.system(init_TABLE)
    os.system(init_BINARY)
    os.system(init_OUTPUT)
    os.system(chmod_BINARY)
    os.system(chmod_OUTPUT)
    os.system(chmod_TABLE)

    return OUTPUT, BINARY


def end_Experiment():
    """Ferme tous les fichiers utilisés"""
    rm_TABLE = "rm "+TABLE
    os.system(rm_TABLE)
    pass


def jsonToXml():
    """Permet de convertir le fichier de sortie JSON en XML comprehensible par NS3"""
    pass


def getTable():
    result = ""
    command = "route -n > " + TABLE
    file = open(TABLE, 'r')
    os.system(command)
    result = file.read()
    # file.close()
    return file

def parseTableData(table):
    result = {}
    result["DESTINATION"] = table[0]
    result["PASSERELLE"] = table[1]
    result["GENMASK"] = table[2]
    result["INDIC"] = table[3]
    result["METRIC"] = table[4]
    result["REF"] = table[5]
    result["USE"] = table[6]
    result["IFACE"] = table[7]

    return result

def getTabledata(src=TABLE):
    data = {}
    with open(src, 'r') as file:
        text = file.read()
        text = text.split("\n")
    for line in range(len(text) - 3):
        lg = text[line + 2].split(' ')
        cle = "ligne " + str(line+1)
        data[cle] = parseTableData(tablerefactor(lg))
    return data


def getTime():
    """if os.path.exists("/dev/ttyUSB0"):
        ser = serial.Serial("/dev/ttyUSB0", 2400, timeout=3)
        while True:
            line = str(ser.readline())
            print("time from gps")
            splitline = line.split(',')

            if splitline[0] == "b'$GPRMC":
                result = splitline[1]
                break"""

    result = time.time()
    return result

"""def getTime():
    result = ""
    if os.path.exists("/dev/ttyUSB0"):
        print("getTime function")
        cmd = "cat < /dev/ttyUSB0 > time.tmp"
        os.system(cmd)
        with open("time.tmp", "r") as file:
            while True:
                print("iteration")
                line = file.readline()
                splitline = line.split(',')
                elmt = 0
                while elmt < len(splitline) - 1:
                    if splitline[elmt] in " ":
                        splitline.pop(elmt)
                    else:
                        splitline[elmt].strip()
                        elmt += 1
                print(splitline)
                if splitline[0] == "$GPRMC":
                    print("find GPRMC")
                    result = splitline[1]
                    print(result)
                    break
    return result"""


def getLastInput(dst):
    dstSize = os.path.getsize(dst)
    with open(dst, "rb") as file:
        if dstSize == 0:
            return -1
        else:
            reader = pickle.Unpickler(file)
            data = reader.load()
            data = data.values()
            return data


def setInput(dst):
    data = getTabledata()
    dstSize = os.path.getsize(dst)
    with open(dst, "ab") as dest:
        if dstSize == 0:
            newinput = {}
            newinput[getTime()] = data
            writer = pickle.Pickler(dest)
            writer.dump(newinput)
        else:
            lastValue = getLastInput(dst)
            if compareData(data, lastValue):
                pass
            else:
                with open(dst, "rb") as dest:
                    reader = pickle.Unpickler(dest)
                    currentData = reader.load()
                    currentData[getTime()] = data
                with open(dst, "wb") as dest:
                    writer = pickle.Pickler(dest)
                    writer.dump(currentData)


def compareData(gottenData, dicValues):
    i = 0
    for v in dicValues:
        if i != len(dicValues) - 1:
            i = +1
    last = v
    return gottenData == last


def readData(dest, scr):
    dstSize = os.path.getsize(scr)
    with open(scr, "rb") as scr:
        if dstSize == 0:
            return -1
        else:
            reader = pickle.Unpickler(scr)
            data = reader.load()
            print(data)
            with open(dest, "w") as dest:
                dest.write(str(data))


def tablerefactor(table):
    elmt = 0
    while elmt < len(table) - 1:
        if table[elmt] in " ":
            table.pop(elmt)
        else:
            table[elmt].strip()
            elmt += 1
    return table

"""def getGPSData():
    if os.path.exists("/dev/ttyUSB0"):
        ser = serial.Serial("/dev/ttyUSB0", 2400, timeout=3)
        while True:
            line = str(ser.readline())
            splitline = line.split(',')
            if splitline[0] == "b'$GPRMC":
                result = splitline
                break
        elmt = 0
        while elmt < len(splitline) - 1:
            if splitline[elmt] in " ":
                splitline.pop(elmt)
            else:
                splitline[elmt].strip()
                elmt += 1
        return result
    else:
        print("NO GPS MODULE CONNECTED")"""


def main():
    xp = new_Experiment()
    OUTPUT = xp[0]
    BINARY = xp[1]
    while (True):
        print("============================= Nouvelle Interation =================================")
        getTable()
        setInput(BINARY)
        readData(OUTPUT, BINARY)
        time.sleep(3)
    end_Experiment()

main()