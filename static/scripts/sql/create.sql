DROP DATABASE IF EXISTS academic_advising;
CREATE DATABASE if not exists academic_advising;
USE academic_advising;



CREATE TABLE ADMIN
(
    admin_id       INT          NOT NULL AUTO_INCREMENT, # Primary key
    admin_number   varchar(10)  NOT NULL,
    admin_email    varchar(255) NOT NULL,
    admin_password varchar(255) NOT NULL,
    admin_name     varchar(255) NOT NULL,
    available      boolean      NOT NULL,
    zoom_link      varchar(255) NOT NULL,
    status         varchar(255) NOT NULL,
    is_admin       boolean      NOT NULL DEFAULT TRUE,

    PRIMARY KEY (admin_id)
    # isAdmin BOOLEAN NOT NULL
);

CREATE TABLE QUEUE
(
    queue_ID     INT          NOT NULL AUTO_INCREMENT, # Primary key

    admin_id     INT          NOT NULL,                # Foreign key
    queue_status varchar(255) NOT NULL,

    PRIMARY KEY (queue_ID),
    FOREIGN KEY (admin_id) REFERENCES ADMIN (admin_id)
);



CREATE TABLE STUDENT
(
    student_number             varchar(10)  NOT NULL, # Primary key
    student_email              varchar(255) NOT NULL,
    student_password           varchar(255) NOT NULL,
    student_name               varchar(255) NOT NULL,
    student_contact_no         varchar(255) NOT NULL,
    student_program            varchar(255) NOT NULL,
    student_year               varchar(255) NOT NULL,
    student_concern            varchar(255),
    student_additional_comment varchar(255),
    queue_order                INT,
    queue_status               varchar(255),
    is_admin                   boolean      NOT NULL DEFAULT FALSE,
    sms_sent                   boolean      NOT NULL DEFAULT FALSE,

    queue_ID                   INT,                   # Foreign key

    FOREIGN KEY (queue_ID) REFERENCES QUEUE (queue_ID),
    PRIMARY KEY (student_number)
);


CREATE TABLE FEEDBACK
(
    feedback_ID    INT          NOT NULL AUTO_INCREMENT, # Primary key

    student_number varchar(10)  NOT NULL,                # Foreign key
    admin_id       INT          NOT NULL,                # Primary key
    feedback       varchar(255) NOT NULL,
    rating         varchar(255) NOT NULL,
    date           varchar(255) NOT NULL,

    PRIMARY KEY (feedback_ID),
    FOREIGN KEY (student_number) REFERENCES STUDENT (student_number),
    FOREIGN KEY (admin_id) REFERENCES ADMIN (admin_id)
);
CREATE TABLE CLASS
(
    class_ID     INT          NOT NULL AUTO_INCREMENT, # Primary key
    class_name   varchar(255) NOT NULL,
    class_code   varchar(255) NOT NULL,
    teacher_name varchar(255) NOT NULL,
    admin_id     INT          NOT NULL,                # Primary key

    PRIMARY KEY (class_ID),
    FOREIGN KEY (admin_id) REFERENCES ADMIN (admin_id)
);