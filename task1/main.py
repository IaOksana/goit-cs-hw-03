import psycopg2

from colorama import Fore, Style
from prettytable import PrettyTable
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


'''decorator'''
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(Fore.BLUE + f"Error {e}.")
            return #(f"Error {e}.")

        except IndexError as e:
            print(Fore.GREEN + f"Error {e}.")
            return# (f"Error {e}.")

        except ValueError as e:
            print(Fore.RED + f"Error {e}.")
            return #(f"Error {e}.")

    return inner


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


@input_error
def get_person_tasks(args : list[str], cur):
    # "Отримати всі завдання певного користувача. Використайте SELECT для отримання завдань конкретного користувача за його user_id."])
    if len(args) < 1:
        raise ValueError("Please enter 1 argument: |user_id|")
    
    try:
        user_id = int(args[0]) # Ensure user_id is an integer
    except ValueError:
        # Handle cases where the input is not a valid number
        raise ValueError(f"Невірний user_id: '{args[0]}'. ID має бути числом.")

    sql_query = """
        SELECT t.id, t.title, t.description, s.name as status
        FROM tasks t
        JOIN status s ON t.status_id = s.id
        WHERE t.user_id = %s;
    """
    try:
        cur.execute(sql_query, (user_id,)) # Pass user_id as a tuple
        tasks = cur.fetchall()

        if not tasks:
            print( Fore.YELLOW + f"Не знайдено завдань для користувача з ID {user_id}.")
            return
            

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Task ID", "Title", "Description", "Status"]
        table.align = "l" # Align left
        table.max_width["Description"] = 100 # Limit description width

        for task in tasks:
            table.add_row(task)
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 30
        table.align["Description"] = "l"
        table.padding_width = 1
        table.max_width["Description"] = 30
        table.align["Status"] = "l"
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred


@input_error
def get_tasks_status(args : list[str], cur) -> str:
    # "Вибрати завдання за певним статусом. Використайте підзапит для вибору завдань з конкретним статусом, наприклад, 'new'."])
    
    if len(args) < 1:
        raise ValueError("Please enter 1 argument: |status name|. має бути new / in progress / completed.")
    
    try:
       status_name = " ".join(args[0:]).lower()  # Ensure status is a text
    except ValueError:
        # Handle cases where the input is not a valid number
        raise ValueError(f"Невірний status name: '{args[0]}'. має бути new / in progress / completed.")

    # sql_query = """
    #     SELECT t.id, t.title, t.description, u.fullname as name, s.name as status
    #     FROM tasks t
    #     JOIN users u ON t.user_id = u.id
    #     JOIN status s ON t.status_id = s.id
    #     WHERE s.name = %s;
    # """

    sql_query = """
        SELECT t.id, t.title, t.description, u.fullname as name, s.name as status
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        JOIN status s ON t.status_id = s.id
        WHERE t.status_id IN (SELECT id FROM status WHERE name = %s)
        """
    try:
        cur.execute(sql_query, (status_name,)) # Pass user_id as a tuple
        tasks = cur.fetchall()

        if len(tasks) == 0:
            return Fore.YELLOW + f"Не знайдено завдань з статусом {status_name}."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Task ID", "Title", "Description", "Name", "Status"]
        table.align = "l" # Align left

        for task in tasks:
            table.add_row(task)
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 30
        table.align["Description"] = "l"
        table.padding_width = 1
        table.max_width["Description"] = 30
        table.align["Name"] = "l"
        table.max_width["Name"] = 30
        table.align["Status"] = "l"
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred


@input_error
def update_status(args : list[str], cur) -> str:
    #"Оновити статус конкретного завдання. Змініть статус конкретного завдання на 'in progress' або інший статус."]
    if len(args) < 2:
        raise ValueError("Please enter 2 arguments: |task_id| |status name| - має бути new / in progress / completed.")
    
    try:
        task_id = int(args[0]) # Ensure user_id is an integer
        status_name = " ".join(args[1:]).lower()  
    except ValueError:
        # Handle cases where the input is not a valid number
        raise ValueError(f"Невірний task_id: '{args[0]}'. ID має бути числом.")

    sql_query = """
        SELECT s.id 
        FROM status s 
        WHERE s.name = %s;
    """
    try:
        cur.execute(sql_query, (status_name,)) # Pass user_id as a tuple
        status = cur.fetchone()

        if not status:
            return Fore.YELLOW + f"Не знайдено статус  {status_name}."
        
        sql_query = """
            UPDATE tasks
            SET status_id = %s
            WHERE id = %s;
        """
        cur.execute(sql_query, (status[0], task_id)) # Pass user_id as a tuple
        
        return("Status updated successfully!")
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred


