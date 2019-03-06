import mysql.connector
import getpass
import os


def show_tables(db):
    mycursor = db.cursor()
    mycursor.execute('SHOW TABLES;')
    for table in mycursor:
        print(table)


def executeScript(db, filename):
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


def insertWorkout(db):
    cursor = db.cursor()
    duration = input("Duration: ")
    performance = input("Performance: ")
    shape = input("Shape: ")
    query = "INSERT INTO Workout(Duration, Performance, Shape) " + \
        "VALUES ({},'{}','{}');".format(duration, performance, shape)
    try:
        cursor.execute(query)
    except Exception:
        pass
    id = cursor.lastrowid
    db.commit()

    exc = input('Would you like to add som exercises?[Y/N]: ')
    while(exc == 'Y' or exc == 'y'):
        os.system('clear')
        insertExcercise(db, id)
        exc = input('Another one?[Y/N]: ')


def insertExcerciseInWorkout(db, eid, wid):
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExcerciseInWorkout (WorkoutID, ExcerciseID)" +
                   "VALUES ({},{})".format(wid, eid))
    db.commit()


def insertExcercise(db, wid):
    excType = input('Excercise with device [D] or without [W]?: ')
    name = input('Name of excercise: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO Excercise(Name) VALUES ('{}')".format(name))
    id = cursor.lastrowid
    if (excType == 'D' or excType == 'd'):
        insertExcerciseOnDevice(db, id)
    else:
        insertExcerciseFree(db, id)
    insertExcerciseInWorkout(db, id, wid)


def insertExcerciseOnDevice(db, id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Device;")
    dids = []
    print('Device:')
    for (did, dname, _) in cursor:
        dids += [did]
        print('  ID: {}, Name: {}'.format(did, dname))
    sid = int(input('Select an ID, or press 0 to add a new one.'))
    if (sid == 0):
        ndname = input('Name of device: ')
        nddesc = input('Description of device: ')
        d = db.cursor()
        d.execute("INSERT INTO Device(Name, Description)" +
                  "VALUES ('{}', '{}')".format(ndname, nddesc))
        sid = d.lastrowid
        db.commit()
        dids += [sid]

    if (sid in dids):
        weight = input('Weight (kg): ')
        reps = input('Repetitions: ')
        e = db.cursor()
        e.execute("INSERT INTO " +
                  "ExcerciseDevice" +
                  "(ExcerciseID, DeviceID, Weight, Repetitions)" +
                  "VALUES ({},{},{},{})".format(id, sid, weight, reps))
        db.commit()


def insertExcerciseFree(db, id):
    desc = input('Description: ')
    cursor = db.cursor()
    cursor.execute("INSERT INTO ExcerciseFree(ExcerciseID, Description) " +
                   "VALUES ({},'{}')".format(id, desc))
    db.commit()


def listWorkouts(db):
    cursor = db.cursor()
    query = "SELECT * FROM Workout;"
    cursor.execute(query)
    print()
    print('Workouts:')
    print('-------------------------')
    rows = cursor.fetchall()
    for (id, date, duration, performance, shape) in rows:
        excercises = getExcercises(db, id)

        minutes = 'minutes' if duration > 1 else 'minute'
        print('{:%d %b %y %H:%M}'.format(date))
        print()
        print('Duration   : {} {}'.format(duration, minutes))
        print('Shape      :', shape)
        print('Performance:', performance)
        if (len(excercises) > 0):
            print('│')
            print('└── Excercises:')
            for i in range(len(excercises)):
                if (i < len(excercises)-1):
                    print('    ├───', excercises[i])
                else:
                    print('    └───', excercises[i])
        print('-------------------------')
    print()


def getExcercises(db, id):
    excercises = []
    cursor = db.cursor()
    cursor.execute("SELECT Excercise.Name " +
                   "FROM Workout " +
                   "NATURAL JOIN ExcerciseInWorkout " +
                   "NATURAL JOIN Excercise " +
                   "WHERE WorkoutID = {}".format(id))
    rows = cursor.fetchall()
    for row, in rows:
        excercises += [row]
    return excercises


def deleteWorkout(db):
    cursor = db.cursor()
    query = "SELECT * FROM Workout;"
    cursor.execute(query)
    print('----------------------------------------')
    print('Which workout would you like to delete?')
    ids = []
    rows = cursor.fetchall()
    for(wid, date, _, _, _) in rows:
        ids += [wid]
        print('ID {}: {:%d %b %y %H:%M}'.format(wid, date))

    deleteId = int(input('Select an ID: '))
    if (deleteId in ids):
        conf = input('Are you sure [Y/N]: ')
        if (conf == 'Y' or conf == 'y'):
            d = db.cursor()
            d.execute('DELETE FROM Workout ' +
                      'WHERE WorkoutID = {}'.format(deleteId))
            db.commit()
            print('Deleted workout with ID {}'.format(deleteId))


def chooseAction(db):
    options = {
        0: 'Exit',
        1: 'Show workouts',
        2: 'Insert a workout',
        3: 'Delete a workout'
    }

    actions = {
        1: listWorkouts,
        2: insertWorkout,
        3: deleteWorkout
    }

    for (index, option) in options.items():
        print('{}: {}'.format(index, option))
    print('-------------------------')
    action = input('Select an action: ')
    try:
        action = int(action)
    except Exception:
        action = -1
    if(action not in [-1, 0]):
        actions[action](db)
    return action


def main():
    os.system('clear')
    print('Welcome to your Workout Journal!')
    username = input('Username: ')
    pwd = getpass.getpass()
    os.system('clear')
    mydb = mysql.connector.connect(
        host='localhost',
        user=username,
        passwd=pwd,
        auth_plugin='mysql_native_password'
    )
    executeScript(mydb, '../SQL/maketables.sql')
    mydb.cursor().execute('USE WorkoutProgram')

    a = 1
    while a != 0:
        a = chooseAction(mydb)
        if(a != 0 and a != -1):
            input('Press Enter to continue...')
        os.system('clear')


if __name__ == '__main__':
    main()
