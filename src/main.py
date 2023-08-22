import os

from time import sleep

from pandas import read_excel

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tenacity import retry, stop_after_attempt, wait_fixed

from logger import logger


@retry(
    reraise=True,
    stop=stop_after_attempt(6),
    wait=wait_fixed(10),
)
def define_webdriver():
    logger.info('starting webdriver')
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--ignore-certificate-errors')
    return Remote(
        command_executor=os.environ.get(
            'CHROME_REMOTE_URL',
            'http://localhost:4444'
        ),
        options=options
    )


def get_element(driver: Remote, xpath: str):
    logger.debug(f'getting element - xpath: {xpath}')
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def clear_element(element: WebElement):
    element.send_keys(Keys.CONTROL + 'a')
    element.send_keys(Keys.BACK_SPACE)


def wait_for_progress_bar(driver: Remote):
    element = None
    try:
        element = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 '//progress')
            )
        )
        logger.debug('progress bar is visible')
    except TimeoutException:
        logger.debug('progress bar not found')
        sleep(0.5)
        return

    try:
        if element is not None:
            WebDriverWait(driver, 300).until(
                EC.invisibility_of_element(element)
            )
        logger.debug('progress bar is invisible')
    except Exception:
        pass
    sleep(0.5)


if __name__ == '__main__':
    driver = define_webdriver()
    driver.get('https://web.whatsapp.com/')

    try:
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//canvas/..')
            )
        )
    except TimeoutException:
        driver.quit()
        raise Exception('QRCode not found!')

    logger.info('waiting 5 minutes until you scan QRCODE...')
    try:
        WebDriverWait(driver, 300).until(
            EC.invisibility_of_element(element)
        )
    except TimeoutException:
        driver.quit()
        raise Exception('You need to scan QRCODE!')

    wait_for_progress_bar(driver)

    numbers = read_excel('../resources/numbers.xlsx')
    message = 'oi alecrim'

    xpath_clipboard = '//textarea[@id="clipboard-element"]'
    xpath_search = (
        '//div[@id="side"]//div[contains(@class, "lexical-rich-text-input")]'
        '/div[@role="textbox"]'
    )
    xpath_contact = '//div[@tabindex="-1" and @role="row"]'
    xpath_message = (
        '//div[@id="main"]//div[contains(@class, "lexical-rich-text-input")]'
        '/div[@role="textbox"]'
    )
    xpath_sent_message = (
        '//div[@id="main"]//div[@role="row"][last()]'
        '[//span[@data-icon="msg-dblcheck" or @data-icon="msg-check"]]'
        f'//span[text() = "{message}"]'
    )
    xpath_menu = '//header//span//span[@data-icon="menu"]'
    xpath_menu_disconnect = '//li[@data-animate-dropdown-item="true"][last()]'
    xpath_confirm_disconnect = (
        '//div[@data-animate-modal-popup="true"]//button[last()]'
    )

    driver.execute_script(
        """
        div = document.createElement("div")
        div.setAttribute(
            'style', "height: 50px; width:100%; background-color: red;"
        )

        textarea = document.createElement("textarea")
        textarea.setAttribute('id', 'clipboard-element')

        app = document.getElementById('app')

        div.append(textarea)

        app.insertBefore(div, app.firstChild);
        """
    )
    for it, row in enumerate(numbers.iterrows(), start=1):
        _, data = row
        driver.execute_script(
            f"""
            textarea = document.getElementById("clipboard-element")
            textarea.innerHTML = '{data["number"]}'
            """
        )
        element_clipboard = get_element(driver, xpath_clipboard)
        element_clipboard.location_once_scrolled_into_view
        element_clipboard.send_keys(Keys.CONTROL + 'a')
        element_clipboard.send_keys(Keys.CONTROL + 'c')

        element_search = get_element(driver, xpath_search)
        element_search.send_keys(Keys.CONTROL + 'v')
        element_search.send_keys(Keys.ENTER)
        clear_element(element_search)

        driver.execute_script(
            f"""
            textarea = document.getElementById("clipboard-element")
            textarea.innerHTML = '{message.format(name=data["name"])}'
            """
        )
        element_clipboard = get_element(driver, xpath_clipboard)
        element_clipboard.location_once_scrolled_into_view
        element_clipboard.send_keys(Keys.CONTROL + 'a')
        element_clipboard.send_keys(Keys.CONTROL + 'c')

        element_message = get_element(driver, xpath_message)
        element_message.location_once_scrolled_into_view
        element_message.send_keys(Keys.CONTROL + 'v')
        element_message.send_keys(Keys.ENTER)

        # TODO: handle not sent message
        element_sent_message = get_element(driver, xpath_sent_message)

        logger.info(f'progress {it}/{len(numbers)}')

    logger.info('disconnecting user...')
    get_element(driver, xpath_menu).click()
    get_element(driver, xpath_menu_disconnect).click()
    get_element(driver, xpath_confirm_disconnect).click()
    WebDriverWait(driver, 180).until(
        EC.presence_of_element_located((
           By.XPATH,
           '//canvas/..')
        )
    )
    driver.quit()
    logger.info('done!')
