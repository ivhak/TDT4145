#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector
import getpass
import sys
import os
import helper as h
from colorama import Fore, init
init(autoreset=True)


# Execute an SQL-script
def execute_script(db, filename):
    cursor = db.cursor()
    with open(filename, 'r') as f:
        sqlFile = f.read()
        f.close()

        sqlCommands = sqlFile.split(';')

        for command in sqlCommands:
            try:
                cursor.execute(command)
            except Exception:
                pass


# Insert a new workout in the database
def insert_workout(db):
    cursor = db.cursor()

    duration = input("Duration (minutes): ")
    duration = h.int_parse(duration)

    accepted = ['A', 'B', 'C', 'D', 'E', 'F']

    # Get user input of performance. If something else than a
    # letter grade is submitted, it defaults to a C
    performance = input("Performance (letter grade A-F): ")
    performance = h.str_parse(performance, accepted, 'C')

    # Get user input of shape. If something else than a
    # letter grade is submitted, it defaults to a C
    shape = input("Shape (letter grade A-F): ")
    shape = h.str_parse(shape, accepted, 'C')

    query = ("INSERT INTO Workout(Duration, Performance, Shape) " +
             "VALUES ({},'{}','{}');".format(duration, performance, shape))
    try:
        cursor.execute(query)
    except Exception:
        pass

    wo_id = cursor.lastrowid
    db.commit()

    # Add excercises to the workout
    exc = input('Would you like to add som exercises?[Y/N]: ')
    while(exc == 'Y' or exc == 'y'):
        os.system('clear')
        insert_excercise(db, wo_id)
        exc = input('Another one?[Y/N]: ')

    # Add a note to the workout
    note = input('Would you like to add a note?[Y/N]: ')
    if (note == 'Y' or note == 'y'):
        os.system('clear')
        insert_note(db, wo_id)


# Link a workout with an excercise
def insert_excerciseinworkout(db, exc_id: int, wo_id: int):
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExcerciseInWorkout (WorkoutID, ExcerciseID)" +
                   "VALUES ({},{});".format(wo_id, exc_id))
    db.commit()


# Insert a note belonging to a workout with ID wo_id
def insert_note(db, wo_id: int):
    cursor = db.cursor()
    goal = input('Goal of the workout:\n')
    print()
    refl = input('Reflections:\n')
    cursor.execute("INSERT INTO ExcerciseNote (WorkoutID, Goal, Reflection)" +
                   "VALUES ({}, '{}', '{}');".format(wo_id, goal, refl))
    db.commit()


