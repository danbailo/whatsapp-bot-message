from pandas import read_excel

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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


if __name__ == '__main__':
    driver = define_webdriver()
    driver.get('https://web.whatsapp.com/')

    while True:
        option = input('Do you already read QRCODE? [y/n] or (q)uit > ')
        if option.lower().startswith(('s', 'y', 'c')):
            break
        if option.lower().startswith(('q')):
            driver.quit()
            logger.info('quitting...')
            exit()

    numbers = read_excel('../resources/numbers.xlsx')

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
        element_clipboard = driver.find_element(
            'xpath', '//textarea[@id="clipboard-element"]'
        )
        element_clipboard.location_once_scrolled_into_view
        element_clipboard.send_keys(Keys.CONTROL + 'a')
        element_clipboard.send_keys(Keys.CONTROL + 'c')

        element_search = driver.find_element('xpath', xpath_search)
        element_search.send_keys(Keys.CONTROL + 'v')
        element_search.send_keys(Keys.ENTER)

        driver.execute_script(
            f"""
            textarea = document.getElementById("clipboard-element")
            textarea.innerHTML = '{message.format(name=data["name"])}'
            """
        )
        element_clipboard = driver.find_element(
            'xpath', '//textarea[@id="clipboard-element"]'
        )
        element_clipboard.location_once_scrolled_into_view
        element_clipboard.send_keys(Keys.CONTROL + 'a')
        element_clipboard.send_keys(Keys.CONTROL + 'c')

        element_message = driver.find_element('xpath', xpath_message)
        element_message.location_once_scrolled_into_view
        element_message.send_keys(Keys.CONTROL + 'v')
        element_message.send_keys(Keys.ENTER)

        logger.info(f'progress {it}/{len(numbers)}')
