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

    # Add exercises to the workout
    exc = input('Would you like to add some exercises?[Y/N]: ')
    while(exc == 'Y' or exc == 'y'):
        os.system('clear')
        ex_id = insert_exercise(db, wo_id)
        group = input('Would you like to add the exercise to a group?[Y/N]: ')
        if (group == 'Y' or group == 'y'):
            add_exercise_to_group(db, ex_id)
        exc = input('Add another exercise?[Y/N]: ')

    # Add a note to the workout
    note = input('Would you like to add a note?[Y/N]: ')
    if (note == 'Y' or note == 'y'):
        os.system('clear')
        insert_note(db, wo_id)


# Link a workout with an exercise
def insert_exerciseinworkout(db, ex_id: int, wo_id: int):
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExerciseInWorkout (WorkoutID, ExerciseID)" +
                   "VALUES ({},{});".format(wo_id, ex_id))
    db.commit()


# Insert a note belonging to a workout with ID wo_id
def insert_note(db, wo_id: int):
    cursor = db.cursor()
    goal = input('Goal of the workout:\n')
    print()
    refl = input('Reflections:\n')
    cursor.execute("INSERT INTO ExerciseNote (WorkoutID, Goal, Reflection)" +
                   "VALUES ({}, '{}', '{}');".format(wo_id, goal, refl))
    db.commit()


