from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Catalog')],
    [KeyboardButton(text='Cart')],
    [
        KeyboardButton(text='Contacts'),
        KeyboardButton(text='About us'),
    ]
])
