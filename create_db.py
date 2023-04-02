import mysql.connector

# declare your database variables
DBHOST = 'localhost'
DBUSER = 'root'
DBPASS = ''

# establish the connection
connection = mysql.connector.connect(host=DBHOST, user=DBUSER, passwd=DBPASS)

my_cur = connection.cursor()

# execute the SQL script
sql_script = """
DROP DATABASE IF EXISTS academic_advising;
CREATE DATABASE if not exists academic_advising;
USE academic_advising;

CREATE TABLE STUDENT
(
    student_number varchar(10) NOT NULL, # Primary key
    student_email varchar(255) NOT NULL,
    student_password varchar(255) NOT NULL,
    student_name varchar(255) NOT NULL,
    student_contact_no varchar(255) NOT NULL,
    student_program varchar(255) NOT NULL,
    student_year varchar(255) NOT NULL,
    student_concern varchar(255) NOT NULL,

    class_ID INT NOT NULL, # Foreign key

    PRIMARY KEY (student_number)
);

CREATE TABLE ADMIN
(
    admin_number varchar(10) NOT NULL, # Primary key
    admin_email varchar(255) NOT NULL,
    admin_password varchar(255) NOT NULL,
    admin_name varchar(255) NOT NULL,

    PRIMARY KEY (admin_number)

    # isAdmin BOOLEAN NOT NULL
);

CREATE TABLE QUEUE
(
    queue_ID INT NOT NULL AUTO_INCREMENT, # Primary key

    student_number varchar(10) NOT NULL, # Foreign key
    student_name varchar(255) NOT NULL, # Foreign key
    student_year varchar(255) NOT NULL, # Foreign key
    student_program varchar(255) NOT NULL, # Foreign key
    admin_number varchar(10) NOT NULL, # Foreign key
    queue_status varchar(255) NOT NULL,

    PRIMARY KEY (queue_ID),
    FOREIGN KEY (student_number) REFERENCES STUDENT(student_number),
    FOREIGN KEY (student_name) REFERENCES STUDENT(student_name),
    FOREIGN KEY  (student_year) REFERENCES STUDENT(student_year),
    FOREIGN KEY (student_program) REFERENCES STUDENT(student_program),
    FOREIGN KEY (admin_number) REFERENCES ADMIN(admin_number)
);

CREATE TABLE FEEDBACK (
                          feedback_ID INT NOT NULL AUTO_INCREMENT, # Primary key

                          student_number varchar(10) NOT NULL, # Foreign key
                          admin_number varchar(10) NOT NULL, # Foreign key
                          feedback varchar(255) NOT NULL,

                          PRIMARY KEY (feedback_ID),
                          FOREIGN KEY (student_number) REFERENCES STUDENT(student_number),
                          FOREIGN KEY (admin_number) REFERENCES ADMIN(admin_number)
);

CREATE TABLE CLASS
(
    class_ID INT NOT NULL AUTO_INCREMENT, # Primary key
    class_name varchar(255) NOT NULL,
    class_code varchar(255) NOT NULL,
    teacher_name varchar(255) NOT NULL,
    admin_number varchar(10) NOT NULL, # Foreign key

    PRIMARY KEY (class_ID),
    FOREIGN KEY (admin_number) REFERENCES ADMIN(admin_number)
);
"""

my_cur.execute(sql_script, multi=True)

# close the cursor and database connection
my_cur.close()
connection.close()