@input_error
def get_users_without_tasks(args : list[str], cur) -> str:
    # "Отримати список користувачів, які не мають жодного завдання. Використайте комбінацію SELECT, WHERE NOT IN і підзапит."])

    sql_query = """
        SELECT id, fullname, email
        FROM users
        WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks WHERE user_id IS NOT NULL);
    """

    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        users = cur.fetchall()

        if not users:
            return Fore.YELLOW + f"Не знайдено користувачів без завдань."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = [" ID", "Full Name", "Email"]
        table.align = "l" # Align left

        for user in users:
            table.add_row(user)
        table.align["User ID"] = "l"
        table.align["Full Name"] = "l"
        table.align["Email"] = "l"
        table.padding_width = 1
        table.max_width["Email"] = 30        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """
    

@input_error
def add_task(args : list[str], cur) -> str:
    # Додати нове завдання для конкретного користувача. Використайте INSERT для додавання нового завдання."])
    # Expecting: user_id, title, description (status defaults to 'new')
    if len(args) < 3:
        raise ValueError("Будь ласка, вкажіть user_id, title, та description. Приклад: add-task 5 'New Task Title' 'Description of the task'")

    try:
        user_id = int(args[0])
        title = args[1]
        # Join the rest of the arguments in case the description has spaces
        description = " ".join(args[2:])
    except ValueError:
        raise ValueError(f"Невірний user_id: '{args[0]}'. ID має бути числом.")
    except IndexError: # Catch potential errors if args[1] or args[2:] are missing after split
         raise ValueError("Не вистачає аргументів. Потрібно: user_id, title, description.")

    # --- 1. Get the ID for the default status 'new' ---
    sql_get_status_id = """
        SELECT id FROM status WHERE name = 'new';
    """
    new_status_id = None
    try:
        cur.execute(sql_get_status_id)
        status_result = cur.fetchone() # Fetch one row

        if not status_result:
            # This should ideally not happen if your DB is set up correctly
            return Fore.RED + "Помилка: Статус 'new' не знайдено в базі даних."
        else:
            new_status_id = status_result[0] # Get the id from the tuple

    except psycopg2.Error as e:
        print(Fore.RED + f"Помилка бази даних при пошуку статусу 'new': {e}")
        return None # Indicate an error

    # --- 2. Check if user_id exists ---
    sql_check_user = "SELECT id FROM users WHERE id = %s;"
    try:
        cur.execute(sql_check_user, (user_id,))
        if not cur.fetchone():
            return Fore.YELLOW + f"Користувача з ID {user_id} не існує."
    except psycopg2.Error as e:
        print(Fore.RED + f"Помилка бази даних при перевірці користувача: {e}")
        return None

    # --- 3. Execute the INSERT query ---
    sql_insert_task = """
        INSERT INTO tasks (title, description, status_id, user_id)
        VALUES (%s, %s, %s, %s);
    """
    try:
        # Pass the arguments in the correct order for the INSERT statement
        cur.execute(sql_insert_task, (title, description, new_status_id, user_id))

        # Commit is handled by autocommit=True or the 'with' block exit
        return Fore.GREEN + f"Завдання '{title}' успішно додано для користувача ID {user_id}."

    except psycopg2.Error as e:
        # Handle potential database errors during the insert
        print(Fore.RED + f"Помилка бази даних при додаванні завдання: {e}")
        return None # Indicate an error

@input_error
def get_tasks_not_completed(args : list[str], cur) -> str:
    #  Отримати всі завдання, які ще не завершено. Виберіть завдання, чий статус не є 'завершено'."])
    sql_query = """
        SELECT id, title, description, status_id, user_id
        FROM tasks
        WHERE status_id NOT IN (SELECT id FROM status WHERE name = 'completed');
    """

    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        tasks = cur.fetchall()

        if not tasks:
            return Fore.YELLOW + f"Не знайдено не завершених завдань."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Task ID", "Title", "Description", "Status ID", "User ID"]
        table.align = "l" # Align left

        for task in tasks:
            table.add_row(task)
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 30
        table.align["Description"] = "l"
        table.padding_width = 1
        table.max_width["Description"] = 30
        table.align["Status ID"] = "l"
        table.align["User ID"] = "l"
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """

