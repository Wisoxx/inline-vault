from telepot.namedtuple import InlineQueryResultCachedGif, InlineQueryResultArticle, InputTextMessageContent
from logger import setup_logger


logger = setup_logger(__name__)


def handle_message(self, user, update):
    pass


def handle_inline_query(self, user, update):
    query_id = update["inline_query"]["id"]
    query_text = update["inline_query"]["query"]  # This is what the user searched for

    # Prepare hard-coded GIFs (either file_ids or URLs)
    gifs = [
        {
            'id': '1',
            'file_id': 'CgACAgIAAxkBAAMJZxLYPO2jcqzPIsUS__WwYP-C4FIAAjdLAAJr2CFLtbOoO_H9ma02BA',
            'title': 'дінаху',
            'description': 'гіф дінаху',
        },
        {
            'id': '2',
            'file_id': 'CgACAgIAAxkBAAMfZxP8Tp382lblvaDlfWLjrriI_ycAAkYpAALIfVBKWoBbTrFxnVk2BA',  # Use a Telegram file_id if uploaded
            'title': 'розумний дофіга да',
            'description': 'гіф розумний дофіга да',
        },
        {
            'id': '3',
            'file_id': 'CgACAgIAAxkBAAMhZxP8ZAvOYE7lMbqj293TgUOSJsQAAj8sAAJlvdBLhJAV8AABeuRVNgQ',  # Use a Telegram file_id if uploaded
            'title': 'питання відсутні',
            'description': 'гіф питання відсутні',
        }
    ]

    # Prepare results for the inline query response
    results = []
    for gif in gifs:
        results.append(InlineQueryResultCachedGif(
            id=gif['id'],  # Unique identifier for this result
            gif_file_id=gif['file_id'],  # The file_id of the GIF
            title=gif['title'],  # Title of the GIF
            description=gif['description'],  # Description of the GIF
        ))

    results.append(InlineQueryResultArticle(
        id='text_1',  # Unique identifier for the text result
        title='Some Info',  # Title of the text result
        input_message_content=InputTextMessageContent(
            message_text='This is a separate text result that provides additional information or context.'
        ),
        description='This text is for context and does not include any media.'
    ))

    logger.debug("Results: %s", results)
    # Send the results back to Telegram
    self.answerInlineQuery(
        query_id,
        results,
        switch_pm_text="Add my own"
    )
