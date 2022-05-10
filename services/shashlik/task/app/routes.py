from flask import render_template, flash, redirect, url_for, abort, send_from_directory
from flask_login import current_user, login_user, logout_user
from app import app, db
from app.models import User, Post, Thread
from app.forms import LoginForm, RegistrationForm, ThemeCreateForm, CommentForm, DeleteForm, ChangePasswordForm
from werkzeug.utils import secure_filename
import requests
import hashlib
import base64


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', lgn_form=LoginForm())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', lgn_form=LoginForm(), form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(base64.b64decode(form.password.data).decode('UTF-8'))
        db.session.add(user)
        db.session.commit()
        flash(f'Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', lgn_form=LoginForm(), form=form)

@app.route('/threads')
def threads():
    threads_list = Thread.query.all()
    return render_template('threads.html', lgn_form=LoginForm(), threads_list=threads_list)

@app.route('/create_theme', methods=['GET', 'POST'])
def create_theme():    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ThemeCreateForm()
    if form.validate_on_submit():
        filename = ''
        if form.file.data:
            filename = form.file.data.filename
            if filename != '':
                filename = secure_filename(filename)
                form.file.data.save(app.config['UPLOAD_FOLDER'] + filename)
        th = Thread(name=form.theme_name.data,
                body=form.body.data,
                author=current_user,
                is_private=form.is_private.data, 
                file_path=filename)
        db.session.add(th)
        db.session.commit()
        return redirect(url_for('thread', id=th.id))
    return render_template('create_theme.html', lgn_form=LoginForm(), form=form)

@app.route('/posts/<id>', methods=['GET', 'POST'])
def thread(id):
    thread = Thread.query.filter_by(id=id).first()
    if not thread:
        abort(404)
    posts_lst = Post.query.filter_by(main=thread).all()
    return render_template('thread.html', 
            lgn_form=LoginForm(), 
            tred=thread, 
            post_form=CommentForm(), 
            posts=posts_lst, 
            del_form=DeleteForm())

@app.route('/post_comment/<th_id>', methods=['POST'])
def post_comment(th_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = CommentForm()
    if form.validate_on_submit():
        thread = Thread.query.filter_by(id=th_id).first()
        if thread.is_private and thread.author != current_user:
            abort(403)
        post = Post(body=form.body.data, main=thread, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('thread', id=th_id))
    return redirect(url_for('thread', id=th_id))

@app.route('/delete_thread/<th_id>', methods=['POST'])
def del_thread(th_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    thread = Thread.query.filter_by(id=th_id).first()
    form = DeleteForm()
    if form.validate_on_submit() and current_user == thread.author:
        Thread.query.filter_by(id=th_id).delete()
        Post.query.filter(Post.main == thread).delete()
        db.session.commit()
        return redirect(url_for('threads'))
    return redirect(url_for('thread', id=th_id))


@app.route('/settings')
def settings():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    threads_list = Thread.query.filter_by(author=current_user).all()
    return render_template('settings.html',
            lgn_form=LoginForm,
            form=ChangePasswordForm(),
            threads_list=threads_list)

@app.route('/change_pass', methods=['POST'])
def change_pass():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        logout_user()
        user = User.query.filter_by(username=form.username.data).first()
        user.set_password(form.password2.data)
        db.session.commit()
        return redirect(url_for('login'))
    return redirect(url_for('settings'))

@app.route('/upload/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

