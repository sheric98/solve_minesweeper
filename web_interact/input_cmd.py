from web_interact import util
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def make_move(driver, coord):
    square = util.coord_to_el(driver, coord)
    square.click()


def put_flag(driver, coord):
    ac = ActionChains(driver)
    square = util.coord_to_el(driver, coord)
    ac.move_to_element(square)
    ac.key_down(Keys.SPACE)
    ac.key_up(Keys.SPACE)
    ac.perform()
#    ac.context_click(square).perform()


def click_face(driver):
    face = util.get_face(driver)
    face.click()