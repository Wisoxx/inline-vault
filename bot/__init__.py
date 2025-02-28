import database as db
import telepot
from logger import setup_logger, thread_local, set_show_debug
from translations import translate
import json


logger = setup_logger(__name__)


class Bot:
    from ._handlers import handle_message, handle_inline_query, media_input_handler, handle_new_media_input, \
        handle_text_input, save_media, check_description, handle_chat_member_status

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
        logger.info("Broadcasting message: {}".format(text))
        exceptions = exceptions or []
        logger.info(f"Found {len(exceptions)} exceptions")
        users = db.Users.execute_query("SELECT user_id FROM users;")
        for user in users:
            if user[0] in exceptions:
                continue
            self.deliver_message(user[0], text, reply_markup=reply_markup)
        logger.info(f"Sent to {len(users)} users")

    @staticmethod
    def get_user(update):
        if "message" in update:
            user = update["message"]["chat"]["id"]
            lang = update["message"]["from"]["language_code"]
        elif "inline_query" in update:
            user = update["inline_query"]["from"]["id"]
            lang = update["inline_query"]["from"]["language_code"]
        elif "my_chat_member" in update:
            user = update["my_chat_member"]["from"]["id"]
            lang = update["my_chat_member"]["from"]["language_code"]
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

            elif "my_chat_member" in update:
                self.handle_chat_member_status(user, lang, update)

        except Exception as e:
            set_show_debug(True)

            # Flush debug logs for this update
            if hasattr(thread_local, "debug_log_stack"):
                logger.debug("Debug log stack before crash:")
                while thread_local.debug_log_stack:
                    logger.debug(thread_local.debug_log_stack.pop(0))  # Log and remove each debug entry
                del thread_local.debug_log_stack  # Clear the stack

            logger.critical(f"Couldn't process update: {e}", exc_info=True)
            set_show_debug(False)

            if user and lang:
                try:
                    self.deliver_message(user, translate(lang, "error"))
                except Exception as e_:
                    logger.critical(f"Couldn't notify user {user} about error: {e_}")
                else:
                    logger.info(f"User {user} notified about error")
