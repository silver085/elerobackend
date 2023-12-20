def deserialize_str_to_list(address: str):
    output = []
    address = address.replace("[", "").replace("]", "")
    for value in address.split(","):
        output.append(int(value, 16))
    return output

def deserialize_str_to_int(value: str):
    return int(value, 16)