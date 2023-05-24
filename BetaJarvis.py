from collections import UserDict
from datetime import datetime
import re
import pickle
import json
from abc import abstractmethod, ABC
import shutil
from pathlib import Path




class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):


    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value: str):
        if value.isalpha() or not value.startswith('+380') or len(value) != 13:
            raise ValueError
        self.__value = value

    def __repr__(self) -> str:
        return self.value


class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            self.__value = value
        else:
            self.__value = self.__set_date(value)

    @staticmethod
    def __set_date(bday: str):
        date_types = ["%d/%m/%Y", "%d/%m"]
        for date_type in date_types:
            try:
                date = datetime.strptime(bday, date_type).date()
                return date
            except ValueError:
                pass
        raise TypeError("Incorrect date format, should be dd/mm/yyyy or dd/mm")
        
    def __str__(self) -> str:
        return str(self.value)


class Adress(Field):
    pass


class Email(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, val):
        if re.match(r'[a-zA-Z]{1}\S+@[a-zA-Z]+\.\w\w+', val):
            self.__value = val
        else:
            self.__value = 'E-mail doesn`t correct'
    

class Record:
    def __init__(self, name: Name, phones: list[Phone] = [], birthday = None, adress: Adress = None, email:Email = None) -> None:
        self.name = name
        self.phones = phones
        self.birthday = birthday
        self.adress = adress
        self.email = email

    def days_to_birthday(self):
        self.day = int(self.birthday.value.day)    
        self.month = int(self.birthday.value.month)    
        today = datetime.today()
        bd_date = datetime(day= self.day, month= self.month, year= today.year)
        count_days = bd_date-today
        if count_days.days < 0:
            bd_date = datetime(day= self.day, month= self.month, year= today.year + 1)
            count_days = bd_date-today
        return f'{count_days.days} days\n' 

    def add_phone(self, phone: Phone):
        if phone not in self.phones:
            self.phones.append(phone)
            return f'I add new number phone {phone.value} to contact {self.name.value}.'
        else:
            return 'This phone number already exists.'
        
    def dell_phone(self, phone: Phone):
        for p in self.phones:
            if p.value == phone.value:
                self.phones.remove(p)
                return f'I remove number phone {p.value}.'
        return f"I don't find this number."
    
    def change(self, phone: Phone, new_phone: Phone): 
        self.dell_phone(phone)
        self.add_phone(new_phone)
        return 'Done!'

    def __str__(self) -> str:
        return ', '.join([str(p) for p in self.phones])
    
    def __repr__(self) -> str:
        return str(self)


class AddressBook(UserDict):
    index = 0
    def add_contact(self, record: Record):
        self.data[record.name.value] = record

    # def display_contact(self, name):
    #     output = f"---------------------------------------------------------\n{name.capitalize()}:\n"
    #     for phone in self.data[name].phones:
    #         output += f"{phone.value}\n"
    #     return output

    def find_phone(self, name: Name):
        for contact in self.data:
            if contact == name.value:
                return self.data[contact]
        return f"Contact {name.value} not found."
    
    def dell_contact(self, name: Name):
        for contact in self.data:
            if contact == name.value:
                self.data.pop(contact)
                return f"Contact {name} removed."
        return f'Contact {name} not found.'
    
    def save_file (self):
        name_file = 'contacts.bin'
        with open(name_file, "wb") as fh:
            pickle.dump(self.data, fh)

    def read_file(self):
        name_file = 'contacts.bin'
        try:
            with open(name_file, "rb") as fh:
                self.data = pickle.load(fh)
        except FileNotFoundError:
            pass
        except AttributeError:
            pass

    def show_all(self, arg = None, *args):
        print("We made it to the contacts")
        if arg:
            items_per_page = int(arg)
            result = "that was the last page \n"
            # pg = self.iterator(items_per_page)
            pg = display_rec.iterator(items_per_page)
            for i in pg:
                print(i)
                input("Press Enter to see the next page\n>>>")
        else:
            result = ""
            for name in self.data.keys():
                # result += self.display_contact(name)
                result += display_rec.generate_text(name)
        return result

    def find(self, value):
        for key, rec in self.data.items():
            if value in key:
                print(f'{key}: {rec.phones}')
            else:
                for phone in rec.phones:
                    if value in phone.value:
                        print(f'{key}: {rec.phones}')
        return ''
    
    def __str__(self):
        result = []
        for record in self.data.values():
            result.append(f"{record.name.value}: {', '.join([phone.value for phone in record.phones])} Birthday: {record.birthday}")
        return "\n".join(result)


