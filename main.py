from collections import UserDict
from datetime import datetime, timedelta
import re
from functools import wraps
import pickle

class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value: str):

        self.validation(value)

        super().__init__(value)


    def validation(self, value):
        pattern = r'\d'
        regular_value = re.findall(pattern, value)
        if list(value) == regular_value:
            if len(value) == 10:
                return value
            else:
                print("not 10 nums")
                raise ValueError ("Invalid number. Use 10 nums")
    
        else:
            print("not a number")
            raise ValueError("Invalid number format. Not a number")
        
class Birthday(Field):
    def __init__(self, value: str) -> datetime:
        try:
            today = datetime.today().date()
            b_day = datetime.strptime(value, "%d.%m.%Y").date()
            value = b_day if today >= b_day else None
        except:
            print("Invalid date format. Use DD.MM.YYYY")
            return self.value
        
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday = None

    def add_phone(self, p_number: str):
        phone = self.find_phone(p_number)
        if phone:
            print( "Phone exists")
            return
        valid_phone = Phone(p_number)
        self.phones.append(valid_phone)
    
    def remove_phone(self, rem_ph_number):
        self.phones = [p for p in self.phones if p.value != rem_ph_number]
    
    def edit_phone(self, find_num: str, replace_num: str):
        phone = self.find_phone(find_num)
        if not phone:
            print( "Phone not found")
            return        
        phone.value = Phone(replace_num).value
    
    def find_phone(self, find_num: str) -> Phone:
        for p in self.phones:
            if find_num == p.value:
                return p
    
    def add_birthday(self, b_date: str):
        self.birthday = Birthday(b_date)

    def __str__(self):
        try:
            b_day = self.birthday.value
        except:
            b_day = None
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {b_day}"

class AddressBook(UserDict):

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name) -> Record:
        return self.data.get(name)

    def delete(self, del_record: str):
        d = self.find(del_record)
        if not d:
            print( "Record not found")
            return
        self.data.pop(del_record)

    def get_upcoming_birthdays(self):    

        today = datetime.today()
        b_users = []

        for name, user in self.data.items():
            user_year = str(user.birthday.value.year)
            year_now = str(today.year)
            user_data = str(user.birthday.value)
            last_birthday = re.sub(user_year, year_now, user_data)
            last_birthday_to_data = datetime.strptime(last_birthday, "%Y-%m-%d")
            if -1 <= (last_birthday_to_data - today).days < 6:

                match last_birthday_to_data.weekday():
                    case 5:
                        last_birthday_to_data = last_birthday_to_data + timedelta(days=2)
                    case 6:
                        last_birthday_to_data = last_birthday_to_data + timedelta(days=1)
        
                b_users.append({"name": user.name.value, "congratulation_date": last_birthday_to_data.strftime("%Y.%m.%d")})
        return b_users

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ == "add_contact" or func.__name__ == "change_username_phone":
                return "Phone is to short. Give me name and full phone number please."
            if func.__name__ == "show_phone":
                return "Give me name. Enter the argument [name]"
            if func.__name__ == "add_birthday":
                return "Give me [ім'я] [дата народження]"
            if func.__name__ == "show_birthday":
                return "Give me [ім'я]"            
            
        except KeyError:
            return "No such name!"
        except IndexError:
            if func.__name__ == "add_contact":
                return "Insufficient data. Give me name and full phone number please."
            if func.__name__ == "change_username_phone":
                return "Insufficient data. Give me [ім'я] [старий телефон] [новий телефон]."
            if func.__name__ == "add_birthday":
                return "Insufficient data. Give me [ім'я] [дата народження]."
            if func.__name__ == "show_birthday":
                return "Insufficient data. Give me [ім'я]."            
        except AttributeError:
            return "Can`t update birthday."

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_username_phone(args, book: AddressBook):
    name, find_num, replace_num, *_ = args
    record = book.find(name)
    record.edit_phone(find_num, replace_num)
    return "Phone chenged"

@input_error
def show_phone(args,  book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:        
        return "Wrong contact."
    p_nums = ""
    p = 0
    while p < len(record.phones):
        p_nums += str(record.phones[p]) + "\n"
        p += 1
    return p_nums

@input_error
def add_birthday(args,  book: AddressBook):
    name, b_day, *_ = args
    record = book.find(name)
    if record is None:        
        return "Wrong contact."
    record.add_birthday(b_day)
    message = "Birthday contact updated."
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:        
        return "Wrong contact."
    return record.birthday

@input_error
def birthdays(book: AddressBook):
    record = book.get_upcoming_birthdays()
    if record is None:        
        return "No BD"
    return record

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    book = load_data()
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "all":
            for name, record in book.data.items():
                print(record)
        elif command == "change":
            print(change_username_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()