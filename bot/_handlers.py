from telepot.namedtuple import InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, InlineQueryResultCachedGif, InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker, InlineQueryResultCachedVideo, InlineQueryResultCachedVoice, InlineQueryResultArticle
import database as db
from logger import setup_logger


logger = setup_logger(__name__)


LIMIT = 15


def handle_message(self, user, update):
    pass


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

        self.answerInlineQuery(
            query_id,
            results,
            next_offset=next_offset,
            is_personal=True
        )