class Note(): 

    def __init__(self, name, text):
        self.name = name #Стара версія імені: datetime.now().strftime("%S%M%H-%d%m%y")
        self.value = text
        self.tags = []

    def add_tag(self, *tags):
        for tag in tags:
            self.tags.append(tag)

    def __str__(self):
        #output = ("-" * 70) + f"\nNote {self.name}:\n{self.value}\n"
        output = f"Note {self.name}:\n{self.value}\n"
        if self.tags != []:
            output += f"Tags: {self.tags}\n"
        # output += ("-" * 70) + "\n"
        return output


class Notebook(UserDict):

    def __init__(self):
        self.data = {}

    def add_note(self, *data): # Додавання нотатки, у якості агрументів - рядки що приходять від парсера. оскільки мій парсер ріже текст на фрагменти у місцях, де були коми, кількість цих рядків може бути довільною.
        if self.data != {}:
            name = str(int(list(self.data.keys())[-1]) + 1)
        else: name = "1"
        text = ", ".join(data) # Як зазначено вище, текст складається із довільної кількості рякдів, тому з них слід зібрати один цілісний текст і повернути на місце коми, стерті парсером.
        if not text or text == "":
            return f"An empty note cannot be added"
        note = Note(name, text)
        self.data[note.name] = note
        return f"Note {note.name} was added"

    def search_by_note(self, *keywords):   # Пошук нотаток за ключовими словами в іменах, вмісті, або тегах. Якщо не введене ключове слово, показує всі нотатки (аналог show all із телефонної книги). Зараз пошук працює у щедрому режимі - збіг навіть в одного слова із багатьох дає позитивний результат.
        result = ""
        if not keywords:
            for note in self.data.values():
                # result += str(note)
                result += str(display_note.generate_text(note.name))
            return result
        notes_to_show = []
        for keyword in keywords:
            for note in self.data.values():
                if (keyword in note.name or keyword in note.value or keyword in note.tags) and note.name not in notes_to_show:
                    # result += str(note)
                    result += display_note.generate_text(note.name)
                    notes_to_show.append(note.name)
        if result == "":
            return f"No matching notes found"
        return result

    def remove_note(self, note_name, *args): # Видалення нотаток за ім'ям.
        if not note_name or note_name == "":
            return "Note name was not specified"        
        if note_name in self.data.keys():
            del self.data[note_name]
            return f"Note {note_name} removed"
        return f"Seems like note {note_name} does not exist already"
    
    def edit_note(self, note_name, *new_text): # Редагування вмісту нотатки за ім'ям. Як і раніше, збирає текст докупи після того, що з ним робить парсер.
        if note_name in self.data.keys():
            text = ", ".join(new_text)
            if not text or text == "":
                return f"An empty note cannot be added"
            self.data[note_name].value = text
            return f"The content of note {note_name} was edited"
        return f"Note {note_name} was not found"

    def add_tag(self, note_name, *tags): # Додає теги (довільну кількість) до нотатки за ім'ям. 
        if note_name not in self.data.keys():
            return f"Note {note_name} not found"
        result = ""
        for tag in tags:
            if tag != "":
                self.data[note_name].add_tag(tag)
                result += f"Tag [{tag}] added\n"
        return f"An empty tag cannot be added" if result == "" else result

    def remove_tag(self, note_name, *tags): # Видаляє теги (довільну кількість) із нотатки за ім'ям.
        result = ""
        for tag in tags:
            if tag in self.data[note_name].tags:
                self.data[note_name].tags.remove(tag)
                result += f"Tag {tag} was removed from note {note_name}\n"
            else:
                result += f"Tag {tag} not found in note {note_name}\n"
        return result

    def to_dict(self): # Перетворює всю інформацію про нотатки у словник, придатний для запису у файл
        data = {}
        for name, note in self.data.items():
            data[name] = {"text": note.value,"tags": note.tags}
        return data

    def from_dict(self, file_data): # Перетворює словник із файлу в інформацію про нотатки
        for name, value in file_data.items():
            note = Note(name, value["text"])
            note.tags = value["tags"]
            self.data[note.name] = note

    def save(self): # Зберігає словник у файл json
        converted_data = self.to_dict()
        with open("notebook_data.json", "w") as file:
            json.dump(converted_data, file)

    def load(self): # Завантажує словник із файлу json
        try:
            with open("notebook_data.json", "r") as file:
                recovered_data = json.load(file)
            if recovered_data != {}:
                self.from_dict(recovered_data)
        except FileNotFoundError:
            print("notebook_data.json was not found")


