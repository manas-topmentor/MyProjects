# STEP 1:

# CREATE DATABASE

CREATE DATABASE UniversityDB;
USE UniversityDB;

# STEP 2:

# CREATE SAMPLE TABLES

# 1. DEPARTMENTS:

CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentName VARCHAR(100) NOT NULL
);

# 2. STUDENTS:

CREATE TABLE Students (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    DepartmentID INT,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

# 3. COURSES:

CREATE TABLE Courses (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    CourseName VARCHAR(100) NOT NULL,
    StudentID INT,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);

# STEP 3 INSERTING VALUES IN TABLES:

# 1. DEPARTMENTS:

INSERT INTO Departments (DepartmentName) VALUES
('Computer Science'),
('BHM'),
('BSC'),
("Bcom"),
("BA");

# 2. STUDENTS: 

INSERT INTO Students (Name, Age, DepartmentID) VALUES
('Avishek Das', 26, 2),
('Deepak Singh', 26, 2),
('Dishan Maniar', 26,4),
('Sunny Jalan', 26, 1),
('Alice Johnson', 26, 2),
('Bidesh Banerjee', 21, 3),
('Aditya Vikram Sharma', 22, 5),
('Manas Banerjee', 28, 1),
('Aditya Gupta', 25, 4);

# 3. COURSES:

INSERT INTO Courses (CourseName, StudentID) VALUES
('Food Production',1),
('Food & Beverage Service',1),
('Front Office Operations',null),
('Housekeeping',null),
('Physics',2),
('Chemistry',2),
('Mathematics',null),
('Life Sciences',null),
('English', 3),
('Modern Indian Language',3),
('History', null),
('Political Science', null),
('Artificial Intelligence', 4),
('Operating Systems', 4),
('Database Management',null),
('Data Structures', null),
('Financial Accounting', 5),
('Business Economics (Micro & Macro)',5),
('Business Mathematics',null), 
('StatisticsBusiness Communication',null);

# STEP 4: QUERIES:

# 1. Retrieve all student details along with their department names:

SELECT Stu.StudentID, Stu.Name, Stu.Age, Dep.DepartmentName 
FROM Students Stu
JOIN Departments Dep ON Stu.DepartmentID = Dep.DepartmentID;

# 2. Find the names of all students who are enrolled in 'Artificial Intelligence':

SELECT Stu.Name FROM 
Students Stu JOIN Courses Co 
ON Stu.StudentID = Co.StudentID 
WHERE Co.CourseName = 'Artificial Intelligence';

# 3. Count how many students are in each department:

SELECT Dep.DepartmentName,COUNT(Stu.StudentID) AS NoOfStudents 
FROM Departments Dep
JOIN Students Stu ON Dep.DepartmentID = Stu.DepartmentID 
GROUP BY Dep.DepartmentName;


# 4. List the courses taken by 'Alice Johnson:

SELECT Co.CourseName FROM Courses Co 
JOIN Students Stu ON Co.StudentID = Stu.StudentID 
WHERE Stu.Name = 'Alice Johnson';


# 5. Find students who are enrolled in more than one course.

SELECT Stu.Name, COUNT(Co.CourseID) AS NoOfCourse 
FROM Students Stu
JOIN Courses CO ON Stu.StudentID = Co.StudentID 
GROUP BY Stu.StudentID 
HAVING NoOfCourse > 1;


# 6. Get the average age of students in each department:

SELECT Dep.DepartmentName, AVG(Stu.Age) AS AverageAge 
FROM Departments Dep
JOIN Students Stu ON Dep.DepartmentID = Stu.DepartmentID 
GROUP BY Dep.DepartmentName;


# 7. Find the department with the most students:

SELECT Dep.DepartmentName FROM Departments Dep
JOIN Students Stu ON Dep.DepartmentID = Stu.DepartmentID 
GROUP BY Dep.DepartmentName 
ORDER BY COUNT(Stu.StudentID) DESC 
LIMIT 1;


# 8. List all students who are NOT enrolled in any course.

SELECT Stu.Name FROM Students Stu
LEFT JOIN Courses Co ON Stu.StudentID = Co.StudentID 
WHERE Co.StudentID IS NULL;


# 9. Retrieve students along with the total number of courses they are enrolled in.

SELECT Stu.Name, COUNT(Co.CourseID) AS NoOfCourses 
FROM Students Stu
JOIN Courses Co ON Stu.StudentID = Co.StudentID 
GROUP BY Stu.StudentID;


# 10. Find students who belong to 'Computer Science' and are taking a course with 'Data' in its name:

SELECT Stu.Name FROM Students Stu 
JOIN Departments Dep ON Stu.DepartmentID = Dep.DepartmentID 
JOIN Courses Co ON Stu.StudentID = Co.StudentID 
WHERE Dep.DepartmentName = 'Computer Science' 
AND Co.CourseName LIKE '%Data%';




