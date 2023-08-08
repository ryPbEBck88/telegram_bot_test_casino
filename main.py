import random

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, Text
from aiogram.types import Message


API_TOKEN = ''

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

# Словарь, в котором будут храниться данные пользователя
user: dict = {'in_game': False,
              'game': None,
              'question': None,
              'answer_plays_by': None,
              'answer_payout': None,
              'answer_number': None,
              'answer_change': None,
              'total_games': 0,
              'wins': 0}


# Функция возвращающая случайные целые 2 числа: от 1 до 100 и 1 из (5, 8, 17, 35)
def get_random_numbers() -> list[int]:
    lst: list[int] = []
    for _ in range(5):
        n = random.randint(1, 15)
        lst.append(n)
    # i = random.randint(0, 3)
    # i = [5, 8, 17, 35][i]
    return lst


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer("Привет!\n"
                         "Выбери игру\n"
                         "/bracket (число * число)\n"
                         "Чтобы получить список доступных команд - отправьте команду /help")


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(f'Правила игры:\n\nВыбрать игру(я знаю, что она пока одна)\n'
                         f'/bracket (число * число)\n'
                         f'Написать и отправить ответ на задание\n'
                         f'Для продолжения нажать на название игры\n'
                         f'оно в чате чуть выше или напишите\n'
                         f'в ручную и отправьте. \n'
                         f'Чтобы выйти из игры отправьте команду -\n'
                         f'/cancel')


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands=['cancel']))
async def process_cancel_command(message: Message):
    if user['in_game']:
        await message.answer('Вы вышли из игры. Если захотите сыграть '
                             'снова - напишите об этом')
        user['in_game'] = False
    else:
        await message.answer('А мы и так с вами не играем. '
                             'Может, сыграем разок?')


# Хэндлер срабатывает на выбор игры bracket(скобки)
@dp.message(Text(text=['bracket', '/bracket', 'скобка', '1'], ignore_case=True))
async def bracket(message: Message):
    if not user['in_game']:
        n = get_random_numbers()
        t = [35, 17, 11, 8, 5]
        user['question'] = f'{n[0]} * {35} +\n' \
                           f'{n[1]} * {17} +\n' \
                           f'{n[2]} * {11} +\n' \
                           f'{n[3]} * {8} +\n' \
                           f'{n[4]} * {5} ='
        user['answer_number'] = sum(n[i] * t[i] for i in range(5))
        await message.answer(user['question'])
        user['in_game'] = True
        user['game'] = '/bracket'


# Хэндлер срабатывает на ответы в игре скобка и запускает игру повторно
@dp.message(lambda x: x.text and x.text.strip().isdigit() and user['game'] in ('bracket', '/bracket'))
async def process_numbers_answer(message: Message):
    if user['in_game']:
        if int(message.text) == user['answer_number']:
            await message.answer('Верно!\n')
            n = get_random_numbers()
            t = [35, 17, 11, 8, 5]
            user['question'] = f'{n[0]} * {35} =\n' \
                               f'{n[1]} * {17} =\n' \
                               f'{n[2]} * {11} =\n' \
                               f'{n[3]} * {8} =\n' \
                               f'{n[4]} * {5} ='
            user['answer_number'] = sum(n[i] * t[i] for i in range(5))
            await message.answer(user['question'])
        else:
            await message.answer('Вы ошиблись. попробуйте еще раз!')
            await message.answer(user['question'])


# Функция, которая генерирует номер на рулетке и количество фишек
# для ставки на комплит. Возвращает ставку комплита
def number_and_bet() -> tuple[int, int]:
    complete_numbers = {0: 17, 1: 27, 2: 36, 4: 30, 5: 40, 34: 18, 35: 24}
    n, i = random.choice(list(complete_numbers.items()))
    return n, i


# Функция, которая вычисляет ответы для игры complete
def answer_complete():
    pass


@dp.message(Text(text=['2', 'complete', '/complete'], ignore_case=True))
async def complete(message: Message):
    if not user['in_game']:
        num, amount_of_chips = number_and_bet()
        bet_complete = random.randrange(8, 80) * 50
        user['question'] = f'Номер комплита: {num}\n' \
                           f'Ставка комплита: {bet_complete}\n\n' \
                           f'По чем играет комплит(10, 25, 50, 75, 100)?'
        await message.answer(user['question'])
        user['in_game'] = True
        user['game'] = 'complete'

        user['answer_plays_by'] = 0  # комплит играет по
        for n in (100, 75, 50, 25, 10):
            if bet_complete // (amount_of_chips * n) == 1:
                user['answer_plays_by'] = n
                break

        # сдача с комплита
        user['answer_change'] = bet_complete - user['answer_plays_by'] * amount_of_chips
        user['answer_payout'] = None  # выплата комплита


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_text_answers(message: Message):
    if user['in_game']:
        await message.answer('Мы же сейчас с вами играем. '
                             'Присылайте, пожалуйста, положительные целые числа')
    else:
        await message.answer('Я довольно ограниченный бот, давайте '
                             'просто сыграем в одну из игр?')


if __name__ == '__main__':
    dp.run_polling(bot)