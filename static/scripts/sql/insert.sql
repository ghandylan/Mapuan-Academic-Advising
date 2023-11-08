INSERT INTO student(student_number, student_email, student_password, student_name, student_contact_no, student_program,
                    student_year, student_concern, student_additional_comment, queue_order, queue_status, sms_sent,
                    role)
VALUES ('800', 'dylan@mapua.com', 'sheesh', 'Dylan Louis Tayag', '09123456789', 'BSIT', '1',
        'I need help with my project',
        'Urgent', 0, '', 0, 'student');


INSERT INTO admin(admin_number, admin_email, admin_password, admin_name, available, zoom_link, status, role)
VALUES ('0001', 'dylan@gg.com', 'sheesh', 'Admin', 0, 'zoom.com', '', 'admin');
SET @admin_id = LAST_INSERT_ID();
INSERT INTO queue(admin_id, queue_status)
VALUES (@admin_id, 'Available');
