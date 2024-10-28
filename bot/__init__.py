import database as db
import telepot
from logger import setup_logger
from translations import translate
import json


logger = setup_logger(__name__)


class Bot:
    from ._handlers import handle_message, handle_inline_query, media_input_handler, handle_new_media_input, handle_text_input, save_media
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

        logger.debug("Sent message: {}".format(json.dumps(response, indent=4)))

    def broadcast(self, text: str, reply_markup=None, exceptions=None):
        exceptions = exceptions or []
        users = db.Users.execute_query("SELECT user_id FROM users;")
        for user in users:
            if user[0] in exceptions:
                continue
            self.deliver_message(user[0], text, reply_markup=reply_markup)

    def get_user(self, update):
        if "message" in update:
            user = update["message"]["chat"]["id"]
            lang = update["message"]["from"]["language_code"]
        elif "inline_query" in update:
            user = update["inline_query"]["from"]["id"]
            lang = update["inline_query"]["from"]["language_code"]
        else:
            raise KeyError("Couldn't find user")

        return user, lang

    def handle_update(self, update):
        user = None
        lang = None
        try:
            logger.debug('Received update: {}'.format(json.dumps(update, indent=4)))  # pretty print logs

            user, lang = self.get_user(update)

            if "message" in update:
                self.handle_message(user, lang, update)

            elif "inline_query" in update:
                self.handle_inline_query(user, lang, update)

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)
            logger.critical(f"Update that caused error: {json.dumps(update, indent=4)}")

            if user and lang:
                self.deliver_message(user, translate(lang, "error"))
