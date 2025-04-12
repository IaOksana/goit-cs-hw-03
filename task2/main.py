import sys # Import sys to exit cleanly on connection failure


from colorama import Fore, Style
from prettytable import PrettyTable
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from bson.objectid import ObjectId

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError


# result_one = db.cats.insert_one(
#     {
#         "name": "barsik",
#         "age": 3,
#         "features": ["ходить в капці", "дає себе гладити", "рудий"],
#     }
# )
# print(result_one.inserted_id)

# result_many = db.cats.insert_many(
#     [
#         {
#             "name": "Lama",
#             "age": 2,
#             "features": ["ходить в лоток", "не дає себе гладити", "сірий"],
#         },
#         {
#             "name": "Liza",
#             "age": 4,
#             "features": ["ходить в лоток", "дає себе гладити", "білий"],
#         },
#     ]
# )
# print(result_many.inserted_ids)

'''
розбиратиме введений користувачем рядок на команду та її аргументи. 
Команди та аргументи мають бути розпізнані незалежно від регістру введення.
'''
def parse_input(user_input):
    stripped_input = user_input.strip()
    # Check if the stripped input is empty
    if not stripped_input:
        print("Please enter a command.")
        return None, [] # Return None for command and empty list for args

    # If not empty, split and process as before
    parts = stripped_input.split()
    cmd = parts[0].lower() # Lowercase the command
    args = parts[1:]       # Get the rest as arguments
    return cmd, args


def helper():
    #створюємо таблицю - Запити для виконання:
    table_help = PrettyTable()
    table_help.field_names = ["Command", "Description"]
    table_help.add_row(["view-all", "виведення всіх записів із колекції."])
    table_help.add_row(["find-cat-info", "ввести ім'я кота та виводить інформацію про цього кота"])
    table_help.add_row(["update-age", "оновити вік кота за ім'ям"])
    table_help.add_row(["add-feature", "додати нову характеристику до списку features кота за ім'ям"])
    table_help.add_row(["delete-cat", "видалення запису з колекції за ім'ям тварини"])
    table_help.add_row(["delete-all-cats", "видалення всіх записів із колекції"])
    table_help.add_row(["add-cat", "."])
    table_help.add_row(["help", "вивести список команд"])
    table_help.add_row(["exit / close", "завершити роботу"])
    table_help.add_row(["hello", "привіт"])

   # --- Formatting Options ---
    # 1. Set alignment (optional)
    # Align 'Command' column to the left, 'Description' to the left
    table_help.align["Command"] = "l"
    table_help.align["Description"] = "l"

    # 2. Set padding width (optional)
    # Add 1 space padding on each side of the text
    table_help.padding_width = 1

    # 3. Set max width for a column (optional)
    # Limit the description column width to, say, 80 characters
    table_help.max_width["Description"] = 40

    # Print the formatted table
    print(table_help)

def view_all(db: MongoClient):
    result = db.cats.find({})
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Age", "Features"]
    for el in result:
        table.add_row([el["_id"], el["name"], el["age"], el["features"]])
    print(table)


def find_cat_info(args, db: MongoClient):
    try:
        name = args[0]
    except IndexError: # Catch potential errors if args[1] is missing after split
        print(Fore.YELLOW + f"Не вистачає аргументів. Потрібно: імя кота.") 
        return # Exit if no cat found
    

    result = db.cats.find_one({"name": name})

    # Check if a result was found
    if not result:
        print(Fore.YELLOW + f"Кіт з ім'ям '{name}' не знайдений.")
        return # Exit if no cat found
    else:
        table = PrettyTable()
        table.field_names = ["ID", "Name", "Age", "Features"]
        table.align = "l" # Align left
        table.padding_width = 1

        table.add_row([
                result.get("_id", "N/A"), # Use .get for safety
                result.get("name", "N/A"),
                result.get("age", "N/A"), 
                ", ".join(result.get("features", []))])
        print(table)


