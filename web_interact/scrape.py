from logic import board
from web_interact import web_constants as wc, util, input_cmd as ic


def get_init_board(driver):
    mines = get_mines(driver)
    rows = try_squares(driver, "row")
    cols = try_squares(driver, "col")
    ret = board.Board(rows, cols, mines)
    return ret


def make_moves(driver, solver, moves):
    new_opens = set()
    for move in moves:
        ic.make_move(driver, move)
        single_update(driver, solver, move, new_opens)

    solver.to_check.update(new_opens)


def single_update(driver, solver, move, new_opens):
    i, j = move
    square = util.coord_to_el(driver, move)
    status = util.get_status(square)
    solver.board.squares[i][j] = status
    if move in solver.board.empties:
        solver.board.empties.remove(move)
    if status != '0':
        new_opens.add(move)
    else:
        empties, a, b = solver.get_neighbors(move)
        for empty in empties:
            single_update(driver, solver, empty, new_opens)


def put_flags(driver, solver, flags):
    for flag in flags:
        i, j = flag
        #ic.put_flag(driver, flag)
        solver.board.squares[i][j] = 'F'
        solver.board.empties.remove(flag)
        solver.board.mines -= 1


def try_squares(driver, dir):
    i = 1
    j = 1
    try:
        while True:
            id = str(i) + '_' + str(j)
            el = driver.find_element_by_id(id)
            if el.get_attribute("style") == wc.NONE:
                if dir == "row":
                    ret = i - 1
                else:
                    ret = j - 1
                break
            if dir == "row":
                i += 1
            else:
                j += 1
    except:
        if dir == "row":
            ret = i - 1
        else:
            ret = j - 1
    return ret



def get_mines(driver):
    ones = get_digit(driver, "mines_ones")
    tens = get_digit(driver, "mines_tens")
    hundreds = get_digit(driver, "mines_hundreds")
    return 100 * hundreds + 10 * tens + ones


def get_digit(driver, id):
    return int(driver.find_element_by_id(id).get_attribute("class")[-1])


def lost_game(driver):
    face = util.get_face(driver).get_attribute("class")
    return face == wc.LOST


def smile_face(driver):
    face = util.get_face(driver).get_attribute("class")
    return face == wc.SMILE


def won_game(driver):
    try:
        driver.switch_to().alert()
        return True
    except:
        return False
