--Таблиця users:

--id: Первинний ключ, автоінкремент (тип SERIAL),
--fullname: Повне ім'я користувача (тип VARCHAR(100)),
--email: Електронна адреса користувача, яка повинна бути унікальною (тип VARCHAR(100))

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Таблиця status:
--id: Первинний ключ, автоінкремент (тип SERIAL),
--name: Назва статусу (тип VARCHAR(50)), повинна бути унікальною. Пропонуємо наступні типи [('new',), ('in progress',), ('completed',)]
DROP TABLE IF EXISTS status;
CREATE TABLE status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    CHECK (name IN ('new', 'in progress', 'completed'))
);
INSERT INTO status (name) VALUES ('new'), ('in progress'), ('completed');


-- Table: tasks:
--id: Первинний ключ, автоінкремент (тип SERIAL),
--title: Назва завдання (тип VARCHAR(100)),
--description: Опис завдання (тип TEXT),
--status_id: Зовнішній ключ, що вказує на id у таблиці status (тип INTEGER),
--user_id: Зовнішній ключ, що вказує на id у таблиці users (тип INTEGER)
DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES status (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE
);