class DisplayData(ABC):
    @abstractmethod
    def __init__(self, book):
        self.book = book
        self.divider = "-" * 70 + "\n"

    @abstractmethod
    def generate_text(self, name):
        pass 

    def iterator(self, items_per_page, *args):
        start = 0
        keys = list(self.book.data.keys())
        while True:
            result = ""
            current_keys = keys[start:start + items_per_page]
            if not current_keys:
                break
            for name in current_keys:
                result += self.generate_text(name)
            yield result
            start += items_per_page


class DisplayRecord(DisplayData):
    
    def __init__(self, book):
        super().__init__(book)
    
    def generate_text(self, name):
        result = "" + self.divider        
        result += name.capitalize() + "\n"
        for phone in self.book.data[name].phones:
            result += f"{phone.value}\n"
        return result


class DisplayNote(DisplayData):
    def __init__(self, book):
        super().__init__(book)

    def generate_text(self, name):
        result = "" + self.divider        
        result += f"{str(self.book.data[name])}\n"
        return result




FILE_MASK = {"images":['*.jpeg', '*.png', '*.jpg', '*.svg'] , 
             "documents":['*.doc', '*.docx', '*.txt', '*.pdf'] ,
             "videos":['*.avi', '*.mp4', '*.mov', '*.mkv'] , 
             "sounds":['*.mp3', '*.ogg', '*.wav', '*.amr'], 
             "archives":['*.zip', '*.gz', '*.tar', '*.rar'] , 
             "others":['*.*'] }

# translation 
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()    


def translate(name):
    return name.translate(TRANS)


# normalise name
def normalise(name):
    rep = re.compile('[^a-zA-Zа-яА-я,\d]')
    name = rep.sub('_', name)
    return name

def def_folder_list():
    result = []
    for d_f in FILE_MASK.keys():
        result.append(d_f)
    return result


# Sort function    
def sort_file(path, root_path):
    for x in path.iterdir():
        if x.is_dir():
            print(x)
            if not x.name in def_folder_list():
                sort_file(Path.joinpath(path, x.name), root_path)
                x.rmdir()
        else:
            
            for k,v in FILE_MASK.items():
                for ex in v:
                    for x in path.glob(ex):
                        
                        files_dir =  root_path / k
                        if not files_dir.exists():
                            files_dir.mkdir()
                            
                        src_path = Path.joinpath(path, x.name)
                        dst_path = Path.joinpath(files_dir, normalise(translate(x.stem)) + x.suffix)
                        shutil.move(src_path, dst_path) 
                        
                        if k == 'archives':
                            shutil.unpack_archive(dst_path, Path.joinpath(files_dir, normalise(translate(x.stem))))
                          
# main           
def main_clean(arg):
    
    try:
        path = Path(arg)
        print("Sorting the files...")
        sort_file(path, path)
        print("Sorting Completed...")   
    except:
        print('Path not found')
        print('example: scrypt.py some_folder ')
        
# if __name__ == "__main__":
#     main_clean()



#import dop

