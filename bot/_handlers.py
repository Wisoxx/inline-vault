from telepot.namedtuple import InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, InlineQueryResultCachedGif, InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker, InlineQueryResultCachedVideo, InlineQueryResultCachedVoice, InlineQueryResultArticle, InputTextMessageContent
import database as db
from logger import setup_logger


logger = setup_logger(__name__)


LIMIT = 25
CACHETIME = 0


def handle_message(self, user, update):
    message = update.get("message", {})
    if "text" in update["message"]:
        text = update["message"]["text"]
        match text:  # commands have bigger priority than other input
            case "/delete":
                db.Temp.add({"user_id": user, "key": "status", "value": "delete"})
                self.deliver_message(user, "Now send me all the media you want to delete. Send /cancel to cancel")
            case "/cancel":
                db.Temp.delete({"user_id": user})
                self.deliver_message(user, "Successfully canceled.")
            case "/done":
                db.Temp.delete({"user_id": user})
                self.deliver_message(user, "Done deleting.")
            case _:
                self.handle_text_input(user, update)

    elif any(media_type in message for media_type in ["photo", "document", "audio", "voice", "video", "sticker", "animation"]):
        self.media_input_handler(user, update)
    else:
        self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")


def handle_text_input(self, user, update):
    text = update["message"]["text"]
    match db.Temp.get({"user_id": user, "key": "status"}, include_column_names=True).get("value", None):  # status
        case "description":
            media_type = db.Temp.get({"user_id": user, "key": "media_type"}, include_column_names=True)["value"]
            file_id = db.Temp.get({"user_id": user, "key": "file_id"}, include_column_names=True)["value"]
            caption = db.Temp.get({"user_id": user, "key": "caption"}, include_column_names=True).get("value", None)
            description = text

            if db.Media.add({"user_id": user, "media_type": media_type, "file_id": file_id, "description": description,
                          "caption": caption})[0]:
                self.deliver_message(user, "Successfully added")
            else:
                self.deliver_message(user, "You already have that in your collection")

            db.Temp.delete({"user_id": user})  # cleanup

        case None:
            self.handle_new_media_input(user, media_type="article", file_id=text)

        case "delete":
            if db.Media.delete({"user_id": user, "file_id": text}):
                self.deliver_message(user, "Successfully deleted. Send next or /done to stop")
            else:
                self.deliver_message(user, "That media was not found in your collection")

        case _:
            raise ValueError("Unsupported status")


def media_input_handler(self, user, update):
    message = update.get('message', {})
    caption = message.get('caption', None)

    media_type, file_id = extract_media_info(message)

    match db.Temp.get({"user_id": user, "key": "status"}, include_column_names=True).get("value", None):
        case None | "description":  # media can't be description, so treat it like no status
            self.handle_new_media_input(user, media_type, file_id, caption)

        case "delete":
            if db.Media.delete({"user_id": user, "file_id": file_id}):
                self.deliver_message(user, "Successfully deleted. Send next or /done to stop")
            else:
                self.deliver_message(user, "That media was not found in your collection")

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


def handle_new_media_input(self, user, media_type, file_id, caption=None):
    data = [{"user_id": user, "key": "media_type", "value": media_type},
            {"user_id": user, "key": "file_id", "value": file_id},
            {"user_id": user, "key": "status", "value": "description"}]  # set status to description

    if caption:
        data.append({"user_id": user, "key": "caption", "value": caption})

    db.Temp.add_bulk(data)
    self.deliver_message(user, "Please provide a description for this media.")


def handle_inline_query(self, user, update):
    query_id = update["inline_query"]["id"]
    query_text = update["inline_query"]["query"]  # This is what the user searched for
    offset = update["inline_query"]["offset"]
    offset = int(offset) if offset != "" else 0

    fetched, total = db.Media.search_by_description(user, query_text, limit=LIMIT, offset=offset)
    next_offset = offset + LIMIT
    if next_offset > total:
        next_offset = ""
    else:
        next_offset = str(next_offset)

    if not fetched:
        self.answerInlineQuery(
            query_id,
            [],
            switch_pm_text="No media found. Click to add",
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
            cache_time=CACHETIME
        )
