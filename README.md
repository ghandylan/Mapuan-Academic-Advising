# Revolutionizing Academic Advising: Mapúan Queue System with SMS Integration
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
### What
The Mapua Academic Advising is a web-based live queueing application built using Flask and MariaDB dedicated to resolve enrollment concerns of currently enrolled Mapuan students. This includes scheduling concerns, missing requirements, document requests, grade changes, section changes, and more. This is a proposed solution to Mapua's current academic advising during the University's enrolment period. It aims to assist professors and students by incorporating a streamlined and unified queue system to avoid the hassle of opening multiple websites at once. 

### Why
During the enrollment period, it came to our attention that the academic advising process at the University was not being handled effectively, as it relied on Google Sheets as a means for students to queue up for concerns regarding their enrollment. This resulted in some students missing their appointments with their professors and, as a consequence, left concerns unresolved in a timely manner. Mapúan Academic Advising provides professors with an easy-to-use platform for managing student queues, while students can view their queue status in real-time and receive SMS notifications when it's their turn. By providing a more efficient and organized system for academic advising, the application aims to help students and professors save time and focus on more important tasks.



### Pre-requisites
- Python 3.10 or higher (https://www.python.org/downloads/)
- XAMPP (https://www.apachefriends.org/download.html)
- Twilio / Vonage account for SMS integration (https://www.twilio.com/) (https://www.vonage.com/communications-apis/sms/)
- requirements.txt
- IDE of your choice (VSCode, PyCharm, IntelliJ, etc.)
- Database Manager (MySQL Workbench, DBeaver, Datagrip, etc.)

### Setup
1. Clone the repository https://github.com/ghandylan/Mapuan-Academic-Advising/archive/refs/heads/master.zip
2. Install the required packages using the command `pip install -r requirements.txt`
3. Open XAMPP and run MySQL
4. Open your database manager and create a schema named `mapua` in MySQL
5. Run the create.sql and insert.sql files in your database manager
6. Edit the config in main.py to match your database credentials
7. Run the application using the command `python main.py`

### Contributors
This project was made possible through the collaborative effort of the following individuals:

Caberto, Drizzle Joy V. (Documentation)\
Delfin, Ivan Zacharia L. (Frontend Development)\
Inocencio, Zara Naomi S. (Frontend Development)\
Lara, Charlene Grazielle E. (Documentation)\
Tayag, Dylan Louis S. (Backend Development)\
\
***Each contributor played a crucial role in the development of the Mapúan Academic Advising system, bringing their unique skills and expertise to the project.***
