import pickle
import re
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Ім'я не може бути порожнім")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not Phone.validate_phone(value):
            raise ValueError("Номер телефону повинен містити 10 цифр")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        pattern = re.compile(r"^\d{10}$")
        return pattern.match(phone) is not None

class Birthday(Field):
    def __init__(self, value):
        if not self.validate_date(value):
            raise ValueError("Неправильний формат дати. Використовуйте DD.MM.YYYY")
        super().__init__(datetime.strptime(value, "%d.%m.%Y"))

    @staticmethod
    def validate_date(date_text):
        try:
            datetime.strptime(date_text, "%d.%m.%Y")
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", День народження: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Ім'я контакту: {self.name.value}, телефони: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today()
        upcoming = today + timedelta(days=days)
        birthdays_next_week = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year < upcoming:
                    birthdays_next_week.append(record.name.value)
        return birthdays_next_week

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        return "Будь ласка, вкажіть ім'я та дату народження."
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        return f"Контакт з іменем {name} не знайдено."
    record.add_birthday(birthday)
    return f"День народження для {name} додано."

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        return "Будь ласка, вкажіть ім'я."
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Контакт з іменем {name} не знайдено."
    if not record.birthday:
        return f"Інформація про день народження для {name} відсутня."
    return f"День народження {name}: {record.birthday.value.strftime('%d.%m.%Y')}."

@input_error
def birthdays(args, book):
    birthdays_list = book.get_upcoming_birthdays()
    if not birthdays_list:
        return "Немає днів народження на наступному тижні."
    return "\n".join(birthdays_list)

@input_error
def add_contact(args, book):
    if len(args) < 2:
        return "Будь ласка, вкажіть ім'я та телефон."
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) < 3:
        return "Будь ласка, вкажіть ім'я, старий і новий телефон."
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        return f"Контакт з іменем {name} не знайдено."
    record.edit_phone(old_phone, new_phone)
    return f"Телефонний номер для {name} змінено."

@input_error
def show_phone(args, book):
    if len(args) < 1:
        return "Будь ласка, вкажіть ім'я."
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Контакт з іменем {name} не знайдено."
    return ', '.join([phone.value for phone in record.phones])

@input_error
def show_all_contacts(book):
    if not book.data:
        return "Адресна книга порожня."
    return "\n".join([str(record) for record in book.values()])

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = load_data()
    print("Ласкаво просимо до асистента!")
    while True:
        user_input = input("Введіть команду: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("До побачення!")
            break

        elif command == "hello":
            print("Чим я можу допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Неправильна команда.")

if __name__ == "__main__":
    main()
