from selenium import webdriver
import selenium.webdriver.support.ui as ui
from logic import find_moves as fm
from web_interact import scrape, input_cmd as inp, web_constants as wc
from selenium.common.exceptions import UnexpectedAlertPresentException
import stats.running_stats as rs


def reset_game(driver):
    board = scrape.get_init_board(driver)
    solver = fm.Solver(board)
    print("new game")
    return solver


if __name__ == "__main__":
    driver = webdriver.Chrome()
    wait = ui.WebDriverWait(driver, 10)

    driver.get(wc.MS_URL)
    solver = reset_game(driver)
    games_played = 1
    while True:
        try:
            moves, flags, msg = solver.find_update()
            scrape.make_moves(driver, solver, moves)
            scrape.put_flags(driver, solver, flags)
            if msg == "random":
                if scrape.lost_game(driver):
                    inp.click_face(driver)
                    solver = reset_game(driver)
                    games_played += 1
        except UnexpectedAlertPresentException:
            print("played " + str(games_played) + " games")
            break
