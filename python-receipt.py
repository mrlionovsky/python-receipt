import subprocess
import os
from datetime import datetime

def print_text(text):
    lines = text.split('\n')
    for line in lines:
        if line.strip():  # Проверяем, что строка не пустая
            subprocess.run(f'echo {line} > LPT3', shell=True) #Заменить на нужный нам порт

#Функция создания пустых строк в конце чека. 
#Заточено под Pisiflex PP-7000II и винду, где через Subprocess неккоректно уходят символы переноса строк
def print_empty_lines(num_lines):
    temp_file = 'temp_spaces.txt'
    with open(temp_file, 'w') as f:
        f.write('\n' * num_lines)
    
    os.system(f'type {temp_file} > LPT3')
    
    os.remove(temp_file)

#Создаём прайс в зависимости от выбора пункта меню
def calculate_price(option, quantity):
    if 1 <= option <= 5:
        return quantity * 2
    elif 6 <= option <= 10:
        return quantity * 1.67
    elif option == 11:
        return quantity * 45
    elif option == 12:
        return quantity * 100
    else:
        return 0

#Верх чека. Сюда записываем его номер, здесь печатаются наши данные.
def print_receipt_header(receipt_number, current_datetime):
    header = (
        f"Товарный чек № {receipt_number}\n"
        f"Дата и время: {current_datetime}\n"
        "ИП ВАСЯ ПУПКИН\n"
        "ИНН 192 168 0 1\n"
        "Адрес: НЬЮ-ЙОРК, УЛ. ПУШКИНА, Д. 321, ОФ. 123\n"
        "ТЕЛ. +7 (123) 123-45-67\n"
        "-----------------------------"
    )
    print_text(header)
    return header

#конец чека. 
def print_receipt_footer():
    footer = (
        "-----------------------------\n"
        "Подпись: ____________________\n"
    )
    print_text(footer)
    # Увеличиваем количество пустых строк до 15, чтоб линия отреза была ниже текста.
    print_empty_lines(15)
    # Добавляем команду отреза чека. Команда для Posiflex, для других принтеров может быть другой. Убрать, если на принтере нет такой функции.
    cut_command = b'\x1D\x56\x00'
    with open('LPT3', 'wb') as printer:
        printer.write(cut_command)

def print_receipt(receipt_number, current_datetime, receipt_lines, total_price):
    header = print_receipt_header(receipt_number, current_datetime)
    for line in receipt_lines:
        print_text(line)
    print_text(f"Общая сумма: {total_price:.2f} руб.")
    print_receipt_footer()
    return header

#Выбираем меню. Стандарт для товарных чеков - указание позции / цена.
def main():
    options = [
        "Убить Билла / 2.00 руб ",
        "Убить Килла / 2.00 руб ",
        "Постучать по деревяшке / 2.00 руб ",
        "Постучать по костяшке / 2.00 руб ",
        "Побить деревяшку / 2.00 руб ",
        "Читать сказки / 1.67 руб ",
        "Глотать смазки / 1.67 руб ",
        "Требовать оральные ласки / 1.67 руб ",
        "Лизать маски / 1.67 руб ",
        "Громко каркать / 1.67 руб ",
        "Дощечка / 45.00 руб ",
        "Словечко / 100 руб "
    ]
    total_price = 0
    receipt_lines = []
    receipt_number = input("Введите номер товарного чека: ")
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")

    while True:
        print("Выберите вариант:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("Введите номер варианта: "))
                if 1 <= choice <= 12:
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")
            except ValueError:
                print("Пожалуйста, введите корректный номер варианта.")

        if 1 <= choice <= 10:
            while True:
                try:
                    quantity = int(input("Введите количество минут: "))
                    if quantity > 0:
                        break
                    else:
                        print("Количество минут должно быть больше 0.")
                except ValueError:
                    print("Пожалуйста, введите корректное количество минут.")
            unit = "мин."
        elif 11 <= choice <= 12:
            while True:
                try:
                    quantity = int(input("Введите количество штук: "))
                    if quantity > 0:
                        break
                    else:
                        print("Количество штук должно быть больше 0.")
                except ValueError:
                    print("Пожалуйста, введите корректное количество штук.")
            unit = "шт."
        
        price = calculate_price(choice, quantity)
        total_price += price
        receipt_lines.append(f"{options[choice - 1]} / {quantity} {unit} / {price:.2f} руб.")
        
        while True:
            more = input("Хотите ввести ещё что-то? (y/n): ").strip().lower()
            if more in ['y', 'n']:
                break
            else:
                print("Пожалуйста, введите 'y' или 'n'.")

        if more != 'y':
            break

    # Печать двух копий чека. Для себя, и для клиента.
    header = print_receipt(receipt_number, current_datetime, receipt_lines, total_price)
    print_receipt(receipt_number, current_datetime, receipt_lines, total_price)

    # Запись в файл
    filename = f"{datetime.now().strftime('%Y%m%d')}-{receipt_number}.txt"
    with open(filename, 'w', encoding='windows-1251') as file:
        file.write(header + "\n")
        for line in receipt_lines:
            file.write(line + '\n')
        file.write(f"Общая сумма: {total_price:.2f} руб.\n")
        file.write("-----------------------------\n")
        file.write("Подпись: ____________________\n")

if __name__ == "__main__":
    main()
