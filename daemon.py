import os
import time
import pickle
import struct

OUTPUT_DIR_NAME = "Experiment_outputs"
OUTPUT_DIR_PATH = os.path.join(os.getenv("HOME"), OUTPUT_DIR_NAME)
META_FILE = os.path.join(OUTPUT_DIR_PATH, "meta.txt")
TABLE = os.path.join(OUTPUT_DIR_PATH, "table.tmp")
BINARY = os.path.join(OUTPUT_DIR_PATH, "binary.tmp")

DESTINATION = 0
PASSERELLE = 1
GENMASK = 2
INDIC = 3
METRIC = 4
REF = 5
USE = 6
IFACE = 7


def initialization():
    """Fonction pour creer le dossier ou seront stockés les sorties
    Ainsi qu'un fichier servant a retrouver le nombre d'experiences realisée
    Leur donner les droits necessaire etc"""
    if os.path.exists(OUTPUT_DIR_PATH):
        with open(META_FILE, "rb") as meta_file:
            number = struct.unpack("i", meta_file.read(4))
            for i in number:
                result = i+1
                break
        with open(META_FILE, "wb") as meta_file:
            meta_file.write(struct.pack("i", result))
        return result

    else:
        os.mkdir(OUTPUT_DIR_PATH)
        create_meta = "touch "+ META_FILE
        os.system(create_meta)
        chmod_META = "chmod a+w " +META_FILE
        with open(META_FILE, "wb") as meta_file:
            meta_file.write(struct.pack("i", 0))
        return 1


def new_Experiment():
    """Fonction pour creer les fichiers necessaires pour une nouvelle experience
    notamment le fichier de sorties. Elle reinitialise aussi les fichiers intermediaires
    comme le BINARY et le TABLE"""

    xp_number = initialization()
    OUTPUT = os.path.join(OUTPUT_DIR_PATH, "experiment_" + str(xp_number) )

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

    return OUTPUT


def end_Experiment():
    """Ferme tous les fichiers utilisés"""
    rm_TABLE = "rm "+TABLE
    rm_BINARY = "rm "+BINARY
    os.system(rm_BINARY)
    os.system(rm_TABLE)
    os.system("nano"+OUTPUT)
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


def getTabledata(src=TABLE):
    data = {}
    with open(src, 'r') as file:
        text = file.read()
        text = text.split("\n")
    for line in range(len(text) - 3):
        lg = text[line + 2].split(' ')
        elmt = 0
        while elmt < len(lg) - 1:
            if lg[elmt] in " ":
                lg.pop(elmt)
            else:
                lg[elmt].strip()
                elmt += 1
        cle = "ligne " + str(line)
        data[cle] = lg
    return data


def getTime():
    return time.time()


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


def setInput(dst=BINARY):
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


def readData(dest, scr=BINARY):
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


def main():
    OUTPUT = new_Experiment()
    while (True):
        print("=============================== Nouvelle Interation ===================================")
        getTable()
        setInput()
        readData(OUTPUT)
        time.sleep(3)
    end_Experiment()