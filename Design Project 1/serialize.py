VERSION = "1"
FORMAT = "utf-8"

def serialize(data):
    data_string = VERSION.encode(FORMAT)
    data_string += data["operation"].value.encode(FORMAT)
    # msgsize = str(len(data["info"])).encode(FORMAT)
    # print(HEADER - len(msgsize))
    # data_string += msgsize + b' ' * (HEADER - len(msgsize))
    data_string += data["info"].encode(FORMAT)
    return data_string

def deserialize(data):
    data = data.decode()
    decoded_data = {}
    VERSION_SIZE = data[0]
    if VERSION_SIZE != VERSION:
        return "Wire Protocols do not match up"
    decoded_data["version"] = VERSION_SIZE
    decoded_data["operation"] = data[1:3]
    decoded_data["info"] = data[3:]

    return decoded_data