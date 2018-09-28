# -*- coding: utf-8
from flask import Flask,session,redirect,url_for,escape,request
from flask import render_template,g,send_from_directory
from werkzeug import secure_filename
import hashlib
import sqlite3
import os


app=Flask(__name__)
app.secret_key = 'a'
DATABASE = './main.db'

def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    return db

'''def init_db():
    with app.app_context():
        db=get_db()
        f=open('schema1.sql','r')
        db.execute(f.read())
        db.commit()
        f=open('schema2.sql','r')
        db.execute(f.read())
        db.commit()
        f=open('schema3.sql','r')
        db.execute(f.read())
        db.commit()'''# sqlite3 main.db < schema(n).sql

def add_user(name,pw,email,phone_num):
    sql_query='INSERT INTO users (name,pw,email,phone_num) VALUES("{}","{}","{}","{}")'.format(name,pw,email,phone_num)
    print (sql_query)
    db=get_db()
    db.execute(sql_query)
    db.commit()

def get_user(name,pw):
    sql_query = 'SELECT * FROM users where name="{}" and pw="{}"'.format(name,pw)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return '<a href="/index">You Already Logined</a>'
        else:
            return render_template('login.html')
    elif request.method == 'POST':

        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')
        hash_pw = hashlib.sha224(user_pw).hexdigest()
        ret = get_user(user_id,hash_pw)
        if len(ret) != 0:
            session['user_id'] = user_id
            session['user_pw'] = user_pw
            return redirect(url_for('index'))
        else:
            return '<a href="/login">No User.... Sign up!... </a>'

@app.route('/',methods=['GET'])
def home():
    if request.method == 'GET':
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return '<a href="/login">LOGOUT COMPLETE</a>'

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method=='POST':
        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')
        hash_pw = hashlib.sha224(user_pw).hexdigest()
        user_email = request.form.get('user_email')
        user_phone_num = request.form.get('user_phone_num')
        sql_query='SELECT * FROM users'
        db=get_db()
        rv=db.execute(sql_query)
        res=rv.fetchall()
        chk_list=[]
        for ret in res:
            chk_list.append(ret[0])
        if user_id in chk_list:
            return '<a href="/register">Duplication ID... please Retry</a>'
        else:
            add_user(user_id,hash_pw,user_email,user_phone_num)
            print add_user
            return '<a href="/login">LOGIN</a>'

@app.route('/index')
def index():
    if 'user_id' in session:
        user_id=session['user_id']
        res= get_post()
        return render_template('index.html',posts=res,user_name=user_id)
    return '<a href="/login">Login First</a>'

def del_user():
    if 'user_id' in session:
        user_id = session['user_id']
        sql_query='DELETE FROM users where name="{}"'.format(user_id)
        db=get_db()
        db.execute(sql_query)
        db.commit()


def edit_pw(user_id,hash_pw):
    sql_query='UPDATE users SET pw="{}" where name="{}"'.format(hash_pw,user_id)
    db=get_db()
    db.execute(sql_query)
    db.commit()

def edit_email(user_id,email):
    sql_query='UPDATE users SET email="{}" where name="{}"'.format(email,user_id)
    db=get_db()
    db.execute(sql_query)
    db.commit()

def edit_phone_num(user_id,phone_num):
    sql_query='UPDATE users SET phone_num="{}" where name="{}"'.format(phone_num,user_id)
    db=get_db()
    db.execute(sql_query)
    db.commit()

@app.route('/user_del',methods=['GET','POST'])
def user_del():
    if 'user_id' in session:
        session_id=session['user_id']
        if request.method=='GET':
            return render_template('user_del.html')
        elif request.method=='POST':
            user_id = request.form.get('user_id')
            user_pw = request.form.get('user_pw')
            hash_pw = hashlib.sha224(user_pw).hexdigest()
            sql_query='SELECT * FROM users'
            db=get_db()
            rv=db.execute(sql_query)
            res=rv.fetchall()
            chk_list=[]
            for ret in res:
                chk_list.append(ret[0])
            if user_id in chk_list:
                if session_id == user_id:
                    del_user()
                    return '<a href="/login">COMPLETE</a>'
                else:
                    return '<a href="/user_del">Permission Denied</a>'
            else:
                return '<a href="/index">No User</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/user_edit_chk',methods=['GET','POST'])
