import database as db
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from logger import setup_logger


logger = setup_logger(__name__)


class Bot:
    def __init__(self, token):
        logger.info('Initializing bot...')
        self.bot = telepot.Bot(token)
        self.users_data = {}

    def __del__(self):
        logger.info('Deleting bot...')

    def __getattr__(self, name):
        return getattr(self.bot, name)

    def deliver_message(self, user, text, reply_to_msg_id=None, reply_markup=None):
        """Deliver a message to a user with optional cancel button and reply markup."""
        if reply_markup:
            final_reply_markup = reply_markup
        else:
            final_reply_markup = {'remove_keyboard': True}

        response = self.sendMessage(user, text, reply_to_message_id=reply_to_msg_id, reply_markup=final_reply_markup)

        logger.debug("Sent message: {}".format(response))

    def broadcast(self, text: str, reply_markup=None):
        users = db.Users.execute_query("SELECT user_id FROM users;")
        for user in users:
            self.deliver_message(user[0], text, reply_markup=reply_markup)

    def broadcast_multilang(self, text: dict, reply_markup=None):
        users = db.Users.execute_query("SELECT user_id, language FROM users;")
        for user, lang in users:
            self.deliver_message(user, text[lang], reply_markup=reply_markup)

    def get_user(self, update):
        if "message" in update:
            user = update["message"]["chat"]["id"]
        elif "inline_query" in update:
            user = update["inline_query"]["from"]["id"]
        else:
            raise KeyError("Couldn't find user")

        return user

    def handle_update(self, update):
        user = None
        try:
            logger.debug('Received update: {}'.format(update))

            user = self.get_user(update)

            if "message" in update:
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    self.deliver_message(user, "From the web: you said '{}'".format(text))
                else:
                    self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")

            elif "inline_query" in update:
                self.deliver_message(user, update["inline_query"]["query"])

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)

            if user:
                self.deliver_message(user, "Something went wrong")
