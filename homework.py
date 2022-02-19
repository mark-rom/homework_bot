import os
import sys
import time
import logging

from dotenv import load_dotenv
import requests as r
import telegram

from exceptions import CustomException

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

logger = logging.getLogger(__name__)
formatter = '%(asctime)s, %(levelname)s, %(message)s'
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
# могу ли я создать логгер в отдельном файле и импортнуть его сюда?


def send_message(bot, message):
    """I'll write docstrings and unify language till the next review."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
        logger.info(f'В телеграм отправлено сообщение {message}')
    except telegram.error.TelegramError(message):
        logger.error(f'Бот не смог отправить сообщение {message}')


def get_api_answer(current_timestamp):
    """I'll write docstrings and unify language till the next review."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = r.get(ENDPOINT, headers=HEADERS, params=params)
        s_code = response.status_code
        if s_code != 200:
            raise r.exceptions.HTTPError
    except r.exceptions.HTTPError:
        msg = f'Не доступен эндпойнт {ENDPOINT}, код ошибки {s_code}'
        raise CustomException(msg)
    else:
        response = response.json()
        return response


def check_response(response):
    """I'll write docstrings and unify language till the next review."""
    try:
        hw_list = response['homeworks']
        if type(hw_list) is not list:
            msg = f'API вернул список домашних работ типа "{type(hw_list)}"'
            raise TypeError(msg)
    except KeyError:
        msg = 'В ответе API нет ключа "homeworks"'
        raise KeyError(msg)
    else:
        return hw_list


def parse_status(homework):
    """I'll write docstrings and unify language till the next review."""
    homework_name = homework.get('homework_name')
    # нужна обработка отсутствия ключа homework_name
    homework_status = homework.get('status')

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        raise KeyError('API вернул неизвестный статус домашней работы')
    else:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """I'll write docstrings and unify language till the next review."""
    variables = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    for variable in variables:
        if not variable:
            logger.critical(
                f'Не определена переменная {variable}. '
                'Работа программы прекращена'
            )
            return False
    return True


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_upd_time = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            hw_list = check_response(response)

            if hw_list:
                homework = hw_list[0]
                upd_time = homework.get('date_updated')

                if upd_time != prev_upd_time:
                    prev_upd_time = upd_time
                    message = parse_status(homework)
                    send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        else:
            current_timestamp = int(time.time())
        finally:
            time.sleep(RETRY_TIME)
            check_tokens()


if __name__ == '__main__':
    main()
