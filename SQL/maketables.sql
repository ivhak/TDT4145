CREATE TABLE IF NOT EXISTS Workout (
    WorkoutID INT AUTO_INCREMENT NOT NULL,
    WorkoutDate DATE,
    Duration INT,
    Performance VARCHAR(255),
    Shape VARCHAR(255),
    PRIMARY KEY (WorkoutID)
);

CREATE TABLE IF NOT EXISTS Excercise (
    ExcerciseID INT AUTO_INCREMENT NOT NULL,
    Name VARCHAR(255),
    PRIMARY KEY (ExcerciseID)
);

CREATE TABLE IF NOT EXISTS Device (
    DeviceID INT AUTO_INCREMENT NOT NULL,
    Name VARCHAR(255),
    Description VARHCAR(255),
    PRIMARY KEY (DeviceID)
);

CREATE TABLE IF NOT EXISTS ExcerciseDevice (
    ExcersiseID INT NOT NULL,
    DeviceID INT NOT NULL,
    Weight INT,
    Repetitions INT,
    PRIMARY KEY (ExcerciseID),
    FOREIGN KEY (ExcersiseID) REFERENCES (Excercise.ExcerciseID),
    FOREIGN KEY (DeviceID) REFERENCES (Device.DeviceID)
);

CREATE TABLE IF NOT EXISTS ExcerciseFree (
    ExcerciseID INT NOT NULL,
    Description VARCHAR(255),
    PRIMARY KEY (ExcerciseID),
    FOREIGN KEY (ExcerciseID) REFERENCES (Excercise.ExcerciseID)
);

CREATE TABLE IF NOT EXISTS ExcerciseInWorkout (
    WorkoutID INT NOT NULL,
    ExcerciseID INT NOT NULL,
    PRIMARY KEY (WorkoutID, ExcerciseID),
    FOREIGN KEY (WorkoutID) REFERENCES (Workout.WorkoutID),
    FOREIGN KEY (ExcerciseID) REFERENCES (Excercise.ExcerciseID)
)

CREATE TABLE IF NOT EXISTS ExcerciseNote (
    WorkoutID INT NOT NULL,
    Goal VARCHAR(255),
    Reflection VARCHAr(255),
    PRIMARY KEY (WorkoutID),
    FOREIGN KEY (WorkoutID) REFERENCES (Workout.WorkoutID)
);

CREATE TABLE IF NOT EXISTS ExcerciseGroup (
    GroupID INT AUTO_INCREMENT NOT NULL,
    GroupName VARCHAR(255),
    PRIMARY KEY (GroupID)
);

CREATE TABLE IF NOT EXISTS ExcerciseInGroup (
    GroupID INT NOT NULL,
    ExcerciseID INT NOT NULL,
    PRIMARY KEY (GroupID, ExcerciseID),
    FOREIGN KEY (GroupID) REFERENCES (ExcerciseGroup.GroupID),
    FOREIGN KEY (ExcerciseID) REFERENCES (Excercise.ExcerciseID)
);

