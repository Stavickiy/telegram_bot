def pluralize(num: int, one: str, few: str, many: str) -> str:
    """
    Функция для склонения слова в зависимости от числа.

    Args:
        num (int): Число, от которого зависит склонение.
        one (str): Слово в форме единственного числа (1 товар).
        few (str): Слово в форме для нескольких (2 товара).
        many (str): Слово в форме для множества (5 товаров и т.д.).

    Returns:
        str: Склоненное слово в зависимости от числа.
    """
    num = abs(num)  # Берем модуль числа, чтобы избежать отрицательных чисел
    if num % 10 == 1 and num % 100 != 11:
        return one
    elif 2 <= num % 10 <= 4 and (num % 100 < 10 or num % 100 >= 20):
        return few
    else:
        return many


def split_list(input_list: list) -> list:
    """
    Используем list comprehension для создания списка списков по 2 элемента

    Args:
        input_list (list): Список элементов.

    Returns:
        list: Список списков по 2 элемента.
    """
    return [input_list[i:i+2] for i in range(0, len(input_list), 2)]
