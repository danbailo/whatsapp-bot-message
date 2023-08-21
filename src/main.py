from pandas import read_excel

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
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
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--ignore-certificate-errors')
    return webdriver.Remote(
        command_executor='http://localhost:4444',
        options=options
    )


def get_element(driver: Remote, xpath: str):
    logger.debug(f'getting element - xpath: {xpath}')
    return WebDriverWait(driver, 180).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


if __name__ == '__main__':
    driver = define_webdriver()
    driver.get('https://web.whatsapp.com/')

    try:
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//div[@data-testid="qrcode"]')
            )
        )
    except TimeoutException:
        raise Exception('QRCode not found!')

    logger.info('waiting 5 minutes until you scan QRCODE...')
    try:
        WebDriverWait(driver, 300).until(
            EC.invisibility_of_element(element)
        )
    except TimeoutException:
        raise Exception('You need to scan QRCODE!')

    numbers = read_excel('../resources/numbers.xlsx')

    xpath_clipboard = '//textarea[@id="clipboard-element"]'
    xpath_search = '//div[@data-testid="chat-list-search"]'
    xpath_contact = '//div[@tabindex="-1" and @role="row"]'
    xpath_message = '//div[@data-testid="conversation-compose-box-input"]'
    message = 'hello {name}!'

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

        logger.info(f'progress {it}/{len(numbers)}')
