def hex_array_to_str(hex_array):
    return f"[{','.join(map(lambda x: hex(x), hex_array))}]".upper()


def hex_int_to_str(hex_int):
    return f"{(hex(hex_int))}".upper()


def hex_n_array_to_str(hex_array):
    output = ""
    for item in hex_array:
        output += hex_array_to_str(item)
    return output
