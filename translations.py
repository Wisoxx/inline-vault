def translate(lang: str, key: str, values: dict = None):
    translations = {
        'en': {
            'start': 'Hi. I will be the one keeping your media safe and always available\n\nYou can send media via simply by writing @inlinevaultbot inside your text field.\nTo add new media firstly, just send it to me, then send me description/tags you want to use to find that media. If you want to delete something, send /delete and then send everything you want to delete',
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
            'open': 'Click here to open bot\'s chat',
            'try': 'Try it out!',
            'error': 'Something went wrong',
            'no records': 'You haven\'t added anything. Click here to open bot\'s chat'
        },
        'uk': {
            'start': 'Привіт. Я буду зберігати твої медіа в безпеці і під рукою\n\nТи можеш висилати медіа просто вписуючи @inlinevaultbot в текстовому полі.\nЩоб додати нове медіа, спершу просто вишли мені його, а потім вишли опис/теги за допомогою яких ти хочеш знаходити конкретну річ. Якщо хочеш видалити щось, вишли /delete і потім все, що хочеш видалити',
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
            'open': 'Натисни тут, щоб відкрити чат з ботом',
            'try': 'Спробуй!',
            'error': 'Щось пішло не плану',
            'no records': 'Ти ще нічого не додав. Натисни тут, щоб відкрити чат з ботом'
        },
        'pl': {
            'start': 'Cześć. Będę czuwać nad bezpieczeństwem twoich mediów i ich ciągłą dostępnością\n\nMożesz wysłać media przez po prostu pisząc @inlinevaultbot w polu tekstowym.\nAby dodać nowe media, po prostu wyślij je do mnie, a następnie wyślij mi opis/tagi, których chcesz użyć, aby znaleźć te media. eśli chcesz coś usunąć, wyślij /delete, a następnie wyślij wszystko, co chcesz usunąć',
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
            'open': 'Kliknij tutaj, aby otworzyć czat bota',
            'try': 'Spróbuj!',
            'error': 'Coś poszło nie tak',
            'no records': 'Jeszcze niczego nie dodałeś. Kliknij tutaj, aby otworzyć czat bota'
        }
    }
    lang = "uk" if lang == "ru" else lang  # change russian to ukrainian
    lang = lang if lang in ("en", "uk", "pl") else "en"  # default lang is english
    translation = translations[lang][key]
    if values:
        return translation.format(**values)
    return translation
