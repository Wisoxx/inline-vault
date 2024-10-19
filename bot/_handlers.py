from telepot.namedtuple import InlineQueryResultGif


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
            'file_id': 'AAMCAgADGQEAAx9nE_xOnfzaVuW9oOV9YuOuuIj_JwACRikAAsh9UEpagFtOsXGdWQEAB20AAzYE',  # Use a Telegram file_id if uploaded
            'title': 'розумний дофіга да',
            'description': 'гіф розумний дофіга да',
        },
        {
            'id': '3',
            'file_id': 'AAMCAgADGQEAAyFnE_xkC85gTuUxuqPb3dOBQ5ImxAACPywAAmW90EuEkBXwAAF65FUBAAdtAAM2BA',  # Use a Telegram file_id if uploaded
            'title': 'питання відсутні',
            'description': 'гіф питання відсутні',
        }
    ]

    # Prepare results for the inline query response
    results = []
    for gif in gifs:
        results.append(InlineQueryResultGif(
            id=gif['id'],  # Unique identifier for this result
            gif_file_id=gif['file_id'],  # The file_id of the GIF
            title=gif['title'],  # Title of the GIF
            description=gif['description'],  # Description of the GIF
            thumb_url=gif['thumb_url']  # Optional thumbnail URL
        ))

    # Send the results back to Telegram
    self.answerInlineQuery(query_id, results)
