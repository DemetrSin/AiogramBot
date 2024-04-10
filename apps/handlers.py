from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import F, Router

import apps.keyboard as kb


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=kb.main)
    await message.reply('How are you?')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.reply('What is you problem?')
