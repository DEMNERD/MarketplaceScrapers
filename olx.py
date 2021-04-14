import requests
from bs4 import BeautifulSoup
import json


def get_all_links():
    """
    Збирає список усіх посилань на категорії
    :return: Повертає список посилань на категорії
    """
    resp = requests.get('https://www.olx.ua/')  # "Переходимо на сторінку"
    soup = BeautifulSoup(resp.text, 'lxml')
    # Оголошуємо змінну для зберігання в ній поточної сторінки в форматі об`єкту BeautifulSoup
    categories = [i.get('href', '') for i in soup.find_all('a', {'class': 'link-relatedcategory'})]
    # Дістаємо усі посилання на категорії
    return categories  # Повертаємо кінцевий список


def get_products_by_main_url(main_url: str = 'https://www.olx.ua/uk/slavutich/'):
    """
    Отримує інформацію про всі оголошення з початкової сторінки категорії (міста)
    :param main_url: Посилання з товарами
    :return: Список з оголошеннями
    """
    current_page = 0  # Оголошуємо змінну для зберігання в ній номеру поточної сторінки
    results = []  # Оголошуємо змінну для зберігання в ній продуктів поточної сторінки
    while not current_page or blocks:  # За умови, що мии зараз на першій сторінці та на останній переглянутій є товари
        current_page += 1  # Збільшуємо значення змінної з номером поточної сторінки на 1
        resp = requests.get(f'{main_url}?page={current_page}')  # "Переходимо на сторінку"
        soup = BeautifulSoup(resp.text, 'lxml')
        # Оголошуємо змінну для зберігання в ній поточної сторінки в форматі об`єкту BeautifulSoup
        blocks = soup.find_all('div', {'class': 'offer-wrapper'})
        # Знаходимо усі елементи оголошень
        tmp = []  # Оголошуємо тимчасову змінну
        for block in blocks:  # Для кожного оголошення в оголошеннях
            price = block.find('p', {'class': 'price'})
            price = price.find('strong').text if price else ''
            # Знаходимо елемент ціни та отримуємо її
            name = block.find('strong').text
            # Отримуємо назву товару
            category = block.find('small', {'class': 'breadcrumb x-normal'}).text.strip()
            # Отримуємо назву категорії товару
            date = block.find('td', {'valign': 'bottom', 'class': 'bottom-cell'}).find_all(
                'small', {'class': 'breadcrumb x-normal'}
            )[1].text.strip().replace('  ', ' ')
            # Отримуємо дату публікації та час публікації (час тільки при сьогоднішній публікації)
            link = block.find('a').get('href').split('#')[0].split('?')[0]
            # Отримуємо посилання на публікацію
            formed = {
                    'name': name,
                    'price': price,
                    'category': category,
                    'date': date,
                    'link': link
                }
            # Формуємо словник зі значеннями
            if formed not in results:  # Перевіряємо, чи є таке оголошення в списку результатів
                tmp.append(formed)  # Додаємо словник до списку оголошень поточної сторінки
        if not tmp:  # Якщо оголошень не було, значить сторінка порожня
            break  # Зупиняємо цикл
        results += tmp  # Додаємо оголошення з поточної сторінки в загальний список
    return results  # Повертаємо список з усією інформацією


if __name__ == '__main__':  # Якщо програма виконується самостійно (не є імпортованим модулем)
    links = get_all_links()  # Отримуємо список усіх посилань на підкатегорії
    res = []  # Оголошуємо змінну, в яку будемо записувати усі оголошення
    for link in links:  # Для кожного посилання
        res += get_products_by_main_url(link)  # Додаємо результат парсингу в нашу змінну з результатами
    with open('olx-result.json', 'w') as file:
        json.dump(res, file)
    # Записуємо усі товари в файл olx-result.json
