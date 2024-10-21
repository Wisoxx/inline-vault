def translate(lang: str, key: str, values: dict = None):
    translations = {
        'en': {
            'start': 'Hi. I will be the one keeping your media safe and always available.',
            'delete': 'Now send me all the media you want to delete. Send /cancel to cancel',
            'cancelled': 'Successfully canceled.',
            'finish deleting': 'Done deleting.',
            'not recognized': 'Sorry, I don\'t recognize that media.',
            'added': 'Successfully added.',
            'duplicate': 'You already have that in your collection',
            'deleted': 'Successfully deleted. Send next or /done to stop',
            'not found': 'That media was not found in your collection',
            'describe': 'Please provide a description for this media. Type /cancel to cancel',
            'empty': 'No media found. Click here to open bot\'s chat',
            'open': 'Click here to open bot\'s chat'


        },
        'uk': {
            'flag': '🇺🇦',
            'choose_lang': '🇺🇦 Вибери свою мову',
            'lang_set': 'Налаштування мови оновлено',
        },
        'pl': {
            'flag': '🇵🇱',
            'choose_lang': '🇵🇱 Wybierz swój język',
            'lang_set': 'Ustawienia językowe zostały zmienione',

        }
    }
    key = key if key in ("en", "uk", "pl") else "en"  # default lang is english
    translation = translations[lang][key]
    if values:
        return translation.format(**values)
    return translation
