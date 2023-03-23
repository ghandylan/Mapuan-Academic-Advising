from flask import Flask, render_template, request, url_for, redirect, jsonify
from sqlalchemy import create_engine
import mariadb

engine = create_engine('mysql+pymysql://root:@localhost:3306/academic-advising')
app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/testme')
def test():
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM student")
        for row in result:
            print(row)
            return jsonify(row)




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])  # index.html
def login():
    # cur = conn.cursor
    if request.method == 'POST':
        if request.form['email'] == 'admin' and request.form['password'] == 'admin':
            return redirect(url_for('admin'))
        elif request.form['email'] == 'student' and request.form['password'] == 'student':
            return redirect(url_for('student'))
        else:
            return redirect(url_for('login'))
    return render_template('index.html')


# if
# app.run(debug=True)
