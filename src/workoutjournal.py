#!/usr/bin/python
# -*- coding: utf-8 -*-

from colorama import Fore, Style, init
from datetime import datetime
import helper as h
import time
import os
import sys
import getpass
import mysql.connector
init(autoreset=True)


# Insert a new workout in the database
def insert_workout(db):
    cursor = db.cursor()
    os.system('clear')

    try:
        duration = input("Duration (minutes): ")
        duration = h.int_parse(duration, -1)
        while (duration < 0):
            print('\nInvalid duration, try again...')
            duration = input("Duration (minutes): ")
            duration = h.int_parse(duration, -1)

        # Get user input of performance. While something else than a number
        # between 1 and 10 is submitted, the user is asked again.
        print()
        performance = input("Performance (1-10): ")
        performance = h.int_parse(performance, -1)
        while (performance not in range(1, 11)):
            print('\nInvalid input, try again...')
            performance = input("Performance (1-10): ")
            performance = h.int_parse(performance, -1)

        # Get user input of shape. While something else than a number between 1
        # and 10 is submitted, the user is asked again.
        print()
        shape = input("Shape (1-10): ")
        shape = h.int_parse(shape, -1)
        while (shape not in range(1, 11)):
            print('\nInvalid input, try again...')
            shape = input("Shape (1-10): ")
            shape = h.int_parse(shape, -1)

        # Get user input on the date. Defaults to now.
        print()
        date = input("Date (yyyy-mm-dd [Press Enter for current date]): ")
        if (not date):
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            while(not h.date_parse(date)):
                date = input('Invalid date, try again... : ')
            time = input('Time (hh:mm): ')
            while(not h.time_parse(time)):
                time = input('Invalid time, try again... : ')

            date += ' ' + time + ':00'

    # <Ctrl-C> will terminate the insertion of the workout and take the user
    # back to the menu
    except KeyboardInterrupt:
        print('\nInsertion terminated')
        return

    query = ("INSERT INTO Workout(WorkoutDate, Duration, Performance, Shape) " +
             "VALUES ('{}', {},'{}','{}');".format(date, duration, performance, shape))
    cursor.execute(query)

    wo_id = cursor.lastrowid
    db.commit()

    # Add exercises to the workout
    exc = input('Would you like to add some exercises?[Y/N]: ')
    while(exc == 'Y' or exc == 'y'):
        os.system('clear')
        ex_id = insert_exercise(db, wo_id)
        group = input('Would you like to add the exercise to a group?[Y/N]: ')
        if (group == 'Y' or group == 'y'):
            insert_exercise_in_group(db, ex_id)
        exc = input('Add another exercise?[Y/N]: ')

    # Add a note to the workout
    note = input('Would you like to add a note?[Y/N]: ')
    if (note == 'Y' or note == 'y'):
        os.system('clear')
        insert_note(db, wo_id)


# Insert a note belonging to a workout with ID wo_id
def insert_note(db, wo_id: int):
    cursor = db.cursor()
    os.system('clear')
    goal = input('Goal of the workout:\n')
    print()
    refl = input('Reflections/Thoughts:\n')
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


# Link a workout with an exercise
def insert_exerciseinworkout(db, ex_id: int, wo_id: int):
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExerciseInWorkout (WorkoutID, ExerciseID)" +
                   "VALUES ({},{});".format(wo_id, ex_id))
    db.commit()


