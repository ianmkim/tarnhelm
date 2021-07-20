from constants import *

def log(str):
    print("[*] ", str)

def data_to_screen(p):
    x = p[0]
    y = p[1]

    new_x = int(x * ((SCREEN_WIDTH-1)/DATA_WIDTH))
    new_y = int(y * ((SCREEN_HEIGHT-1)/DATA_HEIGHT))

    return (new_x, new_y)

def screen_to_data(p):
    x = p[0]
    y = p[1]

    new_x = int(x * ((DATA_WIDTH-1)/SCREEN_WIDTH))
    new_y = int(y * ((DATA_HEIGHT-1)/SCREEN_HEIGHT))

    return (new_x, new_y)