def cheker(text):
    yes_input = ['y', 'yes', '+', 'ok', 'right', 'sure', 'yep', 'course']
    if any(word in text.lower() for word in ['add', 'ad', 'aad', 'aadd', 'append', 'plus', 'put', 'join', 'include']):
        add_correct_input = input('Do you mean, that you would like to add something? \nFour options (please, choose one): 1. Contact. 2. Birthday. 3. Note. 4. Tag. 1/2/3/4 >>> ')
        if add_correct_input == '1':
            print("If you'd like to add contact, use this command  ->  add contact, name, phone_number, birthday, address, email. \nBirthday, address and email are optional.")
        elif add_correct_input == '2':
            print("If you'd like to add birthday for contact, use this command  ->  add birthday, name, birthday. \nFormat of birthday looks like this: day.month.year")
        elif add_correct_input == '3':
            print("If you'd like to add note, use this command  ->  add note, text")
        elif add_correct_input == '4':
            print("If you'd like to add tag, use this command  ->  add tag, note, tag")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['remove', 'delete', 'rem', 'remowe', 'remov', 'del', 'delet', 'cut off', 'cut', 'take out', 'clean']):
        remove_correct_input = input('Do you mean, that you would like to delete something? \nFour options (please, choose one): 1. Phone. 2. Contact. 3. Note. 4. Tag. 1/2/3/4 >>> ')
        if remove_correct_input == '1':
            print("If you'd like to delete phone, use this command  ->  delete phone, name, phone_number")
        elif remove_correct_input == '2':
            print("If you'd like to delete contact, use this command  ->  delete contact, name, phone_number")
        elif remove_correct_input == '3':
            print("If you'd like to remove note, use this command  ->  remove note, note_name")
        elif remove_correct_input == '4':
            print("If you'd like to remove tag, use this command  ->  remove tag, note_name, tag")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in [' find', 'fnd', 'fid', 'search ', 'seach', 'searh', 'sarch', 'serch', 'realize', 'notice', 'detect']):
        find_correct_input = input('Do you mean, that you would like to find something? \nThree options (please, choose one): 1. Phone. 2. Information about contact by part of name or phone. 3. Search for notes.  1/2/3 >>> ')
        if find_correct_input == '1':
            print("If you'd like to find phone, use this command  ->  find phone, name")
        elif find_correct_input == '2':
            print("If you'd like to find information about contact, use this command  ->  find, part of name/phone")
        elif find_correct_input == '3':
            print("If you'd like to search for notes, use this command  ->  search, keyword")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['change', ' change', 'chage', 'chenge', 'swap', 'exchange', 'rewrite', 'switch', 'replace', 'new']):
        change_correct_input = input('Do you mean, that you would like to change the phone? y/n >>> ')
        print("If you'd like to change the phone, use this command  ->  change phone, name, new_phone_number") \
            if change_correct_input.lower() in yes_input else print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['birthday', 'day', ' birthday ', 'birthday ', 'bday', 'birthdate', 'bd', 'birth', 'date']):
        birthday_correct_input = input('Do you mean, that you would like to do smth with birthday? \nTwo options (please, choose one): 1. Add birthday. 2. Days to birthday. 1/2 >>> ')
        if birthday_correct_input == '1':
            print("If you'd like to add birthday to contact, use this command  ->  add birthday, name, birthday \nFormat of birthday looks like this: day.month.year")
        elif birthday_correct_input == '2':
            print("If you'd like to see how many days to birthday of contact, use this command  ->  days to birthday, name")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in [' show', 'show', 'see', ' show all', 'show me', 'aal', 'display', 'look', 'watch', 'view', 'each']):
        show_contact_correct_input = input('Do you mean, that you would like to see contacts?  y/n >>> ')
        print("If you'd like to see the contacts, use this command  ->  show all") \
            if show_contact_correct_input.lower() in yes_input else print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['note ', 'not', 'note', 'noter', 'nots', 'message', 'reminder', 'record', 'notes', 'notation', 'comment', 'remark']):
        note_correct_input = input('Do you mean, that you would like to do smth with notes? \nTwo options (please, choose one): 1. Add. 2. Remove.  1/2 >>> ')
        if note_correct_input == '1':
            print("If you'd like to add note, use this command  ->  add note, text")
        elif note_correct_input == '2':
            print("If you'd like to remove note, use this command  ->  remove note, note_name")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['marker', 'key', 'keyword', 'keywords', 'label', 'sticker', 'tag', 'teg', 'tags', 'tegs']):
        tag_correct_input = input('Do you mean, that you would like to do smth with tag? \nTwo options (please, choose one): 1. Add. 2. Remove. 1/2 >>> ')
        if tag_correct_input == '1':
            print("If you'd like to add tag, use this command  ->  add tag, note, tag")
        elif tag_correct_input == '2':
            print("If you'd like to remove tag, use this command  ->  remove tag, note, tag")
        else:
            print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['clean', 'sort', 'file', 'files', 'cleen', 'clen', 'classify', 'category']):
        cleaner_correct_input = input('Do you mean, that you would like to sort all file by folder?  y/n >>> ')
        print("If you'd like to sort all file by folder, use this command  ->  cleaner, folder") \
            if cleaner_correct_input.lower() in yes_input else print('Unknown command, type "help" to see the list of commands')
    elif any(word in text.lower() for word in ['hi', 'hey', 'yo', 'morning', 'afternoon', 'evening', 'sup', 'hiya']):
        print('Hello! How can I help you?')


def command_error(func):
    def inner(*args):
        try:
            return func(*args)
        except KeyError:
            return 'Unknown command, type "help" to see the list of commands'
        except IndexError:
            return 'IndexError occured'
        except TypeError:
            return 'TypeError occured'
        except ValueError:
            return 'ValueError occured'
    return inner

def parcer(user_input):
    user_input += ","
    disected_input = user_input.lower().split(",")
    disected_input.remove('')
    results = list()
    for i in disected_input:
        results.append(i.lower().strip(' '))
    return results



contacts = AddressBook()
notebook = Notebook()
display_rec = DisplayRecord(contacts)
display_note = DisplayNote(notebook)




def greeting(*args):
    print("Hello! How can i help you?")

