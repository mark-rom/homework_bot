import os
import sys
import time
import logging
from http import HTTPStatus

from dotenv import load_dotenv
import requests as r
import telegram

from exceptions import APIErrException

load_dotenv()


PRACTICUM_TOKEN = os.getenv('YP_TOKEN')
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# logging
logger = logging.getLogger(__name__)
formatter = '%(asctime)s, %(levelname)s, %(message)s'
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """
    Sends message from the Bot to your Telegram.
    Resieves an instance of telegram.Bot class as bot argument
    and string as message.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Bot have sent a message: {message}')
    except telegram.error.TelegramError(message):
        logger.error(f'Due to an error bot have not sent a message: {message}')


def get_api_answer(current_timestamp):
    """
    Makes a request to Practicum.Homeworks API, returns decoded json response.
    Resieves a time in int format as a parameter.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = r.get(ENDPOINT, headers=HEADERS, params=params)
    except r.exceptions.RequestException:
        msg = 'Cannot reach the Endpoint.'
        raise APIErrException(msg)

    if response.status_code != HTTPStatus.OK:
        msg = (f'Endpoint {ENDPOINT} is not availiable, '
               f'http status: {response.status_code}'
               )
        raise APIErrException(msg)

    return response.json()


def check_response(response):
    """
    Checks if given response contains the "homeworks" key.
    Returns it's value if it is a list.
    """
    if 'homeworks' not in response:
        msg = 'There is no "homeworks" key in APIs response'
        raise TypeError(msg)

    hw_list = response['homeworks']

    if not isinstance(hw_list, list):
        msg = ('Type of "homeworks" value in APIs response'
               f'is "{type(hw_list)}" not "list"'
               )
        raise APIErrException(msg)

    return hw_list


def parse_status(homework):
    """
    Takes a homework dictionary.
    Returns a string with the name and status of current homework.
    """
    if 'homework_name' in homework:
        homework_name = homework.get('homework_name')
    else:
        msg = 'API have returned a homework without a "homework_name" key'
        raise KeyError(msg)
    homework_status = homework.get('status')

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        msg = ('API have returned'
               f'an unknown status {homework_status} for "{homework_name}"'
               )
        raise APIErrException(msg)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """
    Returns False if one of TOKENS or CHAT_ID variables is empty.
    Returns True if PRACTICUM_TOKEN, TELEGRAM_TOKEN
    or TELEGRAM_CHAT_ID aren't empty.
    """
    variables = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    for variable in variables:

        if not variable:
            logger.critical(
                f'Variable {variable} is not defined. '
                'The bot is deactivated'
            )
            return False

    return True


def main():
    """General bot's logic."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
        prev_upd_time = ''

        while True:
            try:
                response = get_api_answer(current_timestamp)
                hw_list = check_response(response)

                for homework in hw_list:
                    upd_time = homework.get('date_updated')

                    if upd_time != prev_upd_time:
                        prev_upd_time = upd_time
                        message = parse_status(homework)
                        send_message(bot, message)
                current_timestamp = int(time.time())

            except APIErrException as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(bot, message)

            except Exception as error:
                logger.error(error)

            finally:
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