# Insert an exercise
def insert_exercise(db, wo_id: int):
    ex_type = input('Exercise with device [D] or without [W]?: ')
    name = input('Name of exercise: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO Exercise(Name) VALUES ('{}');".format(name))
    ex_id = cursor.lastrowid
    if (ex_type == 'D' or ex_type == 'd'):
        insert_exerciseondevice(db, ex_id)
    else:
        insert_exercisefree(db, ex_id)
    insert_exerciseinworkout(db, ex_id, wo_id)
    return ex_id


# Insert an exercise performed on a device
def insert_exerciseondevice(db, ex_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Device;")
    rows = cursor.fetchall()
    dev_ids = []
    sel_dev_id = 0
    if (rows is not None):
        print('Device:')

        # Print all registered devices
        for (dev_id, dev_name, _) in rows:
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
                  "ExerciseDevice" +
                  "(ExerciseID, DeviceID, Weight, Repetitions) " +
                  "VALUES ({},{},{},{});".format(ex_id,
                                                 sel_dev_id,
                                                 weight,
                                                 reps))
        db.commit()


# Insert an exercise not performed on a device
def insert_exercisefree(db, ex_id: int):
    desc = input('Description: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExerciseFree(ExerciseID, Description) " +
                   "VALUES ({},'{}');".format(ex_id, desc))
    db.commit()


# Add an exercise to a group. The user is prompted with existing groups, and
# is given a choice to use a registered group. If the user chooses to use a
# previously registered group, or gives a new group the same name as an already
# registered group, the exercise is added to the given group.
def add_exercise_to_group(db, ex_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ExerciseGroup;")
    rows = cursor.fetchall()
    groups = {}
    print('Groups:')
    for (group_id, group_name) in rows:
        groups[group_name] = group_id
        print('ID: {}, Name: {}'.format(group_id, group_name))

    sel_group_id = input('Select an ID, or 0 to create a new group: ')
    sel_group_id = h.int_parse(sel_group_id, 0)

    if (sel_group_id == 0):
        group_name = input('Name of the group: ')
        if (group_name in groups.keys()):
            print('The group {} already exists, '.format(group_name) +
                  'your exercise will be added to the existing group')
            sel_group_id = groups[group_name]
        else:
            cursor = db.cursor()
            cursor.execute("INSERT INTO ExerciseGroup (GroupName) " +
                           "VALUES ('{}')".format(group_name))
            sel_group_id = cursor.lastrowid
            db.commit()

    cursor.execute("INSERT INTO ExerciseInGroup (GroupID, ExerciseID) " +
                   "VALUES ({}, {})".format(sel_group_id, ex_id))

    print('Inserted exercise with ' +
          'id {} into the group {}'.format(ex_id, group_name))

    db.commit()


# List all the workouts in the database
def list_workouts(db):
    count = input(
        'How many of the last workouts would you like to see (default 5)?: ')
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
        exercises = get_exercises(db, id)
        note = get_note(db, id)

        # Print main infor
        minutes = 'minutes' if duration != 1 else 'minute'
        print('{:%d %b %y %H:%M}'.format(date))
        print()
        print(Fore.BLUE + 'Duration:   ', '{} {}'.format(duration, minutes))
        print(Fore.BLUE + 'Shape:      ', shape)
        print(Fore.BLUE + 'Performance:', performance)

        # Print exercises if there are any
        if (len(exercises) > 0):
            print()
            print(Fore.GREEN + 'exercises:')
            for i in range(len(exercises)):
                if (i < len(exercises)-1):
                    print('├───', exercises[i])
                else:
                    print('└───', exercises[i])

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


# Get all the exercises belonging to a workout with ID wo_id
def get_exercises(db, wo_id: int) -> list:
    exercises = []
    cursor = db.cursor()
    cursor.execute("SELECT Exercise.Name " +
                   "FROM Workout " +
                   "NATURAL JOIN ExerciseInWorkout " +
                   "NATURAL JOIN Exercise " +
                   "WHERE WorkoutID = {};".format(wo_id))
    rows = cursor.fetchall()
    for row, in rows:
        exercises += [row]
    return exercises


# Get the note belonging to the workout with ID wo_id.  Returns the goal text
# and the reflection text if the note exists, otherwise None.
def get_note(db, wo_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * " +
                   "FROM ExerciseNote " +
                   "WHERE WorkoutID = {};".format(wo_id))
    row = cursor.fetchone()
    if (row is not None):
        (_, goal, refl) = row
        return (goal, refl)
    return None


# Delete a workout from the database.
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


# Get all devices, sorted by most used ascending.
def show_devices(db):
    cursor = db.cursor()
    cursor.execute("SELECT Device.Name, COUNT(Device.DeviceID) AS Uses " +
                   "FROM ExerciseDevice NATURAL JOIN Device " +
                   "GROUP BY DeviceID " +
                   "ORDER BY Uses DESC")
    rows = cursor.fetchall()
    print('Most used devices: ')
    for (device_name, uses) in rows:
        times = 'time' if uses == 1 else 'times'
        print("├── {}, used {} {}".format(device_name, uses, times))


# Show all groups of exercises, then show all exercises in a given group
def show_groups(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ExerciseGroup;")
    rows = cursor.fetchall()
    print(Fore.RED + 'Groups:')
    group_ids = {}
    for (group_id, group_name) in rows:
        group_ids[group_id] = group_name
        print('├── ID: {}, Name: '.format(group_id) +
              Fore.BLUE + '{}'.format(group_name))
    print()
    sel_group_id = input('Select an ID to show exercises in the given group: ')
    sel_group_id = h.int_parse(sel_group_id, 0)

    if (sel_group_id in group_ids.keys()):
        cursor = db.cursor()
        cursor.execute("SELECT Exercise.Name " +
                       "FROM ExerciseGroup " +
                       "NATURAL JOIN ExerciseInGroup " +
                       "NATURAL JOIN Exercise " +
                       "WHERE " +
                       "ExerciseGroup.GroupID = {}".format(sel_group_id))

        print()
        rows = cursor.fetchall()
        print('Exercises in group ' + Fore.BLUE +
              group_ids[sel_group_id] + ':')
        for ex_name, in rows:
            print('├── ' + Fore.GREEN + ex_name)


# ------------------------------
#             MENU
# ------------------------------
def chooseAction(db):
    options = {
        0: 'Exit',
        1: 'Show workouts',
        2: 'Insert a workout',
        3: 'Delete a workout',
        4: 'Show most used devices',
        5: 'Show exercise groups'
    }

    actions = {
        1: list_workouts,
        2: insert_workout,
        3: delete_workout,
        4: show_devices,
        5: show_groups
    }

    for (index, option) in options.items():
        print('{}: {}'.format(index, option))

    print('-'*h.terminal_width())
    action = input('Select an action: ')
    action = h.int_parse(action, -1)
    print()
    if(action not in [-1, 0]):
        # Execute the chosen method
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
    pwd = getpass.getpass(' MySQL Password: ')
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
