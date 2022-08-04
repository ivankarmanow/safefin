# app.py
from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS
import psycopg2
import datetime as dt
import time
import locale
import json
from psycopg2 import DatabaseError
import os


locale.setlocale(category=locale.LC_ALL, locale=('ru_RU', 'UTF-8'))

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources='*')

def check_passwd(user, pwd):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username='" + user + "';")
            if cur.fetchone()[0] == pwd:
                return True
            else:
                return False
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return False
    except Exception as e:
        print(e)
        return False

@app.route('/register/')
def register_handler():
    try:
        with conn.cursor() as cur:
            username = request.args.get('username')
            cur.execute("SELECT username FROM users WHERE username='" + username + "';")
            if cur.fetchone() != None:
                resp = Response("EX")
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
            else:
                cur.execute("INSERT INTO users VALUES ('" + request.args.get('username') + "', '" + request.args.get('pwd') + "');")
                conn.commit()
                resp = Response("OK")
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/login/')
def login_handler():
    try:
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username='" + username + "';")
            pwd_db = cur.fetchone()[0]
        if  pwd_db == pwd:
            resp = Response("OK")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        elif pwd_db == None:
            resp = Response("US")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            resp = Response("PW")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/add_exp/')
def add_exp_handler():
    try:
        username = request.args.get('username')
        title = request.args.get('title')
        category = request.args.get('category')
        summ = request.args.get('sum')
        pwd = request.args.get('pwd')
        if request.args.get('time') == None:
            tim = dt.datetime.now()
        else:
            tim = dt.datetime.fromtimestamp(request.args.get('time'))
        if check_passwd(username, pwd):
            qq = "'" + username + "', '" + title + "', '" + category + "', '" + summ + "', '" + str(tim) + "');"
            with conn.cursor() as cur:
                cur.execute("INSERT INTO test_exps (username, title, category, sum, time) VALUES (" + qq)
                conn.commit()
            resp = "OK"
            return resp
        else:
            cur.close()
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/del_exp')
def del_exp_handler():
    try:
        exp_id = request.args.get('id')
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        if check_passwd(username, pwd):
            with conn.cursor() as cur:
                cur.execute("DELETE FROM test_exps WHERE id=" + exp_id + ";")
                conn.commit()
            resp = Response("OK")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/add_cat/')
def add_cat_handler():
    try:
        cat = request.args.get('category')
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        if check_passwd(username, pwd):
            with conn.cursor() as cur:
                cur.execute("INSERT INTO categories VALUES ('" + cat + "', '" + username + "');")
                conn.commit()
            resp = Response("OK")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/del_cat/')
def del_cat_handler():
    try:
        cat = request.args.get('category')
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        if check_passwd(username, pwd):
            with conn.cursor() as cur:
                cur.execute("DELETE FROM categories WHERE category='" + cat + "' AND username='" + username + "';")
                conn.commit()
            resp = Response("OK")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/allsum/')
def allsum_handler():
    try:
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        tim = dt.datetime.now() - dt.timedelta(days=30)
        if check_passwd(username, pwd):
            with conn.cursor() as cur:
                cur.execute("SELECT SUM(sum) FROM test_exps WHERE username='" + username + "' AND time >= '" + str(tim) + "';")
                allsum = cur.fetchall()[0][0]
                cur.execute("SELECT category, SUM(sum) FROM test_exps WHERE username='" + username + "' AND time >= '" + str(tim) + "' GROUP BY category;")
                fetc = cur.fetchall()
        else:
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        resp = jsonify(
            all=allsum,
            categories=fetc
            )
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/analyze/')
def analyze_handler():
    try:
        username = request.args.get('username')
        cat = request.args.get('category')
        tim = dt.datetime.now() - dt.timedelta(days=30)
        if check_passwd(username, request.args.get('pwd')):
            with conn.cursor() as cur:
                cur.execute("SELECT SUM(sum) FROM test_exps WHERE username='" + username + "' AND time >= '" + str(tim) + "' AND category='" + cat + "';")
                catsum = cur.fetchall()[0][0]
                cur.execute("SELECT title, SUM(sum) FROM test_exps WHERE username='" + username + "' AND time >= '" + str(tim) + "' AND category='"+cat+"' GROUP BY title;")
                fetc = cur.fetchall()
            resp = jsonify(
                cat=catsum,
                titles=fetc
            )
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            resp = Response("AD")
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

class DTEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (dt.date, dt.datetime)):
            return obj.isoformat()

@app.route('/exps/')
def exps_handler():
    try:
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        cat = request.args.get('cat')
        if check_passwd(username, pwd):
            if cat == None:
                with conn.cursor() as cur:
                    cur.execute("SELECT title, category, sum, time, id FROM test_exps WHERE username='" + username + "';")
                    dat = []
                    for i in cur.fetchall():
                        dat.append(list(i))
                    for i in dat:
                        i[3] += dt.timedelta(hours=7)
            else:
                with conn.cursor() as cur:
                    cur.execute("SELECT title, sum, time, id FROM test_exps WHERE username='" + username + "' AND category='" + cat + "';")
                    dat = []
                    for i in cur.fetchall():
                        dat.append(list(i))
                    for i in dat:
                        i[2] += dt.timedelta(hours=7)
            resp = json.dumps(dat, indent=4, cls=DTEncoder, ensure_ascii=False)
            return resp
        else:
            return "AD"
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/cats/')
def cats_handler():
    try:
        username = request.args.get('username')
        pwd = request.args.get('pwd')
        if check_passwd(username, pwd):
            with conn.cursor() as cur:
                cur.execute("SELECT category FROM categories WHERE username='" + username + "';")
                resp = jsonify(cur.fetchall())
            return resp
        else:
            return "AD"
    except DatabaseError as db:
        print(db)
        conn.rollback()
        return "Error!"
    except Exception as e:
        print(e)
        resp = Response("Error!")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/')
def index():
    comms = [
        "/register?username=&pwd=",
        "/login?username=&pwd=",
        "/add_exp?username=&title=&category=&sum=&pwd=",
        "/del_exp?id=&username=&pwd=",
        "/add_cat?category=&username=&pwd=",
        "/del_cat?category=&username=&pwd=",
        "/allsum?username=&pwd=&time=",
        "/analyze?username=&pwd=&time=&category=",
        "/exps?username=&pwd=&cat=",
        "/cats?username=&pwd="
    ]
    return jsonify(comms)

if __name__ == '__main__':
    app.run(threaded=True)