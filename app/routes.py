from flask import render_template, redirect, flash, url_for, logging, request
from app import app, db
from app.forms import LoginForm, RegisterForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live !')
        return redirect(url_for('index'))

    posts = []
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
    
    return render_template('index.html', title='Home', form=form, posts=posts)

@app.route('/explore')
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(index))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Username or password is invalid')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Username or password is invalid')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'{user.username} succesfully registered!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author':user, 'body':"This is my first post"},
        {'author':user, 'body':"Now, this is my second post"}
    ]
    return render_template('user.html', title='Profile', user=user, posts=posts)
    

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not current_user.is_authenticated:
        flash('User is not registered')
        return redirect(url_for('index'))

    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('User information was modified')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def before_request():
    '''
    register the decorated function to be executed right 
    before the view function. This is extremely useful 
    because now I can insert code that I want to execute 
    before any view function in the application, and I 
    can have it in a single place
    '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/follow/<username>')
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} doesn\'t exist')
        return redirect(url_for('index'))
    if user == current_user:
        flash(f'You can\'t follow yourself')
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    flash(f'You now following {username}')
    return redirect(url_for('index'))

@app.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} doesn\'t exist')
        return redirect(url_for('index'))
    if user == current_user:
        flash(f'You can\'t unfollow yourself')
        return redirect(url_for('index'))
    if not current_user.is_following(user):
        flash(f'You aren\'t following {username}')
        return redirect(url_for('index'))
    
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You now stopped following {username}')
    return redirect(url_for('index'))