@input_error
def delete_task(args : list[str], cur) -> str:
    # "Видалити конкретне завдання. Використайте DELETE для видалення завдання за його id."])
    if len(args) < 1:
        # Provide a clear error message about expected arguments
        raise ValueError("Будь ласка, вкажіть task id")

    try:
        task_id = int(args[0])
    except ValueError:
        raise ValueError(f"Невірний task_id: '{args[0]}'. ID має бути числом.")

    sql_delete_task = """
        DELETE FROM tasks 
        WHERE id = %s;
    """
    try:
        # Pass the arguments in the correct order for the INSERT statement
        cur.execute(sql_delete_task, (task_id,))

        # Check how many rows were affected
        if cur.rowcount > 0:
            # If rowcount is greater than 0, a row was deleted
            # Commit is handled by autocommit=True or the 'with' block exit
            return Fore.GREEN + f"Завдання {task_id} успішно видалено."
        else:
            # If rowcount is 0, no row matched the WHERE clause (task_id not found)
            return Fore.YELLOW + f"Завдання з ID {task_id} не знайдено."

    except psycopg2.Error as e:
        # Handle potential database errors during the insert
        print(Fore.RED + f"Помилка бази даних при додаванні завдання: {e}")
        return None # Indicate an error

@input_error
def find_users_by_email(args : list[str], cur) -> str:
    # найти користувачів з певною електронною поштою. 
    # Використайте SELECT із умовою LIKE для фільтрації за електронною поштою."])
    if len(args) < 1:
        raise ValueError("Будь ласка, вкажіть email.")
    
    email = args[0]
    email_pattern = f"%{email}%"
         
    sql_query = """
        SELECT id, fullname, email
        FROM users
        WHERE email LIKE %s;
    """

    try:
        cur.execute(sql_query, (email_pattern,)) # Pass user_id as a tuple
        users = cur.fetchall()

        if not users:
            return Fore.YELLOW + f"Не знайдено користувачів з електронною поштою {email} ."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["User ID", "FullName", "Email"]
        table.align = "l" # Align left

        for user in users:
            table.add_row(user)
        table.align["User ID"] = "l"
        table.align["FullName"] = "l"
        table.align["email"] = "l"
        table.padding_width = 1
        table.max_width["email"] = 30
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """

@input_error
def update_name(args : list[str], cur) -> str:
    # Оновити ім'я користувача. Змініть ім'я користувача за допомогою UPDATE."])
    if len(args) < 2:
        raise ValueError("Будь ласка, вкажіть ID та нове ім'я користувача.")
    
    try:
        user_id = int(args[0])
        new_name = " ".join(args[1:])
    except ValueError:
        raise ValueError(f"Невірний user_id: '{args[0]}'. ID має бути числом.")
    except IndexError: # Catch potential errors if args[1] is missing after split
         raise ValueError("Не вистачає аргументів. Потрібно: user_id, new_name.")
         
    sql_query = """
        UPDATE users
        SET fullname = %s
        WHERE id = %s;
    """

    try:
        cur.execute(sql_query, (new_name, user_id,)) # Pass user_id as a tuple

        if cur.rowcount > 0:
            # If rowcount is greater than 0, a row was deleted
            # Commit is handled by autocommit=True or the 'with' block exit
            return Fore.GREEN + f"Користувача з ID {user_id} успішно змінено."
        else:
            # If rowcount is 0, no row matched the WHERE clause (task_id not found)
            return Fore.YELLOW + f"Користувача з ID {user_id} не знайдено."
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """
    

