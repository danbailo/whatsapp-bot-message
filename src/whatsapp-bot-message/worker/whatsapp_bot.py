from dataclasses import dataclass, field

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

from common.logger import logger


@retry(
    reraise=True,
    stop=stop_after_attempt(6),
    wait=wait_fixed(10),
)
def define_webdriver() -> Remote:
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


@dataclass
class WhatsAppBot:
    message: str

    driver: Remote = field(default=None, init=False)

    XPATH_CLIBOARD: str = '//textarea[@id="clipboard-element"]'
    XPATH_SEARCH: str = (
        '//div[@id="side"]//div[contains(@class, "lexical-rich-text-input")]'
        '/div[@role="textbox"]'
    )
    XPATH_MESSAGE: str = (
        '//div[@id="main"]//div[contains(@class, "lexical-rich-text-input")]'
        '/div[@role="textbox"]'
    )
    XPATH_SENT_MESSAGE: str = (
        '//div[@id="main"]//div[@role="row"][last()]'
        '[//span[@data-icon="msg-dblcheck" or @data-icon="msg-check"]]'
        '//span[text() = "{message}"]'
    )
    XPATH_MENU: str = '//header//span//span[@data-icon="menu"]'
    XPATH_MENU_DISCONNECT: str = (
        '//li[@data-animate-dropdown-item="true"][last()]'
    )
    XPATH_CONFIRM_DISCONNECT: str = (
        '//div[@data-animate-modal-popup="true"]//button[last()]'
    )

    def __post_init__(self):
        self.driver = define_webdriver()

    def __del__(self):
        try:
            logger.info('quitting driver...')
            self.driver.quit()
        except Exception:
            logger.warning('not possible quit driver')

    def __call__(self):
        self.execute()

    def _get_qrcode(self) -> WebElement:
        logger.info('getting qrcode...')
        try:
            return WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//canvas/..')
                )
            )
        except TimeoutException:
            raise Exception('QRCode not found!')

    def _wait_for_user_scan_qrcode(self, element: WebElement):
        logger.info('waiting 5 minutes until you scan QRCODE...')
        try:
            WebDriverWait(self.driver, 300).until(
                EC.invisibility_of_element(element)
            )
        except TimeoutException:
            raise Exception('You need to scan QRCODE!')

    def _wait_for_progress_bar(self):
        element = None
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//progress')
                )
            )
            logger.debug('progress bar is visible')
        except TimeoutException:
            logger.debug('progress bar not found')
            sleep(0.5)
            return

        try:
            if element is not None:
                WebDriverWait(self.driver, 300).until(
                    EC.invisibility_of_element(element)
                )
            logger.debug('progress bar is invisible')
        except Exception:
            pass
        sleep(0.5)

    def _create_textarea_element(self):
        self.driver.execute_script(
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

    def _insert_value_in_textarea_element(self, value: str):
        self.driver.execute_script(
            f"""
            textarea = document.getElementById("clipboard-element")
            textarea.innerHTML = '{value}'
            """
        )

    def _get_element(
        self,
        xpath: str,
        need_scroll_into_element: bool = False
    ) -> WebElement:
        logger.debug(f'getting element - xpath: {xpath}')
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        if need_scroll_into_element is True:
            element.location_once_scrolled_into_view
        return element

    def _clear_element(self, element: WebElement):
        element.send_keys(Keys.CONTROL + 'a')
        element.send_keys(Keys.BACK_SPACE)

    def execute(self):
        self.driver.get('https://web.whatsapp.com/')

        element_qrcode = self._get_qrcode()
        self._wait_for_user_scan_qrcode(element_qrcode)
        self._wait_for_progress_bar()

        numbers = read_excel('../resources/numbers.xlsx')

        self._create_textarea_element()

        for it, row in enumerate(numbers.iterrows(), start=1):
            _, data = row
            self._insert_value_in_textarea_element(data["number"])

            element_clipboard = self._get_element(
                self.XPATH_CLIBOARD, need_scroll_into_element=True
            )
            element_clipboard.send_keys(Keys.CONTROL + 'a')
            element_clipboard.send_keys(Keys.CONTROL + 'c')

            element_search = self._get_element(self.XPATH_SEARCH)
            element_search.send_keys(Keys.CONTROL + 'v')
            element_search.send_keys(Keys.ENTER)
            self._clear_element(element_search)

            self._insert_value_in_textarea_element(self.message)

            element_clipboard = self._get_element(
                self.XPATH_CLIBOARD, need_scroll_into_element=True
            )
            element_clipboard.send_keys(Keys.CONTROL + 'a')
            element_clipboard.send_keys(Keys.CONTROL + 'c')

            element_message = self._get_element(
                self.XPATH_MESSAGE, need_scroll_into_element=True
            )
            element_message.send_keys(Keys.CONTROL + 'v')
            element_message.send_keys(Keys.ENTER)

            # TODO: handle not sent message and retry
            self._get_element(
                self.XPATH_SENT_MESSAGE.format(message=self.message)
            )
            logger.info(f'progress {it}/{len(numbers)}')

        logger.info('disconnecting user...')
        self._get_element(self.XPATH_MENU).click()
        self._get_element(self.XPATH_MENU_DISCONNECT).click()
        self._get_element(self.XPATH_CONFIRM_DISCONNECT).click()

        # TODO: improve way to validate when user is disconnected
        self._get_qrcode()
        logger.info('done!')