# Insert an excercise
def insert_excercise(db, wo_id: int):
    exc_type = input('Excercise with device [D] or without [W]?: ')
    name = input('Name of excercise: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO Excercise(Name) VALUES ('{}');".format(name))
    exc_id = cursor.lastrowid
    if (exc_type == 'D' or exc_type == 'd'):
        insert_excerciseondevice(db, exc_id)
    else:
        insert_excercisefree(db, exc_id)
    insert_excerciseinworkout(db, exc_id, wo_id)


# Insert an excercise performed on a device
def insert_excerciseondevice(db, exc_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Device;")
    dev_ids = []
    rows = cursor.fetchall()
    sel_dev_id = 0
    if (rows is not None):
        print('Device:')

        # Print all registered devices
        for (dev_id, dev_name, _) in cursor:
            dev_ids += [dev_id]
            print('  ID: {}, Name: {}'.format(dev_id, dev_name))

        sel_dev_id = input('Select an ID, or press 0 to add a new one: ')
        # If sel_dev_id is not a number, default to 0
        sel_dev_id = h.int_parse(sel_dev_id)

    # Add a new device if the user sumbits 0 or an invalid ID.
    if (sel_dev_id == 0 or sel_dev_id not in dev_ids):
        new_dev_name = input('Name of device: ')
        nwq_dev_desc = input('Description of device: ')
        d = db.cursor()
        d.execute("INSERT INTO Device(Name, Description)" +
                  "VALUES ('{}', '{}');".format(new_dev_name, nwq_dev_desc))
        sel_dev_id = d.lastrowid
        db.commit()
        dev_ids += [sel_dev_id]

    if (sel_dev_id in dev_ids):
        weight = input('Weight (kg): ')
        # If weights is not a number, default to 0
        weight = h.int_parse(weight)

        reps = input('Repetitions: ')
        # If reps is not a number, default to 0
        reps = h.int_parse(reps)

        e = db.cursor()
        e.execute("INSERT INTO " +
                  "ExcerciseDevice" +
                  "(ExcerciseID, DeviceID, Weight, Repetitions) " +
                  "VALUES ({},{},{},{});".format(exc_id,
                                                 sel_dev_id,
                                                 weight,
                                                 reps))
        db.commit()


# Insert an excercise not performed on a device
def insert_excercisefree(db, exc_id: int):
    desc = input('Description: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExcerciseFree(ExcerciseID, Description) " +
                   "VALUES ({},'{}');".format(exc_id, desc))
    db.commit()


# List all the workouts in the database
def list_workouts(db):
    count = input('How many of the last workouts would you like to see?: ')
    count = h.int_parse(count, 5)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Workout " +
                   "ORDER BY WorkoutDate DESC " +
                   "LIMIT {};".format(count))
    rows = cursor.fetchall()

    print(Fore.RED + 'Workouts:')
    print('-'*h.terminal_width())

    # Loop through the workouts
    for (id, date, duration, performance, shape) in rows:
        excercises = get_excercises(db, id)
        note = get_note(db, id)

        # Print main infor
        minutes = 'minutes' if duration != 1 else 'minute'
        print('{:%d %b %y %H:%M}'.format(date))
        print()
        print(Fore.BLUE + 'Duration:   ', '{} {}'.format(duration, minutes))
        print(Fore.BLUE + 'Shape:      ', shape)
        print(Fore.BLUE + 'Performance:', performance)

        # Print excercises if there are any
        if (len(excercises) > 0):
            print()
            print(Fore.GREEN + 'Excercises:')
            for i in range(len(excercises)):
                if (i < len(excercises)-1):
                    print('├───', excercises[i])
                else:
                    print('└───', excercises[i])

        # Print the note if it exists
        if (note is not None):
            goal = note[0]
            refl = note[1]
            print()
            print(Fore.YELLOW + 'Note:')
            print('├─── Goal: ')
            print(h.wrap_indent(goal, 5, '│'))
            print('│')
            print('└─── Reflection:')
            print(h.wrap_indent(refl, 5))
        print('-'*h.terminal_width())
    print()


# Get all the excercises belonging to a workout with ID wo_id
def get_excercises(db, wo_id: int) -> list:
    excercises = []
    cursor = db.cursor()
    cursor.execute("SELECT Excercise.Name " +
                   "FROM Workout " +
                   "NATURAL JOIN ExcerciseInWorkout " +
                   "NATURAL JOIN Excercise " +
                   "WHERE WorkoutID = {};".format(wo_id))
    rows = cursor.fetchall()
    for row, in rows:
        excercises += [row]
    return excercises


# Get the note belonging to the workout with ID wo_id.
# Returns the goal text and the reflection text if the note exists,
# otherwise None
def get_note(db, wo_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * " +
                   "FROM ExcerciseNote " +
                   "WHERE WorkoutID = {};".format(wo_id))
    row = cursor.fetchone()
    if (row is not None):
        (_, goal, refl) = row
        return (goal, refl)
    return None


# Delete a workout from the database
def delete_workout(db):
    cursor = db.cursor()
    query = "SELECT * FROM Workout;"
    cursor.execute(query)
    print('-'*h.terminal_width())
    print('Which workout would you like to delete?')
    ids = []
    rows = cursor.fetchall()
    for(wid, date, _, _, _) in rows:
        ids += [wid]
        print('ID {}: {:%d %b %y %H:%M}'.format(wid, date))

    print()
    deleteId = input('Select an ID: ')
    deleteId = h.int_parse(deleteId, -1)
    if (deleteId in ids):
        print()
        conf = input('Are you sure [Y/N]: ')
        if (conf == 'Y' or conf == 'y'):
            d = db.cursor()
            d.execute('DELETE FROM Workout ' +
                      'WHERE WorkoutID = {};'.format(deleteId))
            db.commit()
            print('Deleted workout with ID {}'.format(deleteId))


# ------------------------------
#             MENU
# ------------------------------
def chooseAction(db):
    options = {
        0: 'Exit',
        1: 'Show workouts',
        2: 'Insert a workout',
        3: 'Delete a workout'
    }

    actions = {
        1: list_workouts,
        2: insert_workout,
        3: delete_workout
    }

    for (index, option) in options.items():
        print('{}: {}'.format(index, option))

    print('-'*h.terminal_width())
    action = input('Select an action: ')
    print()
    try:
        action = int(action)
    except Exception:
        action = -1
    if(action not in [-1, 0]):
        actions[action](db)
    return action


# ------------------------------
#             MAIN
# ------------------------------
def main():
    os.system('clear')
    print(Fore.BLUE + """
                     Welcome to your Workout Journal!
                     --------------------------------

 This program requires that you have a MySQL server running on your machine.
 Log in using your username and password for the server. Make sure the server
 is running.

 This program is designed to be a journal where you can log your workouts.

    """)
    username = input(' MySQL Username: ')
    pwd = getpass.getpass(' MySql Password: ')
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user=username,
            passwd=pwd,
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.errors.ProgrammingError:

        print(" Something went wrong, exiting ...")
        sys.exit()

    os.system('clear')

    execute_script(mydb, 'SQL/maketables.sql')
    mydb.cursor().execute('USE WorkoutProgram;')

    a = 1
    while a != 0:
        a = chooseAction(mydb)
        if(a != 0 and a != -1):
            input('Press Enter to continue...')
        os.system('clear')


if __name__ == '__main__':
    main()
