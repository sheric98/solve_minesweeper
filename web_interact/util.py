from web_interact import web_constants as wc


def get_face(driver):
    return driver.find_element_by_id(wc.FACE)


def coord_to_el(driver, coord):
    i, j = coord
    i += 1
    j += 1
    id = str(i) + '_' + str(j)
    return driver.find_element_by_id(id)


def get_status(square):
    key = square.get_attribute("class").split()[-1]
    if wc.EMPTY in key:
        return 'E'
    elif wc.FLAG in key:
        return 'F'
    else:
        dig = key[-1]
        return dig