def update_age(args, db: MongoClient):
    try:
        name = args[0]
        new_age = int(args[1])
    except IndexError: # Catch potential errors if args[1] is missing after split
        print(Fore.YELLOW + f"Не вистачає аргументів. Потрібно: імя кота, та новий вік.")
        return # Exit if no cat found
    except ValueError:
        print(Fore.RED + f"Невірний ageid: '{args[1]}'. вік має бути числом.") 
        return # Exit if no cat found
    
    
    try:
        result = db.cats.update_one({"name": name}, {"$set": {"age": new_age}})
        
        if result.modified_count > 0:
            print(Fore.GREEN + f"Вік кота '{name}' успішно оновлено на {new_age}.")
            updated_cat = db.cats.find_one({"name": name})
            if updated_cat:
                 table = PrettyTable()
                 table.field_names = ["ID", "Name", "Age", "Features"]
                 table.align = "l"
                 table.padding_width = 1
                 features_str = ", ".join(updated_cat.get("features", []))
                 table.add_row([
                     updated_cat.get("_id", "N/A"),
                     updated_cat.get("name", "N/A"),
                     updated_cat.get("age", "N/A"),
                     features_str
                 ])
                 print(table)        
        elif result.matched_count > 0:
            print(Fore.YELLOW + f"Вік кота '{name}' вже {new_age}.")        
        else:
            print(Fore.YELLOW + f"Кіт з ім'ям '{name}' не знайдений.")
            
    except Exception as e:
         # Catch any other potential errors during the database operation
        print(Fore.RED + f"Помилка під час збереження нового віку: {e}")   
        

def add_feature(args, db: MongoClient):
    #додати нову характеристику до списку features кота за ім'ям
    try:
        name = args[0]
        new_feature = " ".join(args[1:])
    except IndexError: # Catch potential errors if args[1] is missing after split
        print(Fore.YELLOW + f"Не вистачає аргументів. Потрібно: імя кота") 
        return # Exit if no cat found
        

    try:
        result = db.cats.update_one({"name": name}, {"$push": {"features": new_feature}})
        if result.modified_count > 0:
            print(Fore.GREEN + f"характеристики кота '{name}' успішно оновлено.")
            updated_cat = db.cats.find_one({"name": name})
            if updated_cat:
                 table = PrettyTable()
                 table.field_names = ["ID", "Name", "Age", "Features"]
                 table.align = "l"
                 table.padding_width = 1
                 features_str = ", ".join(updated_cat.get("features", []))
                 table.add_row([
                     updated_cat.get("_id", "N/A"),
                     updated_cat.get("name", "N/A"),
                     updated_cat.get("age", "N/A"),
                     features_str
                 ])
                 print(table)        
        elif result.matched_count > 0:
            print(Fore.YELLOW + f"характеристика кота '{name}' вже є в списку.")        
        else:
            print(Fore.YELLOW + f"Кіт з ім'ям '{name}' не знайдений.")
    except Exception as e:
         # Catch any other potential errors during the database operation
        print(Fore.RED + f"Помилка під час ддавання нової характеристики: {e}")   


def delete_cat(args, db: MongoClient):
    try:
        name = args[0]
    except IndexError: # Catch potential errors if args[1] is missing after split
        print(Fore.YELLOW + f"Не вистачає аргументів. Потрібно: імя кота.") 
        return # Exit if no cat found
    
    try:
    
        result = db.cats.delete_one({"name": name})

        # Check the deleted_count attribute of the result
        if result.deleted_count > 0:
            print(Fore.GREEN + f"Кіт з ім'ям '{name}' успішно видалений.")
        else:
            # No document matched the filter
            print(Fore.YELLOW + f"Кіт з ім'ям '{name}' не знайдений.")

    except Exception as e:
         # Catch any other potential errors during the database operation
        print(Fore.RED + f"Помилка під час видалення кота: {e}")      


def delete_all_cats(db):
    try:
        result = db.cats.delete_many({})
        # Check the deleted_count attribute of the result
        if result.deleted_count > 0:
            print(Fore.GREEN + f"Кіти успішно видалені.")
        else:
            # No document matched the filter
            print(Fore.YELLOW + f"Кіти не знайдені.")
    except Exception as e:
         # Catch any other potential errors during the database operation
        print(Fore.RED + f"Помилка під час видалення: {e}")  


