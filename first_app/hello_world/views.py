from .models import User, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash 

app = Flask(__name__)


@app.route('/')
def index():
	posts = get_todays_recent_posts()
	return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		# do stuff
		username = request.form['username']
		password = request.form['password']
		
		if len(username) < 1:
			flash('User name must be at least one character long.')		
		elif not User(username).register(password):
			flash('Username %s already exists' % (username))
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))
	
	return render_template('register.html')
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
		if not User(username).verify_password(password):
			flash('Invalid login.')
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))
			
	return render_template('login.html')
	

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('username', None)
	flash('Logged out.')
	return redirect(url_for('index'))
	

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    posts = user_being_viewed.get_recent_posts()
    print user_being_viewed_username
    print posts
    if logged_in_username:
        logged_in_user = User(logged_in_username)        

    return render_template(
        'profile.html',
        username=username,
        posts=posts
    )	

@app.route('/add_post', methods=['POST'])
def add_post():
	title = request.form['title']
	tags = request.form['tags']
	text = request.form['text']
	
	if not title:
		flash('You must give your post a title.')
	elif not tags:
		flash('You must give your post at least one tag.')
	elif not text:
		flash('You must give your post a text body.')
	else:
		User(session['username']).add_post(title, tags, text)

	return redirect(url_for('index'))












