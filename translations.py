def translate(lang: str, key: str, values: dict = None):
    translations = {
        'en': {
            'start': 'Hi. I will be the one keeping your media safe and always available.',
            'delete': 'Now send me all the media you want to delete. Send /cancel to cancel',
            'cancelled': 'Successfully canceled',
            'finish deleting': 'Done deleting',
            'not recognized': 'Sorry, I don\'t recognize that media.',
            'added': 'Successfully added',
            'duplicate': 'You already have that in your collection',
            'deleted': 'Successfully deleted. Send next or /done to stop',
            'not found': 'That media was not found in your collection',
            'describe': 'Please provide a description for this media. Type /cancel to cancel',
            'empty': 'No media found. Click here to open bot\'s chat',
            'open': 'Click here to open bot\'s chat'
        },
        'uk': {
            'start': 'Привіт. Я буду зберігати твої медіа в безпеці і під рукою',
            'delete': 'Тепер надішли мені всі медіа, які ти хочеш видалити. Надішли /cancel, щоб відмінити',
            'cancelled': 'Успішно скасовано.',
            'finish deleting': 'Видалення завершено',
            'not recognized': 'Вибач, я не можу розпінати дане медіа',
            'added': 'Успішно додано',
            'duplicate': 'Ти вже маєш це в своїй колекції',
            'deleted': 'Успішно видалено. Надішли /done, щоб завершити',
            'not found': 'Це медіа не знайдено в твоїй колекції',
            'describe': 'Надай опис цьому медіа. Надішли /cancel, щоб скасувати',
            'empty': 'Нічого не знайдено. Натисни тут, щоб відкрити чат з ботом',
            'open': 'Натисни тут, щоб відкрити чат з ботом'
        },
        'pl': {
            'start': 'Cześć. Będę czuwać nad bezpieczeństwem twoich mediów i ich ciągłą dostępnością.',
            'delete': 'Teraz wyślij mi wszystkie media, które chcesz usunąć. Wyślij /cancel, żeby anulować',
            'cancelled': 'Pomyślnie anulowano',
            'finish deleting': 'Usuwanie zakończono',
            'not recognized': 'Przepraszam, nie rozpoznaję tego media',
            'added': 'Pomyślnie dodano',
            'duplicate': 'Masz to już w swojej kolekcji',
            'deleted': 'Pomyślnie usunięto. Wyślij kolejne albo /done, żeby zatrzymać',
            'not found': 'Tego media nie znaleziono w twojej kolekcji',
            'describe': 'Podaj opis tego nośnika. Wyślij /cancel, żeby anulować',
            'empty': 'Nie znaleziono mediów. Kliknij tutaj, aby otworzyć czat bota',
            'open': 'Kliknij tutaj, aby otworzyć czat bota'
        }
    }
    lang = lang if lang in ("en", "uk", "pl") else "en"  # default lang is english
    translation = translations[lang][key]
    if values:
        return translation.format(**values)
    return translation