def add_cat(args, db: MongoClient):
    try:
        name = args[0]
        age = int(args[1])
        features_string = " ".join(args[2:])
        features = [f.strip() for f in features_string.split(',')] # Split by comma and remove whitespace
    except IndexError: # Catch potential errors if args[1] is missing after split
         print(Fore.YELLOW + f"Не вистачає аргументів. Потрібно: імя кота, вік, та список характеристик.")  
         return # Exit if no cat found
    except ValueError:
        print(Fore.RED + f"Невірний ageid: '{args[1]}'. вік має бути числом.") 
        return
         
    try: 
        result = db.cats.insert_one({"name": name, "age": age, "features": features})
        # Provide feedback on success
        print(Fore.GREEN + f"Кіт '{name}' успішно доданий з ID: {result.inserted_id}")
    except Exception as e:
        print(Fore.RED + f"Помилка під час додавання кота: {e}")

    

def main():
    # завантажимо або новый зробимо словник Python для зберігання імен і номерів телефонів. Ім'я буде ключем, а номер телефону – значенням.

    # ініціалізація списку команд-підказок
    command_completer = WordCompleter(['exit', 'close', 'hello', 'help', 'view-all', 'find-cat-info', 'update-age', 
                                       'add-feature', 'delete-cat', 'delete-all-cats', 'add-cat'])
    # вітаємо користувача
    print(Fore.BLUE + "Welcome to the assistant bot!")  

    #виводимо підказку, що наш бот вміє виконувати наступні команди:
    helper() 
    
    db = None
    client = None

    try:
        # Підключення до MongoDB
        print(Fore.CYAN + "Attempting to connect to MongoDB...")
        client = MongoClient(
            "mongodb+srv://iashchukoksana:0GMS4NbU3XREWLvV@cluster0.gckkwgt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000
        )

        # The ismaster command is cheap and does not require auth.
        # It will trigger server selection and raise an error if connection fails.
        client.admin.command('ping')
        print(Fore.GREEN + "Successfully connected to MongoDB!")

        # Get the database object only after successful connection
        db = client.book
    
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(Fore.RED + f"Error connecting to MongoDB: {e}")
        print(Fore.YELLOW + "Please check your connection string, network, and MongoDB Atlas IP access list.")
        sys.exit(1) # Exit the script if connection fails
    except OperationFailure as e:
        print(Fore.RED + f"Authentication error connecting to MongoDB: {e}")
        print(Fore.YELLOW + "Please check your username and password.")
        sys.exit(1) # Exit the script on auth failure
    except Exception as e: # Catch any other unexpected errors during connection setup
        print(Fore.RED + f"An unexpected error occurred during MongoDB connection: {e}")
        sys.exit(1)

    try:
        while True:
            text = prompt("Enter a command: ", completer=command_completer)
           
            command, args = parse_input(text)
            
            if command in ["close", "exit"]:
                print("Good bye!")
                break
            #виводимо підказку, що наш бот вміє виконувати наступні команди:
            elif command == "hello":
                print("How can I help you?")

            elif command == "help":
                helper()

            elif command == "view-all":
                view_all(db)

            elif command == "find-cat-info":
                find_cat_info(args, db) 

            elif command == "update-age":
                update_age(args, db)

            elif command == "add-feature":
                add_feature(args, db) 
                           
            elif command == "delete-cat":
                delete_cat(args, db) 

            elif command == "delete-all-cats":
                delete_all_cats(db)

            elif command == "add-cat":
                add_cat(args, db)  
    except KeyboardInterrupt:
        print("\nExiting on user request.") # Handle Ctrl+C gracefully 
    finally:
        # Ensure the client connection is closed when the loop exits or an error occurs
        if client:
            print(Fore.CYAN + "Closing MongoDB connection.")
            client.close()

if __name__ == "__main__":
    main()