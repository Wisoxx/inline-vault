from telepot.namedtuple import InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, \
    InlineQueryResultCachedGif, InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker, \
    InlineQueryResultCachedVideo, InlineQueryResultCachedVoice, InlineQueryResultArticle, InputTextMessageContent
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from logger import setup_logger
import string
from translations import translate

logger = setup_logger(__name__)

LIMIT = 50
CACHETIME = 10


def handle_message(self, user, lang, update):
    message = update.get("message", {})
    if "text" in update["message"]:
        text = update["message"]["text"]
        # commands have bigger priority than other input
        if text.startswith("/start") or text.startswith("/help"):
            username = update.get("message", {}).get("from", {}).get("username", None)
            if not username:
                first_name = update.get("message", {}).get("from", {}).get("first_name", "")
                last_name = update.get("message", {}).get("from", {}).get("last_name", "")
                username = ':' + first_name.lower() + ":" + last_name.lower() + ':'
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=translate(lang, "try"), switch_inline_query_current_chat="")]
                ]
            )
            if db.Users.add({"user_id": user, "username": username})[0]:
                logger.info(f"New user added: {username}")
            self.deliver_message(user, translate(lang, "start"), reply_markup=keyboard)
        elif text.startswith("/description"):
            db.Temp.add({"user_id": user, "key": "status", "value": "check description"})
            self.deliver_message(user, translate(lang, "check description"))
            logger.debug(f"User {user} changed status to check description")
        elif text.startswith("/delete"):
            db.Temp.add({"user_id": user, "key": "status", "value": "delete"})
            self.deliver_message(user, translate(lang, "delete"))
            logger.debug(f"User {user} changed status to delete")
        elif text.startswith("/cancel"):
            db.Temp.delete({"user_id": user})
            self.deliver_message(user, translate(lang, "cancelled"))
            logger.debug(f"User {user} cleared temp")
        elif text.startswith("/done"):
            db.Temp.delete({"user_id": user})
            self.deliver_message(user, translate(lang, "finish deleting"))
            logger.debug(f"User {user} cleared temp")
        else:
            self.handle_text_input(user, lang, update)

    elif any(media_type in message for media_type in ["photo", "document", "audio", "voice", "video", "sticker", "animation"]):
        self.media_input_handler(user, lang, update)
    else:
        self.deliver_message(user, translate(lang, "not recognized"))
        logger.warning(f"Couldn't recognize update: {update}")


def check_description(self, user, lang, file_id):
    description = db.Media.get({"user_id": user, "file_id": file_id}, include_column_names=True).get("description", None)
    if not description:
        self.deliver_message(user, translate(lang, "not found"))
    else:
        self.deliver_message(user, translate(lang, "described by", {"description": description}))
    db.Temp.delete({"user_id": user})  # cleanup
    logger.debug(f"User {user} cleared temp")


def save_media(self, user, lang, description, media_type, file_id, caption):
    if db.Media.add({"user_id": user, "media_type": media_type, "file_id": file_id, "description": description,
                     "caption": caption})[0]:
        self.deliver_message(user, translate(lang, "added"))
        logger.info(f"User {user} added: {media_type} \"{file_id}\"")
    else:
        self.deliver_message(user, translate(lang, "duplicate"))
        self.check_description(user, lang, file_id)

    db.Temp.delete({"user_id": user})  # cleanup
    logger.debug(f"User {user} cleared temp")


def handle_text_input(self, user, lang, update):
    text = update["message"]["text"]
    match db.Temp.get({"user_id": user, "key": "status"}, include_column_names=True).get("value", None):  # status
        case "description":
            temp_data = db.Temp.get({"user_id": user}, include_column_names=True)
            temp_dict = {item["key"]: item["value"] for item in temp_data}  # combine all key-value pairs in one dict
            media_type = temp_dict.get("media_type")
            file_id = temp_dict.get("file_id")
            caption = temp_dict.get("caption", None)
            description = normalize_text(text)
            self.save_media(user, lang, description, media_type, file_id, caption)

        case None:
            self.handle_new_media_input(user, lang, media_type="article", file_id=text)

        case "check description":
            self.check_description(user, lang, text)

        case "delete":
            if db.Media.delete({"user_id": user, "file_id": text}):
                self.deliver_message(user, translate(lang, "deleted"))
                logger.info(f"User {user} deleted {text}")
            else:
                self.deliver_message(user, translate(lang, "not found"))

        case _:
            raise ValueError("Unsupported status")