# Insert an exercise performed on a device
def insert_exerciseondevice(db, ex_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Device;")
    rows = cursor.fetchall()
    dev_ids = []
    sel_dev_id = 0
    if (len(rows) > 0):
        print('Devices:')

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
def insert_exercise_in_group(db, ex_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ExerciseGroup;")
    rows = cursor.fetchall()
    sel_group_id = 0
    groups = {}
    os.system('clear')
    if (len(rows) > 0):
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
    rows = cursor.fetchall()
    os.system('clear')
    if (len(rows) > 0):
        print('Which workout would you like to delete?')
        print('─'*h.terminal_width())
        ids = []
        for(wid, date, _, _, _) in rows:
            ids += [wid]
            print('ID {}: {:%d %b %y %H:%M}'.format(wid, date))

        print('─'*h.terminal_width())
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
    else:
        print('No workouts logged')


# List all the workouts in the database. The user is prompted for a number of
# workouts it wants to see, or a default of 5.
def list_workouts(db):
    count = input(
        'How many of the last workouts would you like to see? (default 5): ')
    count = h.int_parse(count, 5)

    cursor = db.cursor()
    cursor.execute("SELECT * FROM Workout " +
                   "ORDER BY WorkoutDate DESC " +
                   "LIMIT {};".format(count))
    rows = cursor.fetchall()

    os.system('clear')
    if (len(rows) > 0):
        # Print header
        print(Fore.RED + 'Workouts:')
        print('─'*h.terminal_width())

        # Loop through the workouts
        for (id, date, duration, performance, shape) in rows:
            exercises = get_exercises(db, id)
            note = get_note(db, id)

            # Print main infor
            minutes = 'minutes' if duration != 1 else 'minute'
            print('{:%d %b %y %H:%M}'.format(date))
            print()
            print(Fore.BLUE + 'Duration:   ',
                  '{} {}'.format(duration, minutes))
            print(Fore.BLUE + 'Performance:', performance + '/10')
            print(Fore.BLUE + 'Shape:      ', shape + '/10')

            # Print exercises if there are any, tree style
            if (len(exercises) > 0):
                print()
                print(Fore.GREEN + 'Exercises:')
                for i in range(len(exercises)):
                    if (i < len(exercises)-1):
                        print('├───', exercises[i])
                    else:
                        print('└───', exercises[i])

            # Print the note if it exists, tree style
            if (note is not None):
                goal = note[0]
                refl = note[1]
                print()
                print(Fore.YELLOW + 'Note:')
                print('├─── ' + Style.BRIGHT + 'Goal: ')
                print(h.wrap_indent(goal, 5, '│'))
                print('│')
                print('└─── ' + Style.BRIGHT + 'Reflections/Thoughts:')
                print(h.wrap_indent(refl, 5))
            print('─'*h.terminal_width())
        print()
    else:
        print('No workouts logged.')


# Lists the performance and shape of the workout where an exercise was done, in
# a given time interval.
def list_exercise_results(db):
    # Get all logged exercises
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Exercise;")
    rows = cursor.fetchall()

    ex_ids = []
    sel_ex_id = 0

    if (len(rows) > 0):
        # Print the logged exercises with name and id.
        print("Which exercise would you like to see the results for?")
        for (ex_id, name) in rows:
            ex_ids += [ex_id]
            print('{}: {}'.format(ex_id, name))
        sel_ex_id = h.int_parse(input("ID: "), 0)

        if (ex_id in ex_ids):

            # Start date
            start_date = input("Select start date (yyyy-mm-dd): ")
            while(not h.date_parse(start_date)):
                print("Invalid date. try again...")
                start_date = input("Select start date (yyyy-mm-dd): ")

            # End date
            end_date = input("Select end date (yyyy-mm-dd): ")
            while(not h.date_parse(end_date)):
                print("Invalid date. try again...")
                end_date = input("Select end date (yyyy-mm-dd): ")

            # Get the peformance and shape in the given tim interval
            cursor = db.cursor()
            cursor.execute("SELECT WorkoutDate, Exercise.Name, Performance, Shape " +
                           "FROM Workout NATURAL JOIN Exercise " +
                           "WHERE WorkoutID = {} ".format(sel_ex_id) +
                           "AND CAST('{} 23:59:59' as datetime) >= WorkoutDate ".format(end_date) +
                           "AND CAST('{} 00:00:00' as datetime) <= WorkoutDate;".format(start_date))
            rows = cursor.fetchall()

            (_, name, _, _) = rows[0]
            print('\nResults of workout ' + Fore.GREEN +
                  name + Fore.RESET + ':')
            length = len(rows)
            i = 0

            # Print the results, tree style
            for (date, _, performance, shape) in rows:
                i += 1
                prefix1 = '├──' if i < length else '└──'
                prefix2 = '│' if i < length else ' '
                print(prefix1 + Fore.CYAN + 'Date: ' + Fore.RESET + str(date))
                print(prefix2 + '  ├── ' + Fore.BLUE + 'Performance:' +
                      Fore.RESET + ' {}'.format(performance))
                print(prefix2 + '  └── ' + Fore.YELLOW + 'Shape:' +
                      Fore.RESET + '       {}'.format(performance))
            print()

    else:
        print('No logged exercises')


# Get all devices, sorted by most used descending.
def list_devices(db):
    cursor = db.cursor()
    cursor.execute("SELECT Device.Name, COUNT(Device.DeviceID) AS Uses " +
                   "FROM ExerciseDevice NATURAL JOIN Device " +
                   "GROUP BY DeviceID " +
                   "ORDER BY Uses DESC")
    rows = cursor.fetchall()
    os.system('clear')
    if (len(rows) > 0):
        devices = [(name, uses) for (name, uses) in rows]
        longest = max([len(name) for (name, _) in devices])
        print('Most used devices: ')
        for i in range(len(devices)):
            name = devices[i][0]

            uses = devices[i][1]
            suffix = '' if uses == 1 else 's'

            # Add spaces to align "(used x time(s))"
            spaces = ' '*(longest - len(name))

            prefix = '├──' if i < len(devices) - 1 else '└──'

            print("{} {}: {} {}(used {} time{})".format(
                prefix,
                Fore.YELLOW + str(i+1) + '.' + Fore.RESET,
                Fore.BLUE + name + Fore.RESET,
                spaces, uses, suffix))
    else:
        print('No devices logged')


# Show all groups of exercises, then show all exercises in a given group
def list_groups(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ExerciseGroup;")
    rows = cursor.fetchall()
    os.system('clear')
    if (len(rows) > 0):
        print(Fore.RED + 'Groups:')
        group_ids = {}
        for (group_id, group_name) in rows:
            group_ids[group_id] = group_name
            print('├── ID: {}, Name: '.format(group_id) +
                  Fore.BLUE + '{}'.format(group_name))
        print()
        sel_group_id = input(
            'Select an ID to show exercises in the given group: ')
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
    else:
        print('No groups logged.')


# ------------------------------
#             MENU
# ------------------------------
def choose_action(db):
    menu = [
        'Exit',
        'Show workouts',
        'Insert a workout',
        'Delete a workout',
        'Show most used devices',
        'Show exercise groups',
        'List exercise results'
    ]

    actions = {
        1: list_workouts,
        2: insert_workout,
        3: delete_workout,
        4: list_devices,
        5: list_groups,
        6: list_exercise_results
    }

    h.print_menu(menu)
    print('─'*h.terminal_width())
    action = input('Select an action: ')
    action = h.int_parse(action, -1)
    print()
    if(action in actions.keys()):
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
    try:
        username = input('MySQL Username: ')
        pwd = getpass.getpass('MySQL Password: ')
    except KeyboardInterrupt:
        print('\n Bye!')
        sys.exit(0)

    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user=username,
            passwd=pwd,
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.errors.ProgrammingError:
        print(" Something went wrong, try again")
        time.sleep(0.5)
        main()

    os.system('clear')

    h.execute_script(mydb, 'maketables.sql')
    mydb.cursor().execute('USE WorkoutProgram;')

    a = 1
    while a != 0:
        a = choose_action(mydb)
        if(a != 0 and a != -1):
            input('Press Enter to continue...')
        os.system('clear')


if __name__ == '__main__':
    main()
