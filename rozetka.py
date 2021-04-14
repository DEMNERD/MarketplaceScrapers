import json
import requests


def get_children(input_iterable: [dict, list]):
    """
    Рекурсивна функція для отримання усіх підкатегорій
    :param input_iterable: Об`єкт з множиною категорій
    :return: Усі підкатегорії в множині даних категорій
    """
    all_children = list()  # Оголошуємо список з усіма підкатегоріями
    next_children = []  # Зміна в яку ми зберігаємо множину категорій з яких треба буде дістати наступні підкатегорії
    if isinstance(input_iterable, list) and input_iterable:
        next_children = input_iterable
        # Якщо input_iterable - список, ми записуємо його в next_children
    elif input_iterable.get('children') is None:
        return []
        # Якщо у input_iterable немає підкатегорій, ми повертаємо порожній список
    elif isinstance(input_iterable.get('children'), list) and input_iterable.get('children'):
        next_children = input_iterable.get('children')
        # Якщо підкатегорії у input_iterable являють собою заповнений список, ми ставимо його в next_children
        if isinstance(next_children[0], dict):
            all_children += [i.get('category_id') for i in next_children]
            # Якщо підкатегорії являють собою одновимірний масив,
            # то ми додаємо ідентифікатори підкатегорій в all_children
    elif isinstance(input_iterable.get('children'), dict):
        next_children = list(input_iterable.get('children').values())
        # Якщо ж підкатегорії у input_iterable являють собою словник, ми ставимо набір його в значень next_children
        if isinstance(next_children[0], dict):
            all_children += [i.get('category_id') for i in next_children]
            # Якщо підкатегорії являють собою підкатегорії у input_iterable являють собою словник,
            # без списку в якості елементів, то ми додаємо ідентифікатори підкатегорій в all_children

    for child in next_children:
        # Об`єкти кожної підкатегорії проганяємо через цю ж функцію
        all_children += get_children(child)
    return all_children   # Нарешті повертаємо список з ідентифікаторами усіх категорій


def get_all_categories():
    """
    Функція, яка повертає посилання на всі категорії
    :return: Список посилань на всі категорії
    """
    categories_json = requests.get('https://common-api.rozetka.com.ua/v2/fat-menu/full').json()['data']
    # Отримуємо інформацію з АПІ Розетки в змінну categories_json
    main_categories = categories_json.values()
    # Отримуємо інформацію про "основні категорії" (першого порядку)
    all_categories = set()
    # Прив`язуємо до змінної all_categories тип даних set, щоб запобігти повторення одного і того самого значення
    all_categories.update([i.get('category_id') for i in main_categories if i.get('category_id')])
    # Додаємо до зміної з ідентифікаторами категорій, ідентифікатори "основних категорій"
    for main_category in main_categories:
        all_categories.update(main_category)
        # Додаємо ідентифікатори усіх підкатегорій в відповідний масив
    return all_categories  # Повертаємо масив з ідентифікаторами усіх підкатегорій


def parse_category(category_id: int):
    """
    Збираємл інформацію про товари з певної категорії
    :param category_id: унікальний ідентифікатор кожної категорії
    :return: список з даними про усі товари даної категорії
    """
    page_num = 1  # Номер поточної сторінки
    result = []  # Оголошуємо змінну у яку ми будемо записувати інформацію про товари
    while True:   # Входимо у цикл
        resp = requests.get(
            f'https://xl-catalog-api.rozetka.com.ua/v4/goods/get?front-type=xl&category_id={category_id}&page={page_num}&lang=ua'
        )
        # Отримуємо все, що віддає апі, після get запиту на неї для отримання ідентифікаторів товарів
        # на сторінці під номером page_num
        ids = [str(identifier) for identifier in resp.json()['data']['ids']]
        # Отримуємо ідентифікатори товарів з відповіді на наш запит
        upd = requests.get(
            f'https://xl-catalog-api.rozetka.com.ua/v4/goods/getDetails?front-type=xl&product_ids={",".join(ids)}&lang=ua'
        ).json()['data']
        # Отримуємо інформацію про товари
        if upd[0] in result:
            # За умови того, що інформація про перший товар на сторінці у нас вже є - ми виходимо з функції
            # (Бо це означає, що передостання "переглянута" сторінка - остання) та повертаємо інформацію про товари
            return result
        result += upd
        # Додаємо інформацію про кожен товар в наш кінцевий список
        page_num += 1  # Вказуємоп ерехід на наступну сторінку


if __name__ == '__main__':  # Якщо програма виконується самостійно (не є імпортованим модулем)
    categories = get_all_categories()  # Отримуємо список усіх ідентифікаторів категорій
    res = []  # Оголошуємо змінну, в яку будемо записувати усі товари
    for category in categories:  # Для кожної категорії
        res += parse_category(category)  # Додаємо результат скрапінгу в нашу змінну з результатами
    with open('rozetka-result.json', 'w') as file:
        json.dump(res, file)
    # Записуємо усі товари в файл rozetka-result.json