def media_input_handler(self, user, lang, update):
    message = update.get('message', {})
    caption = message.get('caption', None)

    media_type, file_id = extract_media_info(message)

    match db.Temp.get({"user_id": user, "key": "status"}, include_column_names=True).get("value", None):
        case None:
            self.handle_new_media_input(user, lang, media_type, file_id, caption)

        case "description":
            if db.Temp.get({"user_id": user, "key": "media_type"}, include_column_names=True)["value"] != "article":
                self.handle_new_media_input(user, lang, media_type, file_id, caption)
            else:  # description was sent before the main media, usually by forwarding
                # text of the message is stored in file_id
                description = normalize_text(db.Temp.get({"user_id": user, "key": "file_id"}, include_column_names=True)["value"])
                self.save_media(user, lang, description, media_type, file_id, caption)

        case "check description":
            self.check_description(user, lang, file_id)

        case "delete":
            if db.Media.delete({"user_id": user, "file_id": file_id}):
                self.deliver_message(user, translate(lang, "deleted"))
                logger.info(f"User {user} deleted {file_id}")
            else:
                self.deliver_message(user, translate(lang, "not found"))

        case _:
            raise ValueError("Unsupported status")


def extract_media_info(message):
    if "photo" in message:
        media_type = "photo"
        file_id = message["photo"][-1]["file_id"]  # selects file_id of the largest photo version (last one)

    elif "animation" in message:  # GIFs are sent as animations
        media_type = "gif"
        file_id = message["animation"]["file_id"]

    elif "document" in message:
        media_type = "document"
        file_id = message["document"]["file_id"]

    elif "audio" in message:
        media_type = "audio"
        file_id = message["audio"]["file_id"]

    elif "voice" in message:
        media_type = "voice"
        file_id = message["voice"]["file_id"]

    elif "video" in message:
        media_type = "video"
        file_id = message["video"]["file_id"]

    elif "sticker" in message:
        media_type = "sticker"
        file_id = message["sticker"]["file_id"]

    else:
        return None, None

    return media_type, file_id


def handle_new_media_input(self, user, lang, media_type, file_id, caption=None):
    data = [{"user_id": user, "key": "media_type", "value": media_type},
            {"user_id": user, "key": "file_id", "value": file_id},
            {"user_id": user, "key": "status", "value": "description"}]  # set status to description

    if caption:
        data.append({"user_id": user, "key": "caption", "value": caption})

    db.Temp.add_bulk(data)
    logger.debug(f"User {user} sent: media_type={media_type}, file_id={file_id}")
    logger.debug(f"User {user} changed status to description")
    self.deliver_message(user, translate(lang, "describe"))


def handle_inline_query(self, user, lang, update):
    query_id = update["inline_query"]["id"]
    query_text = normalize_text(update["inline_query"]["query"])
    offset = update["inline_query"]["offset"]
    offset = int(offset) if offset != "" else 0

    logger.info(f"Incoming inline query: user={user}, lang={lang}, offset={offset}, text=\"{query_text}\"")

    fetched, total = db.Media.search_by_description(user, query_text, limit=LIMIT, offset=offset)
    next_offset = offset + LIMIT
    if next_offset > total:
        next_offset = ""
    else:
        next_offset = str(next_offset)

    if not fetched:
        key = "empty" if query_text else "no records"
        text = translate(lang, key)

        if user == 930457591:
            text = "Testing the limit of text message on a button inside inline query results"

        self.answerInlineQuery(
            query_id,
            [],
            is_personal=True,
            cache_time=0,
            switch_pm_text=text,
            switch_pm_parameter="default"
        )
    else:
        results = []

        for element in fetched:
            user_id, media_type, file_id, caption, media_id, description = element

            match media_type:
                case "gif":
                    results.append(InlineQueryResultCachedGif(
                        id=str(media_id),
                        gif_file_id=file_id,
                        title=description,
                        caption=caption
                    ))
                case "audio":
                    results.append(InlineQueryResultCachedAudio(
                        id=str(media_id),
                        audio_file_id=file_id,
                        title=description,
                        caption=caption
                    ))
                case "document":
                    results.append(InlineQueryResultCachedDocument(
                        id=str(media_id),
                        document_file_id=file_id,
                        title=description,
                        caption=caption
                    ))
                case "photo":
                    results.append(InlineQueryResultCachedPhoto(
                        id=str(media_id),
                        photo_file_id=file_id,
                        title=description,
                        caption=caption
                    ))
                case "sticker":
                    results.append(InlineQueryResultCachedSticker(
                        id=str(media_id),
                        sticker_file_id=file_id,
                        title=description,
                    ))
                case "video":
                    results.append(InlineQueryResultCachedVideo(
                        id=str(media_id),
                        video_file_id=file_id,
                        title=description,
                        caption=caption
                    ))
                case "voice":
                    results.append(InlineQueryResultCachedVoice(
                        id=str(media_id),
                        voice_file_id=file_id,
                        title=description,
                        caption=caption
                    ))

                case "article":
                    results.append(InlineQueryResultArticle(
                        id=str(media_id),
                        title='Text',
                        input_message_content=InputTextMessageContent(
                            message_text=file_id
                        ),
                        description=description
                    ))

        self.answerInlineQuery(
            query_id,
            results,
            next_offset=next_offset,
            is_personal=True,
            cache_time=CACHETIME,
            switch_pm_text=translate(lang, "open"),
            switch_pm_parameter="default"
        )


def normalize_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))  # remove punctuation
    text = text.strip()  # trim whitespace
    text = ' '.join(text.split())  # remove extra whitespace
    return text