def add_ct(name, phone, *args:tuple): #допрацювати для всіх необовязкових параметрів bd=None, address=None, mail=None, 
    tupl = tuple(args)
    name = Name(name)
    phone = Phone(phone)
    bd = None
    address = None
    mail = None
    if len(tupl) > 0:
        bd = Birthday(tupl[0])
    if len(tupl) > 1:
        address = tupl[1]
    if len(tupl) > 2:
        mail = tupl[2]
    rec = Record(name, [phone], bd, address, mail)
    if name.value in contacts:
        for key_contact in contacts:
            if key_contact == name.value and phone.value not in contacts[key_contact].phones:
                return contacts[key_contact].add_phone(phone)
    else:
        contacts.add_contact(rec)
        return f'Contact {name.value} added'

def add_bd(name, bd, *args):
    name = Name(name)
    bd = Birthday(bd)
    if name.value in contacts.keys():
        contacts[name.value].birthday = bd

#@command_error
def dell_phone(name, phone, *args:tuple):
    name = Name(name)
    phone = Phone(phone)  
    for key_contact in contacts:
        if key_contact == name.value:        
            return contacts[key_contact].dell_phone(phone)
    return 'An entry with the specified name was not found' 

@command_error
def dell_contact(name, *args:tuple):
    # tupl = args[0].split(",")
    name = Name(name)
    return contacts.dell_contact(name)

@command_error
def change_phone(name, old_phone, new_phone, *args:tuple):
    if name in contacts.keys():
        name = Name(name)
        old_phone = Phone(old_phone)
        new_phone = Phone(new_phone)
        record = contacts[name.value]
        return record.change(old_phone, new_phone)
    return f"Can't find {name} in the Addressbook"

def delta_days(name, *args):
    name = Name(name)
    return contacts[name.value].days_to_birthday()

def show_all(step = None, *args):
    return contacts.show_all(step, *args)

def find_phone(name, *args:tuple):
    name = Name(name)
    return contacts.find_phone(name)

def find(keyword, *args:tuple):
    return contacts.find(keyword)

def cleaner(path, *args:tuple):
    
    main_clean(path)

def help(*args):
    commands = [{"command": "hello", "description": "show greeting"},
                {"command": "help", "description": "show all available commands"},
                {"command": "add contact, name, phone_number", "description": "add a new contact"},
                {"command": "add birthday, name, day.month.year", "description": "add a birthday date to a contact"},
                {"command": "delete contact, name, phone_number", "description": "delete  target contact"},
                {"command": "delete phone, name, phone_number", "description": "delete  phone in contact"},
                {"command": "change, name, new_phone_number", "description": "change the phone number of an existing contact"},
                {"command": "days to birthday, name", "description": "days to birthday of contact"},
                {"command": "show all", "description": "show all contacts"},
                {"command": "find phone, name", "description": "show the phone number of a contact"},
                {"command": "find , part of name  or phone", "description": "show contacts that include this part"},
                {"command": "clener , folder", "description": "sort all file by folder"},
                {"command": "add note, text", "description": "save note whith text"},
                {"command": "search, keyword", "description": "Search for notes by keywords in names, contents, or tags"},
                {"command": "remove note, note name", "description": "remove target note"},
                {"command": "add tag, note, tegs", "description": "add tag to note"},
                {"command": "remove tag, note, tegs", "description": "remove tag from note"},
                {"command": "goodbye", "description": "exit Phonebook manager"},
                {"command": "close", "description": "exit Phonebook manager"},
                {"command": "exit", "description": "exit Phonebook manager"}]
    result = ""
    for item in commands:
        result += f'{item["command"]}: {item["description"]}\n'
    return result



@command_error
def handler(command, args):
    functions = {
                "hello": greeting,
                "help": help,
                "add contact": add_ct,
                "add birthday": add_bd,
                "change phone": change_phone,
                "remove phone": dell_phone,
                "remove contact": dell_contact,
                "show all": show_all,
                "search phone": find_phone,
                "search name": find,
                "days to birthday": delta_days,
                "add note": notebook.add_note,
                "remove note": notebook.remove_note,
                "add tag": notebook.add_tag,
                "remove tag": notebook.remove_tag,
                "edit note": notebook.edit_note,
                "search note": notebook.search_by_note,
                "cleaner": cleaner
                }
    if command in functions.keys():
        return functions[command](*args)
    else:
        return cheker(command)



def main():

    contacts.read_file()
    notebook.load()

    while True:
        user_input = parcer(input('Enter a command: \n>>> '))
        command = user_input[0]
        user_input.remove(command)
        args = [arg for arg in user_input]
        if command in ("goodbye", "close", "exit"):
            print("Goodbye!")
            break

        result = handler(command, args)
        if result != "" and result != None: 
            print(result)

#if __name__ == '__main__':
main()