def user_edit_chk():
    session_id=session['user_id']
    if 'user_id' in session:
        if request.method=='GET':
            return render_template('user_edit_chk.html')
        elif request.method=='POST':
            user_id = request.form.get('user_id')
            user_pw = request.form.get('user_pw')
            hash_pw = hashlib.sha224(user_pw).hexdigest()
            ret = get_user(user_id,hash_pw)
            if session_id == user_id:
                if len(ret) != 0:
                    return redirect(url_for('user_edit'))
                else:
                    return '<a href="/user_edit_chk">Please Retry</a>'
            else:
                return '<a href="/index">Permisson Denied</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/user_edit_choose',methods=['GET','POST'])
def user_edit():
    if request.method=='GET':
        return render_template('user_edit_choose.html')


@app.route('/user_edit_pw',methods=['GET','POST'])
def user_edit_pw():
    if 'user_id' in session:
        user_id=session['user_id']
        if request.method=='GET':
            return render_template('user_edit_pw.html')
        elif request.method=='POST':
            user_pw= request.form.get('user_pw')
            hash_pw= hashlib.sha224(user_pw).hexdigest()
            edit_pw(user_id,hash_pw)
            return '<a href="/index">COMPLETE</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/user_edit_email',methods=['GET','POST'])
def user_edit_email():
    if 'user_id' in session:
        user_id=session['user_id']
        if request.method=='GET':
            return render_template('user_edit_email.html')
        elif request.method=='POST':
            user_email=request.form.get('user_email')
            edit_email(user_id,user_email)
            return '<a href="/index">COMPLETE</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/user_edit_phone_num',methods=['GET','POST'])
def user_edit_phone_num():
    if 'user_id' in session:
        user_id=session['user_id']
        if request.method=='GET':
            return render_template('user_edit_phone_num.html')
        elif request.method=='POST':
            user_phone_num=request.form.get('user_phone_num')
            edit_phone_num(user_id,user_phone_num)
            return '<a href="/index">COMPLETE</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/create_post',methods=['GET','POST'])
def create_post():
    if 'user_id' in session:
        if request.method=='GET':
            return render_template('create_post.html')
        elif request.method=='POST':
            post_title=request.form.get('post_title')
            post_writer=session['user_id']
            post_content=request.form.get('post_content')
            file_name=request.form.get('_file')
            if file_name == '':
                add_post(post_title,post_writer,post_content,None)
                return '<a href="/index">COMPLETE</a>' 
            else:
                f=request.files['_file']
                f.save('./uploads/'+secure_filename(f.filename))
                strf=str(f)
                splf=strf.split("'")
                add_post(post_title,post_writer,post_content,splf[1])
                return '<a href="/index">COMEPLETE</a>'
    else:
        return '<a href="/login">Login First</a>'

def add_post(title,writer,content,filename):
        db=get_db()
        sql_query = 'INSERT INTO posts (title,writer,content,filename) VALUES("{}","{}","{}","{}")'.format(title,writer,content,filename)
        db.execute(sql_query)
        db.commit()