@input_error
def get_tasks_count_by_status(args : list[str], cur) -> str:
    # Отримати кількість завдань для кожного статусу. 
    # Використайте SELECT, COUNT, GROUP BY для групування завдань за статусами.t"])
    
    sql_query = """
        SELECT s.name AS status_name, COUNT(t.id) AS task_count
        FROM status s
        LEFT JOIN tasks t ON s.id = t.status_id
        GROUP BY s.name;
    """

    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        statuses = cur.fetchall()

        if not statuses:
            return Fore.YELLOW + f"Не знайдено завдань."
        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Status", "Number of tasks"]
        table.align = "l" # Align left

        for status in statuses:
            table.add_row(status)
        table.align["Status"] = "l"
        table.align["Number of tasks"] = "l"
        table.padding_width = 1    
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """        
        

@input_error
def get_tasks_by_email_domain(args : list[str], cur) -> str:
    # Отримати завдання, які призначені користувачам з певною доменною частиною електронної пошти. 
    # Використайте SELECT з умовою LIKE в поєднанні з JOIN, щоб вибрати завдання, призначені користувачам, 
    # чия електронна пошта містить певний домен (наприклад, '%@example.com')"])
    if len(args) < 1:
        raise ValueError("Будь ласка, вкажіть шаблон домену email (наприклад, %@example.com або %gmail%).")

    # The user provides the pattern directly, including '%' wildcards
    email_pattern = args[0]

    sql_query = """
        SELECT t.id, t.title, t.description, u.fullname AS user_name, u.email
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        WHERE u.email LIKE %s;
    """
    try:
        cur.execute(sql_query, (email_pattern,)) # Pass the pattern as a parameter
        tasks = cur.fetchall()

        if not tasks:
            return Fore.YELLOW + f"Не знайдено завдань для користувачів з email, що відповідає шаблону '{email_pattern}'."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Task ID", "Title", "Description", "User Name", "User Email"]
        table.align = "l" # Align left
        for task in tasks:
            table.add_row(task)
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 30
        table.align["Description"] = "l"
        table.max_width["Description"] = 30
        table.align["User Name"] = "l"
        table.align["User Email"] = "l"
        table.max_width["User Email"] = 30
        table.padding_width = 1
        print(table)

    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань за доменом email: {e}")
        return None # Indicate an error occurred

@input_error
def get_tasks_without_description(args : list[str], cur) -> str:
    # Отримати список завдань, що не мають опису. Виберіть завдання, у яких відсутній опис."])
    sql_query = """
        SELECT id, title, description, status_id, user_id
        FROM tasks
        WHERE description IS NULL OR description = '';
    """

    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        tasks = cur.fetchall()

        if not tasks:
            return Fore.YELLOW + f"Не знайдено не завершених завдань."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Task ID", "Title", "Description", "Status ID", "User ID"]
        table.align = "l" # Align left

        for task in tasks:
            table.add_row(task)
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 30
        table.align["Description"] = "l"
        table.padding_width = 1
        table.max_width["Description"] = 30
        table.align["Status ID"] = "l"
        table.align["User ID"] = "l"
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred    """

@input_error
def get_tasks_in_progress_for_users(args : list[str], cur) -> str:
    # Вибрати користувачів та їхні завдання, які є у статусі 'in progress'. 
    # Використайте INNER JOIN для отримання списку користувачів та їхніх завдань із певним статусо
    sql_query = """
        SELECT u.id, u.fullname AS user_name, u.email, t.id, t.title, t.description, s.name AS status_name
        FROM users u
        INNER JOIN tasks t ON u.id = t.user_id
        INNER JOIN status s ON t.status_id = s.id
        WHERE s.name = 'in progress';
    """

    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        users = cur.fetchall()

        if not users:
            return Fore.YELLOW + f"Не знайдено."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["USer ID", "Full Name", "Email", "Task ID", "Title", "Description", "Status"]
        table.align = "l" # Align left

        for user in users:
            table.add_row(user)
        table.align["User ID"] = "l"
        table.align["Full Name"] = "l"
        table.align["Email"] = "l"
        table.max_width["Email"] = 30
        table.align["Task ID"] = "l"
        table.align["Title"] = "l"
        table.max_width["Title"] = 20
        table.align["Description"] = "l"
        table.padding_width = 1
        table.max_width["Description"] = 20
        table.align["Status"] = "l"
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred  
    

@input_error
def get_users_and_task_count(args : list[str], cur) -> str:
    # Отримати користувачів та кількість їхніх завдань. 
    # Використайте LEFT JOIN та GROUP BY для вибору користувачів та підрахунку їхніх завдань.
    sql_query = """
        SELECT u.fullname AS name, COUNT(t.id) AS task_count
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        GROUP BY u.fullname;
    """
    try:
        cur.execute(sql_query) # Pass user_id as a tuple
        users = cur.fetchall()

        if not users:
            return Fore.YELLOW + f"Не знайдено."

        # Create a table to display the results
        table = PrettyTable()
        table.field_names = ["Full Name", "Count"]
        table.align = "l" # Align left

        for user in users:
            table.add_row(user)
        table.align["Full Name"] = "l"
        table.align["Count"] = "l"
        table.padding_width = 1
        
        print(table)
    
    except psycopg2.Error as e:
        # Handle potential database errors during query execution
        print(Fore.RED + f"Помилка бази даних при отриманні завдань: {e}")
        return None # Indicate an error occurred  
    
