# Homework_bot
Homework_bot is a Telegram bot that checks homework's status on Practicum Bootcamp. It is developed with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library.
____

### How it works
The bot makes a request to API [Bootcamp Homeworks](https://practicum.yandex.ru/api/user_api/homework_statuses/) and checks all the statuses every 10 minutes. If one has updated, the bot sends a message to the owner via Telegram.


### Bot's answers
| API status | Bot's response |
|--------------|-----------------------------|
| reviewing | The review status of the "*homework_name*" has changed. Work is on review. |
| approved | The review status of the "*homework_name*" has changed. Homework is reviewed: reviewer left notes. |
| rejected | The review status of the "*homework_name*" has changed. Homework is reviewed: reviewer is satisfied. Hurray! |
| Unknown status | API have returned an unknown status *homework_status* for "*homework_name*" |

### Environment variables
The bot requires the following env variables:
- TELEGRAM_TOKEN - bot's token. Is given after bot' creation [here](https://t.me/BotFather).
- PRACTICUM_TOKEN - Bootcamp's token. Can be received [here](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).
- TELEGRAM_CHAT_ID - Chat id in Telegram. Can be received [here](https://t.me/userinfobot).

### Logging
Logging format: date and time of the event, event level, event description

***Logging example:***
*2021-10-09 15:34:45,150 &#91;ERROR&#93; Program's error: Endpoint https://practicum.yandex.ru/api/user_api/homework_statuses/111 is unavailable. Response code: 404*

#### Logging levels
##### INFO
- sending any Telegram message

##### ERROR
- error while sending a message via Telegram
- [endpoint](https://practicum.yandex.ru/api/user_api/homework_statuses/) is unavailable 
- other errors with the [endpoint](https://practicum.yandex.ru/api/user_api/homework_statuses/)
- unexpected key in API's answer
- unknown homework status in API's answer

##### DEBUG
- lack of new homework's statuses in API's answer

##### CRITICAL
- lack of env variables during the launch
