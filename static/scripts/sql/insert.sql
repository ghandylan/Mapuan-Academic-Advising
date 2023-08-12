# INSERT INTO student(student_number, student_email, student_password, student_name, student_contact_no, student_program,
#                     student_year, student_concern, student_additional_comment, queue_order, queue_status)
# VALUES ( REMOVE THIS AND PUT YOUR OWN VALUES HERE );


INSERT INTO admin(admin_number, admin_email, admin_password, admin_name, available, zoom_link, status)
VALUES ( '0001', 'dylan@gg.com', 'sheesh', 'Dylan Louis Tayag', 0, 'zoom.com', '');
SET @admin_id = LAST_INSERT_ID();
INSERT INTO queue(admin_id, queue_status)
VALUES (@admin_id, 'Available');
