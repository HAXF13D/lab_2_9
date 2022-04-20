#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
from datetime import datetime
import psycopg2

DB_PATH = "./data.db"


def create_db():
    con = psycopg2.connect(dbname=DB_PATH)
    cur = con.cursor()

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS types(
            type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_type TEXT NOT NULL
        )
        '''
    )

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS departures(
            departure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number INTEGER NOT NULL,
            destination TEXT NOT NULL,
            type_id INTEGER NOT NULL,
            time DATE,
            FOREIGN KEY(type_id) REFERENCES types(type_id)
        )
        '''
    )
    con.commit()
    con.close()


def select_all():
    pass
    conn = psycopg2.connect(dbname=DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            departures.train_number, 
            types.train_type, 
            departures.destination,
            departures.time
        FROM departures
        INNER JOIN types ON types.type_id = departures.type_id
        """
    )
    rows = cursor.fetchall()
    conn.commit()
    conn.close()

    return [
        {
            'destination': row[2],
            'number': row[0],
            'train_type': row[1],
            'time': datetime.strptime(row[3], '%H:%M'),
        }
        for row in rows
    ]


def add():
    destination = input("Название пункта назначения? ")
    number = int(input("Номер поезда? "))
    time = input("Время отправления ЧЧ:ММ? ")
    train_type = input("Тип поезд? ")
    time = datetime.strptime(time, '%H:%M')

    conn = psycopg2.connect(dbname=DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT type_id FROM types WHERE train_type = ?
        """,
        (train_type,)
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO types (train_type) VALUES (?)
            """,
            (train_type,)
        )
        type_id = cursor.lastrowid
    else:
        type_id = row[0]

    cursor.execute(
        """
        INSERT INTO departures (train_number, destination, type_id, time)
        VALUES (?, ?, ?, ?)
        """,
        (number, destination, type_id, time.strftime("%H:%M"))
    )

    conn.commit()
    conn.close()


def select(command):
    count = 0
    parts = command.split(' ', maxsplit=1)
    time = datetime.strptime(parts[1], '%H:%M')

    conn = psycopg2.connect(dbname=DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            departures.train_number, 
            types.train_type, 
            departures.destination,
            departures.time
        FROM departures
        INNER JOIN types ON types.type_id = departures.type_id
        WHERE departures.time > ?
        """,
        (time.strftime("%H:%M"),)
    )
    rows = cursor.fetchall()
    conn.close()

    trains = [
        {
            'destination': row[2],
            'number': row[0],
            'train_type': row[1],
            'time': datetime.strptime(row[3], '%H:%M'),
        }
        for row in rows
    ]

    if len(trains) == 0:
        print("Отправлений позже этого времени нет.")
    else:
        print_list(trains)


def main():
    create_db()
    while True:
        command = get_command()
        if command == 'exit':
            break

        elif command == 'add':
            add()

        elif command == 'list':
            print_list(select_all())

        elif command.startswith('select'):
            select(command)

        elif command == 'help':
            print_help()

        else:
            print(f"Неизвестная команда {command}", file=sys.stderr)


def get_command():
    return input(">>> ").lower()


def print_list(trains):
    line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
        '-' * 4,
        '-' * 28,
        '-' * 14,
        '-' * 14,
        '-' * 19
    )
    print(line)
    print(
        '| {:^4} | {:^28} | {:^14} | {:^14} | {:^19} |'.format(
            "No",
            "Название пункта назначения",
            "Номер поезда",
            "Тип поезда",
            "Время отправления"
        )
    )
    print(line)
    for idx, train in enumerate(trains, 1):
        print(
            '| {:>4} | {:<28} | {:^14} | {:<14} | {:>19} |'.format(
                idx,
                train.get('destination', ''),
                train.get('number', ''),
                train.get('train_type', ''),
                train.get('time', 0).strftime("%H:%M")
            )
        )
    print(line)


def print_help():
    print("Список команд:\n")
    print("add - добавить отправление;")
    print("list - вывести список отправлений;")
    print("select <ЧЧ:ММ> - вывод на экран информации о "
          "поездах, отправляющихся после этого времени;")
    print("help - отобразить справку;")
    print("exit - завершить работу с программой.")


if __name__ == '__main__':
    main()
