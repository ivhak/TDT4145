CREATE DATABASE IF NOT EXISTS WorkoutProgram;

USE WorkoutProgram;

CREATE TABLE IF NOT EXISTS Workout (
    WorkoutID       INT NOT NULL AUTO_INCREMENT,
    WorkoutDate     DATETIME DEFAULT NOW(),
    Duration        INT,
    Performance     VARCHAR(255),
    Shape           VARCHAR(255),
    PRIMARY KEY (WorkoutID)
);

CREATE TABLE IF NOT EXISTS Exercise (
    ExerciseID      INT NOT NULL AUTO_INCREMENT,
    Name            VARCHAR(255),
    PRIMARY KEY (ExerciseID)
);

CREATE TABLE IF NOT EXISTS Device (
    DeviceID        INT NOT NULL AUTO_INCREMENT,
    Name            VARCHAR(255),
    Description     VARCHAR(255),
    PRIMARY KEY (DeviceID)
);

CREATE TABLE IF NOT EXISTS ExerciseDevice (
    ExerciseID      INT NOT NULL,
    DeviceID        INT NOT NULL,
    Weight          INT,
    Repetitions     INT,
    PRIMARY KEY (ExerciseID),
    FOREIGN KEY (ExerciseID)
        REFERENCES Exercise(ExerciseID)
        ON DELETE CASCADE,
    FOREIGN KEY (DeviceID)
        REFERENCES Device(DeviceID)
);

CREATE TABLE IF NOT EXISTS ExerciseFree (
    ExerciseID      INT NOT NULL,
    Description     VARCHAR(255),
    PRIMARY KEY (ExerciseID),
    FOREIGN KEY (ExerciseID)
        REFERENCES Exercise(ExerciseID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ExerciseInWorkout (
    WorkoutID       INT NOT NULL,
    ExerciseID      INT NOT NULL,
    PRIMARY KEY (WorkoutID, ExerciseID),
    FOREIGN KEY (WorkoutID)
        REFERENCES Workout(WorkoutID)
        ON DELETE CASCADE,
    FOREIGN KEY (ExerciseID)
        REFERENCES Exercise(ExerciseID)
);

CREATE TABLE IF NOT EXISTS ExerciseNote (
    WorkoutID       INT NOT NULL,
    Goal            TEXT,
    Reflection      TEXT,
    PRIMARY KEY (WorkoutID),
    FOREIGN KEY (WorkoutID)
        REFERENCES Workout(WorkoutID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ExerciseGroup (
    GroupID         INT NOT NULL AUTO_INCREMENT,
    GroupName       VARCHAR(255),
    PRIMARY KEY (GroupID)
);

CREATE TABLE IF NOT EXISTS ExerciseInGroup (
    GroupID         INT NOT NULL,
    ExerciseID      INT NOT NULL,
    PRIMARY KEY (GroupID, ExerciseID),
    FOREIGN KEY (GroupID)
        REFERENCES ExerciseGroup(GroupID)
        ON DELETE CASCADE,
    FOREIGN KEY (ExerciseID)
        REFERENCES Exercise(ExerciseID)
        ON DELETE CASCADE
);

