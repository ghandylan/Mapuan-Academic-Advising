from flask import Flask 
from flask_mysqldb import MySQL 

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'academic-advising'

mysql = MySQL(app)

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT 1''')
        result = cur.fetchone()
        cur.close()
        if result[0] == 1:
            return 'Successfully connected to MySQL database!'
        else:
            return 'Failed to connect to MySQL database!'
    except Exception as e:
        return f'Error connecting to MySQL database: {str(e)}'
index()

@app.route('/login', methods=['GET', 'POST'])
def login