def helper():
    #створюємо таблицю - Запити для виконання:
    help_data = [
        ["get-person-tasks", "Отримати всі завдання певного користувача. (за user_id)"],
        ["get-tasks-status", "Вибрати завдання за певним статусом. (наприклад, 'new')"],
        ["update-status", "Оновити статус конкретного завдання. (на 'in progress' тощо)"],
        ["get-users-without-tasks", "Отримати користувачів без жодного завдання."],
        ["add-task", "Додати нове завдання для користувача."],
        ["get-tasks-not-completed", "Отримати всі незавершені завдання."],
        ["delete-task", "Видалити конкретне завдання. (за id)"],
        ["find-users-by-email", "Знайти користувачів за шаблоном email. (LIKE)"],
        ["update-name", "Оновити ім'я користувача."],
        ["get-tasks-count-by-status", "Отримати кількість завдань для кожного статусу."],
        ["get-tasks-by-email-domain", "Отримати завдання за доменом email користувача."],
        ["get-tasks-without-description", "Отримати завдання без опису."],
        ["get-tasks-in-progress-for-users", "Вибрати користувачів та їхні завдання у статусі 'in progress'."],
        ["get-users-and-task-count", "Отримати користувачів та кількість їхніх завдань."],
        ["help", "Вивести цей список команд."],
        ["exit / close", "Завершити роботу."],
        ["hello", "Привітатися з ботом."]
    ]

    table_help = PrettyTable()
    table_help.field_names = ["Command", "Description"]
    table_help.add_rows(help_data)

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
    table_help.max_width["Description"] = 80

    # Print the formatted table
    print(table_help)
    

def main() :
    # завантажимо або новый зробимо словник Python для зберігання імен і номерів телефонів. Ім'я буде ключем, а номер телефону – значенням.

    # ініціалізація списку команд-підказок
    command_completer = WordCompleter(['exit', 'close', 'hello', 'help', 'get-person-tasks', 'get-tasks-status', 'update-status', 'get-users-without-tasks', 'add-task', 'get-tasks-not-completed', 'delete-task', 'find-users-by-email', 'update-name', 'get-tasks-count-by-status', 'get-tasks-by-email-domain', 'get-tasks-without-description', 'get-tasks-in-progress-for-users', 'get-users-and-task-count'])

    # вітаємо користувача
    print(Fore.BLUE + "Welcome to the assistant bot!")  

    #виводимо підказку, що наш бот вміє виконувати наступні команди:
    helper() 

    con = None  # Initialize conn to None
    try:
        # Connect to the PostgreSQL server
        with psycopg2.connect(
            host="localhost",
            database="task_1",
            port='5433',
            user="postgres",
            password="postgres",
        ) as con:
            con.autocommit = True

            cur = con.cursor() 

            while True:
                text = prompt("Enter a command: ", completer=command_completer)
                table = PrettyTable()
                
                command, args = parse_input(text)

                if command in ["close", "exit"]:
                    print("Good bye!")
                    break
                #виводимо підказку, що наш бот вміє виконувати наступні команди:
                elif command == "hello":
                    print("How can I help you?")

                elif command == "help":
                    helper()

                elif command == "get-person-tasks":
                    get_person_tasks(args, cur)

                elif command == "get-tasks-status":
                    res = get_tasks_status(args, cur)
                    if res:
                        print(res)

                elif command == "update-status":
                    res = update_status(args, cur)
                    if res:
                        print(res)
                        con.commit()

                elif command == "get-users-without-tasks":
                    res = get_users_without_tasks(args, cur)
                    if res:
                        print(res)                        

                elif command == "add-task":
                    res = add_task(args, cur)
                    if res:
                        print(res)
                        con.commit()
                        
                elif command == "get-tasks-not-completed":
                    res = get_tasks_not_completed(args, cur)
                    if res:
                        print(res)

                elif command == "delete-task":
                    res = delete_task(args, cur)
                    if res:
                        print(res)
                        con.commit()
                        
                elif command == "find-users-by-email":
                    res = find_users_by_email(args, cur)
                    if res:
                        print(res)

                elif command == "update-name":
                    res = update_name(args, cur)
                    if res:
                        print(res)
                        con.commit()

                elif command == "get-tasks-count-by-status":
                    res = get_tasks_count_by_status(args, cur)
                    if res:
                        print(res)
                        
                elif command == "get-tasks-by-email-domain":
                    res = get_tasks_by_email_domain(args, cur)
                    if res:
                        print(res)

                elif command == "get-tasks-without-description":
                    res = get_tasks_without_description(args, cur)
                    if res:
                        print(res)

                elif command == "get-tasks-in-progress-for-users":
                    res = get_tasks_in_progress_for_users(args, cur)
                    if res:
                        print(res)

                elif command == "get-users-and-task-count":
                    res = get_users_and_task_count(args, cur)
                    if res:
                        print(res)
                

    finally:
        if con:
            con.close()


if __name__ == "__main__":
    main()
