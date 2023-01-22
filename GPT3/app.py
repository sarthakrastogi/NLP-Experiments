from flask import *
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_cors import CORS
from flask_login import current_user
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from datetime import datetime
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from celery import Celery
from httplib2 import Http
from json import dumps
import io
import json


DEBUG = True
global dbfilename
dbfilename = 'instance/database23.db'
global EMAILS_TABLE
EMAILS_TABLE = "emails_table"
global JOBDESCS_TABLE
JOBDESCS_TABLE = "jobdescs_table"

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database23.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#source: official flask_login documentation

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(10), nullable=False)
    first_name = db.Column(db.String(10), nullable=False)
    last_name = db.Column(db.String(10), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=14)], render_kw={"placeholder": "Email"})
    first_name = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "First Name"})
    last_name = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Last Name"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=14)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign up')
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(
                'Username already exists!')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=14)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=14)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign in')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                print("logged in as", user.username)
                global username
                username = user.username
                return redirect(url_for('kanbanhome', username=user.username))
    return render_template('signin.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        db.session.add(User(username=form.username.data, first_name=form.first_name.data, last_name=form.last_name.data, password=bcrypt.generate_password_hash(form.password.data)))
        db.session.commit()
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))



def GPT3call(prompt):
    import os
    import openai

    api_key = None#"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"
    openai.api_key = api_key

    if api_key:
        response = openai.Completion.create(
          model="text-curie-001",
          prompt=prompt,
          #temperature=0.5,
          max_tokens=150,
          #top_p=1.0,
          #frequency_penalty=0.0,
          #presence_penalty=0.0
        )
        choices = []
        for choice in a['choices']:
            choices.append(choice['text'])
        response = choices[0]
    else:
        response = "API key missing"
    return response



@app.route('/kanban/<username>')
@login_required
def kanbanhome(username):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()
        cur.execute(f"select * from {EMAILS_TABLE} where username='{username}';")
        taskslist = cur.fetchall()
        cur.execute(f"select * from {JOBDESCS_TABLE} where username='{username}';")
        listslist = cur.fetchall()
        return render_template("main.html")#, status='success', tasksjin=taskslist, listsjin=listslist)


@app.route('/insert_email/<username>', methods=['GET', 'POST'])
@login_required
def insert_email(username):
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        #id = post_data.get('id')
        name = post_data.get('name')
        subject = post_data.get('subject')
        email_prompt = post_data.get('email_prompt')
        task_type = "email"
        with sqlite3.connect(dbfilename) as conn:
            cur = conn.cursor()
            cur.execute(f"select first_name, last_name from user where username='{username}'")
            row = cur.fetchall()
            first_name, last_name = row[0][0], row[0][1]
            print("user's name is", first_name, last_name)

        prompt = "Generate an email to " + name + " from " + first_name + " " + last_name + " with the subject " + subject + ". The email should say that " + email_prompt
        result = GPT3call(prompt)


        print(name, subject, email_prompt, task_type, username, result)

        with sqlite3.connect(dbfilename) as conn:
            print(3)
            cur = conn.cursor()
            cur.execute(f'insert into {EMAILS_TABLE} (name, subject, email_prompt, result, task_type, created_at, username) values ("{name}", "{subject}", "{email_prompt}", "{result}", "{task_type}", CURRENT_TIMESTAMP, "{username}")')
            conn.commit()
            print('email insertion complete')
        response_object['message'] = "Successfully Added"
    return jsonify(response_object)



@app.route('/insert_jobdesc/<username>', methods=['GET', 'POST'])
@login_required
def insert_jobdesc(username):
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        #id = post_data.get('id')
        job_title = post_data.get('job_title')
        job_responsibilities = post_data.get('job_responsibilities')
        job_requirements = post_data.get('job_requirements')
        task_type = "jobdesc"

        prompt = "Generate a job description for the role of " + job_title + " with the job responsibilities including " + job_responsibilities + " and job requirements including " + job_requirements
        result = GPT3call(prompt)

        print(job_title, job_responsibilities, job_requirements, task_type, username, result)

        with sqlite3.connect(dbfilename) as conn:
            print(3)
            cur = conn.cursor()
            cur.execute(f'insert into {JOBDESCS_TABLE} (job_title, job_responsibilities, job_requirements, result, task_type, created_at, username) values ("{job_title}", "{job_responsibilities}", "{job_requirements}", "{result}", "{task_type}", CURRENT_TIMESTAMP, "{username}")')
            conn.commit()
            print('jobdesc insertion complete')
        response_object['message'] = "Successfully Added"
    return jsonify(response_object)



@app.route('/delete_task/<string:type>/<string:id>/<username>', methods=['GET', 'POST'])
@login_required
def delete(id, type, username):
    with sqlite3.connect(dbfilename) as conn:
        print("deleting task with id", id)
        cur = conn.cursor()
        response_object = {'status': 'success'}
        if type == "email": cur.execute(f"delete from {EMAILS_TABLE} where id='{id}'")
        elif type == "jobdesc": cur.execute(f"delete from {JOBDESCS_TABLE} where id='{id}'")
        conn.commit()
        cur.close()
        print("deleted task", id)

    response_object['message'] = "Successfully Deleted"
    return jsonify(response_object)


def export_a_task(type, id):
    with sqlite3.connect(dbfilename) as conn:
        print("exporting task with id", id)
        cur = conn.cursor()
        if type == "email":
            cur.execute(f"select *  from {EMAILS_TABLE} where id='{id}'")
            columns = ['id', 'name', 'subject', 'email_prompt', 'task_type', 'result', 'created_at', 'username']
        elif type == "jobdesc":
            cur.execute(f"select *  from {JOBDESCS_TABLE} where id='{id}'")
            columns = ['id', 'job_title', 'job_responsibilities', 'job_requirements', 'result', 'task_type', 'created_at', 'username']
        row = cur.fetchall()
        print("exported row is ", row)
        df = pd.DataFrame(row, columns=columns)
        df.to_csv(str(row[0][1])+'.csv', index=False)
        conn.commit()
        cur.close()
        print("exported task")



@app.route('/export_task/<string:type>/<string:id>', methods=['GET', 'POST'])
@login_required
def export(type, id):
    export_a_task(type, id)
    response_object = {'status': 'success'}
    response_object['message'] = "Successfully Exported"
    return jsonify(response_object)


@app.route('/fetch/<username>', methods=['GET'])
def fetchkanban(username):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()
        cur.execute(f"select * from {EMAILS_TABLE} where username='{username}';")
        emailslist = cur.fetchall()
        cur.execute(f"select * from {JOBDESCS_TABLE} where username='{username}';")
        jobdescslist = cur.fetchall()
    result = jsonify({
        'status': 'success',
        'emails': emailslist,
        'jobdescs': jobdescslist,
        'username': username
    })
    print(result)
    return result


@app.route('/user', methods=['GET'])
def usern():
    result = jsonify({
        'status': 'success',
        'username': username
    })
    return result


if __name__ == '__main__':
    app.run(debug=True)