def get_post():
    sql_query = "SELECT * FROM posts"
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_comments_from_p_num(p_number):
    sql_query='select * from comments where p_num="{}"'.format(p_number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_comments_from_num(number):
    sql_query='select * from comments where num="{}"'.format(number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_posts_from_num(number):
    sql_query='select * from posts where num="{}"'.format(number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_writer_from_posts_num(number):
    sql_query='select writer from posts where num="{}"'.format(number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_num_from_comments_p_num(p_number):
    sql_query='select num from comments where p_num="{}"'.format(p_number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_writer_from_comments_num(number):
    sql_query='select writer from comments where num="{}"'.format(number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

def get_p_num_from_comments_num(number):
    sql_query='select p_num from comments where num="{}"'.format(number)
    db=get_db()
    rv=db.execute(sql_query)
    res=rv.fetchall()
    return res

@app.route('/see_post',methods=['GET'])
def see_post():
    if 'user_id' in session:
        num=request.args.get('num')
        res_posts=get_posts_from_num(num)
        res_comments=get_comments_from_p_num(num)
        return render_template('see_post.html',posts=res_posts,comments=res_comments)
    else:
        return '<a href="/login">Login First</a>'

@app.route('/del_post', methods=['GET'])
def del_post():
    if 'user_id' in session:
        num=request.args.get('num')
        res=get_writer_from_posts_num(num)
        if res[0][0] == session['user_id']:
            res=get_num_from_comments_p_num(num)
            sql_query3='DELETE FROM posts where num="{}"'.format(num)
            if  res != []:
                return '<a href="index">comments exist</a>'
            else:
                db=get_db()
                db.execute(sql_query3)
                db.commit()
                return '<a href="/index">COMPLETE</a>'
        else:
            return '<a href="/index">Permission Denied</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/edit_post', methods=['GET','POST'])
def edit_post():
    if 'user_id' in session:
        if request.method=='GET':
            num=request.args.get('num')
            edit_post.num=num
            res=get_posts_from_num(num)
            res_writer=get_writer_from_posts_num(num)
            if res_writer[0][0] ==session['user_id']:
                return render_template('edit_post.html',posts=res)
            else:
                return '<a href="/index">Permission Denied</a>'

        elif request.method=='POST':
            num=edit_post.num
            post_title=request.form.get('post_title')
            post_content=request.form.get('post_content')
            sql_query1='UPDATE posts SET title="{}" where num="{}"'.format(post_title,num)
            sql_query2='UPDATE posts SET content="{}" where num="{}"'.format(post_content,num)
            if post_title=='':
                db=get_db()
                db.execute(sql_query2)
                db.commit()
                res=get_posts_from_num(num)
                return render_template('see_post_changed.html',posts=res)
            elif post_content=='':
                db=get_db()
                db.execute(sql_query1)
                db.commit()
                res=get_posts_from_num(num)
                return render_template('see_post_changed.html',posts=res)
            else:
                db=get_db()
                db.execute(sql_query1)
                db.execute(sql_query2)
                db.commit()
                res=get_posts_from_num(num)
                return render_template('see_post_changed.html',posts=res)
    else:
        return '<a href="/login">Login First</a>'

@app.route('/comment_post',methods=['GET','POST'])
def comment_post():
    if 'user_id' in session:
        user_id=session['user_id']
        if request.method=='GET':
            num=request.args.get('num')
            comment_post.num=num
            return render_template('comment_post.html',comment_writer=user_id)
        elif request.method=='POST':
            num=comment_post.num
            comment_writer=user_id
            comment_content=request.form.get('comment_content')
            add_comment(comment_writer,comment_content,num)
            res=get_posts_from_num(num)
            return render_template('see_post_changed.html',posts=res)
    else:
        '<a href="/login">Login First</a>'


def add_comment(writer,content,p_num):
    sql_query='INSERT INTO comments (writer,content,p_num) VALUES("{}","{}","{}")'.format(writer,content,p_num)
    db=get_db()
    db.execute(sql_query)
    db.commit()

@app.route('/del_comment',methods=['GET'])
def del_comment():
    if 'user_id' in session:
        num=request.args.get('num')
        res=get_writer_from_comments_num(num) # res[0][0]=comment_writer
        if res[0][0] == session['user_id']:
            res_p_num=get_p_num_from_comments_num(num)
            pnum=res_p_num[0][0]#res1[0][0]=comment_p_num
            res_posts=get_posts_from_num(pnum)#res= posts arguments
            sql_query3='DELETE FROM comments where num="{}"'.format(num)
            db=get_db()
            db.execute(sql_query3)
            db.commit()
            return render_template('see_post_changed.html',posts=res_posts)
        else:
            return '<a href="/index">Permission Denied</a>'
    else:
        return '<a href="/login">Login First</a>'

@app.route('/edit_comment',methods=['GET','POST'])
def edit_comment():
    if 'user_id' in session:
        if request.method=='GET':
            num=request.args.get('num')
            edit_comment.num=num
            res_id=get_writer_from_comments_num(num)
            res=get_comments_from_num(num)
            if res_id[0][0] == session['user_id']:
                return render_template('edit_comment.html',comments=res)
            else:
                return '<a href="/index">Permission Denied</a>'
        elif request.method=='POST':
            num=edit_comment.num
            comment_content=request.form.get('comment_content')
            sql_query1='UPDATE comments SET content="{}" where num="{}"'.format(comment_content,num)
            res_p_num=get_p_num_from_comments_num(num)
            pnum=res_p_num[0][0]
            res_posts=get_posts_from_num(pnum)
            db=get_db()
            db.execute(sql_query1)
            db.commit()
            return render_template('see_post_changed.html',posts=res_posts)
    else:
        return '<a href="/login">Login First</a>'

@app.route('/downloads',methods=['GET','POST'])
def filedownload():
    if request.method=='GET':
        num=request.args.get('num')
        res=get_posts_from_num(num)
        filepath=os.path.abspath('uploads')
        files=os.listdir(filepath)
        if res[0][4] in files:
            return send_from_directory(directory='./uploads',filename=res[0][4])
        else:
            return 'file deleted'

if __name__ == '__main__':
    #init_db()
    app.run(debug=True, host='0.0.0.0',port=3333)
