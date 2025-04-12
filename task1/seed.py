from datetime import datetime
from datetime import date
import faker
from random import randint, choice
import psycopg2 

NUMBER_STATUSES = 3
NUMBER_TASKS = 80
NUMBER_USERS = 15

def generate_fake_data(number_users, number_tasks) -> tuple:
    fake_users = []
    fake_tasks = []
    fake_data = faker.Faker()

    for _ in range(number_users):
        fake_users.append((fake_data.name(), fake_data.email()))

    for _ in range(number_tasks):
        fake_tasks.append((fake_data.text(max_nb_chars=100), fake_data.text()))

    return fake_users, fake_tasks

def prepare_data(users, tasks) -> tuple:
    for_users = []
    for user in users:
        for_users.append(user)

    for_tasks = []
    for task in tasks:
        for_tasks.append((*task, randint(1, NUMBER_STATUSES), randint(1, NUMBER_USERS)))

    return for_users, for_tasks

def insert_data_to_db(users, tasks) -> None:
    with psycopg2.connect(
        host="localhost",
        database="task_1",
        port='5433',
        user="postgres",
        password="postgres",
    ) as con:
        con.autocommit = True

        cur = con.cursor()

        sql_to_users = """INSERT INTO users(fullname, email)
                               VALUES (%s, %s)"""

        cur.executemany(sql_to_users, users)

        sql_to_tasks = """INSERT INTO tasks(title, description, status_id, user_id)
                               VALUES (%s, %s, %s, %s)"""

        cur.executemany(sql_to_tasks, tasks)

# Фіксуємо наші зміни в БД

        con.commit()

if __name__ == "__main__":
    users, tasks = prepare_data(*generate_fake_data(NUMBER_USERS, NUMBER_TASKS))
    insert_data_to_db(users, tasks)

