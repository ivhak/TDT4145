CREATE DATABASE IF NOT EXISTS WorkoutProgram;

USE WorkoutProgram;

CREATE TABLE IF NOT EXISTS Workout (
    WorkoutID INT NOT NULL AUTO_INCREMENT,
    WorkoutDate DATETIME DEFAULT NOW(),
    Duration INT,
    Performance VARCHAR(255),
    Shape VARCHAR(255),
    PRIMARY KEY (WorkoutID)
);

CREATE TABLE IF NOT EXISTS Excercise (
    ExcerciseID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255),
    PRIMARY KEY (ExcerciseID)
);

CREATE TABLE IF NOT EXISTS Device (
    DeviceID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(255),
    Description VARCHAR(255),
    PRIMARY KEY (DeviceID)
);

CREATE TABLE IF NOT EXISTS ExcerciseDevice (
    ExcerciseID INT NOT NULL,
    DeviceID INT NOT NULL,
    Weight INT,
    Repetitions INT,
    PRIMARY KEY (ExcerciseID),
    FOREIGN KEY (ExcerciseID)
        REFERENCES Excercise(ExcerciseID)
        ON DELETE CASCADE,
    FOREIGN KEY (DeviceID)
        REFERENCES Device(DeviceID)
);

CREATE TABLE IF NOT EXISTS ExcerciseFree (
    ExcerciseID INT NOT NULL,
    Description VARCHAR(255),
    PRIMARY KEY (ExcerciseID),
    FOREIGN KEY (ExcerciseID)
        REFERENCES Excercise(ExcerciseID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ExcerciseInWorkout (
    WorkoutID INT NOT NULL,
    ExcerciseID INT NOT NULL,
    PRIMARY KEY (WorkoutID, ExcerciseID),
    FOREIGN KEY (WorkoutID)
        REFERENCES Workout(WorkoutID)
        ON DELETE CASCADE,
    FOREIGN KEY (ExcerciseID)
        REFERENCES Excercise(ExcerciseID)
);

CREATE TABLE IF NOT EXISTS ExcerciseNote (
    WorkoutID INT NOT NULL,
    Goal TEXT,
    Reflection TEXT,
    PRIMARY KEY (WorkoutID),
    FOREIGN KEY (WorkoutID)
        REFERENCES Workout(WorkoutID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ExcerciseGroup (
    GroupID INT NOT NULL AUTO_INCREMENT,
    GroupName VARCHAR(255),
    PRIMARY KEY (GroupID)
);

CREATE TABLE IF NOT EXISTS ExcerciseInGroup (
    GroupID INT NOT NULL,
    ExcerciseID INT NOT NULL,
    PRIMARY KEY (GroupID, ExcerciseID),
    FOREIGN KEY (GroupID)
        REFERENCES ExcerciseGroup(GroupID)
        ON DELETE CASCADE,
    FOREIGN KEY (ExcerciseID)
        REFERENCES Excercise(ExcerciseID)
        ON DELETE CASCADE
);

