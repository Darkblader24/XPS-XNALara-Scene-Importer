
import struct
import binascii


ENCODING_READ = 'utf-8-sig'
ENCODING_WRITE = 'utf-8'


# Format
class TypeFormat:
    SByte = '<b'
    Byte = '<B'
    Int16 = '<h'
    UInt16 = '<H'
    Int32 = '<i'
    UInt32 = '<I'
    Int64 = '<l'
    UInt64 = '<L'
    Single = '<f'
    Double = '<d'


def roundToMultiple(numToRound, multiple):
    return (numToRound + multiple - 1) // multiple * multiple


def readByte(file, print_hex=False):
    numberBin = file.read(1)
    number = struct.unpack(TypeFormat.Byte, numberBin)[0]
    if print_hex:
        print(" ", numberBin, binascii.hexlify(numberBin))
    return number


def writeByte(number):
    bytesBin = struct.pack(TypeFormat.Byte, number)
    return bytesBin


def readUInt16(file):
    numberBin = file.read(2)
    number = struct.unpack(TypeFormat.UInt16, numberBin)[0]
    return number


def writeUInt16(number):
    uInt16 = struct.pack(TypeFormat.UInt16, number)
    return uInt16


def readInt16(file):
    numberBin = file.read(2)
    number = struct.unpack(TypeFormat.Int16, numberBin)[0]
    return number


def writeInt16(number):
    int16 = struct.pack(TypeFormat.Int16, number)
    return int16


def readUInt32(file):
    numberBin = file.read(4)
    number = struct.unpack(TypeFormat.UInt32, numberBin)[0]
    return number


def writeUInt32(number):
    uInt32 = struct.pack(TypeFormat.UInt32, number)
    return uInt32


def readSingle(file, round_to=None, print_hex=False):
    numberBin = file.read(4)
    single = struct.unpack(TypeFormat.Single, numberBin)[0]
    if print_hex:
        print(" ", numberBin, binascii.hexlify(numberBin))
    if round_to is not None:
        single = round(single, round_to)
    return single


def writeSingle(number):
    single = struct.pack(TypeFormat.Single, number)
    return single


def readString(file):
    # Read the byte as an integer indicating the string length
    byte = file.read(1) + b'\x00'
    string_length = struct.unpack(TypeFormat.UInt16, byte)[0]
    # print(string_length, binascii.hexlify(byte))

    # Read the string of the indicated length
    string = ""
    for i in range(string_length):
        # print(string, binascii.hexlify(byte))
        byte = file.read(1)
        if byte == b'\x00':
            print("WARNING: String contains null character. This should never happen!")
            file.seek(file.tell() - 1)
            break
        char = decodeBytes(byte)
        string += char
    # print(string)
    return string


def writeString(string):
    # String Length
    byteString = encodeString(string)
    return byteString


def decodeBytes(bytes):
    # print(bytes)
    return bytes.decode(ENCODING_READ)


def encodeString(string):
    # print(string)
    return string.encode(ENCODING_WRITE)


def hasHeader(fileformat='.xps'):
    return fileformat == '.xps'


def hasTangentVersion(verMayor, verMinor, hasHeader=True):
    return (verMinor <= 12 and verMayor <= 2) if hasHeader else True


def hasVariableWeights(verMayor, verMinor, hasHeader=True):
    return (verMayor >= 3) if hasHeader else False


def check_and_return(file, length):
    numberBin = file.read(length)
    file.seek(file.tell() - length)
    return numberBin


def move_by(file, length):
    file.seek(file.tell() + length)

