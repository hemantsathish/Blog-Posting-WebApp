from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
import re
import os

full_path = os.path.realpath('blog.db')
print(full_path + "\n")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+full_path
db = SQLAlchemy(app)
app.secret_key = "EP)tozJYFMdf!C5(sA`S|wn?mJ(0*f"
Base = automap_base()
Base.prepare(db.engine, reflect = True)
register = Base.classes.register

class Blogpost(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	subtitle = db.Column(db.String(50))
	author = db.Column(db.String(20))
	date_posted = db.Column(db.DateTime)
	content = db.Column(db.Text)

class Register(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(20))

class Editlogs(db.Model):
	editid = db.Column(db.Integer, primary_key=True)
	id = db.Column(db.Integer )
	title = db.Column(db.String(50))
	subtitle = db.Column(db.String(50))
	date_posted = db.Column(db.DateTime)
	content = db.Column(db.Text)

@app.route('/')
@app.route('/main')
def main():
	return render_template('main.html')


@app.route('/index')
def index():
	posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
	print(posts)
	return render_template('index.html', posts=posts)


@app.route('/search',methods =['GET', 'POST'])
def search():
	msg=''
	error = ''


	i = 1
	if request.method == 'POST' and 'searchbox' in request.form:
		searchvalue = request.form['searchbox']
		i = request.form['selection']

		if(searchvalue ==''):
			print('yes')
			posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
			error="Please enter a search term"
			return render_template('index.html', posts=posts,error=error)

		posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).filter(Blogpost.title.contains(searchvalue)).all()
		
		if(i == "2"):
			posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).filter(Blogpost.author.startswith(searchvalue)).all()
		
		if(i == "3"):
			posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).filter(Blogpost.content.contains(searchvalue)).all()


		print(posts)
		lenPosts = len(posts)
		if(lenPosts == 0):
			msg="No results found"
		else:
			msg= str(lenPosts) + " result(s) found"
		return render_template('index.html', posts=posts,msg=msg)

	posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
	return render_template('index.html', posts=posts,error =error)


@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if(request.method == 'POST'):
		username = request.form['username']
		password = request.form['password']
		if(username =='' or password ==''):
			msg="Please enter both username and password"
			return render_template('login.html', msg = msg)
		r = Register.query.filter_by(username=username,password=password).first()
		if r:
			session['loggedin'] = True
			session['id'] = r.userid
			session['username'] = r.username
			msg = 'Logged in successfully !'

			return redirect(url_for('index'))
			#return render_template('index.html',  ,session=session,posts=posts)
		else:
			msg = 'Incorrect username / password !'
			print(msg)
	return render_template('login.html', msg = msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('main'))


@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		r = Register.query.filter_by(username=username).first()
		e = Register.query.filter_by(email=email).first()
		if not username or not password or not email:
			msg = 'Please fill out the form !'
			render_template('register.html',msg=msg)
		if(e is None):
			if r is None:
				new_user = Register(username=username,password= password,email=email)
				db.session.add(new_user)
				db.session.commit()
				msg = 'You have successfully registered !'
				#return render_template('index.html', msg = msg,session=session)
				return redirect(url_for('login'))
			elif r.username==username:
				msg = 'Account already exists !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
				msg = 'Invalid email address !'
				return render_template('register.html', msg = msg)
			elif not re.match(r'[A-Za-z0-9]+',username):
				msg = 'Username must contain only characters and numbers !'
				return render_template('register.html', msg = msg)
		else:
			msg = 'That Email is already registerd !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:post_id>')
def post(post_id):
	post = Blogpost.query.filter_by(id=post_id).one()

	if(session['username'] == post.author):
		return render_template('postOfAuthor.html', post=post)
	else:
		return render_template('post.html', post=post)


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/addpost', methods=['POST'])
def addpost():
	title = request.form['title']
	subtitle = request.form['subtitle']
	author = session['username']
	content = request.form['content']
	dtn = datetime.now()
	if(title and content ):
		post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted= dtn)
		#edit =  Editlogs(postid =post.id, title=title, subtitle=subtitle, date_posted=dtn, content=content)
		db.session.add(post)
		#db.session.add(edit)
		db.session.commit()
		edit =  Editlogs(id =post.id, title=title, subtitle=subtitle, date_posted=dtn, content=content)
		db.session.add(edit)
		db.session.commit()

		return redirect(url_for('index'))
	else:
		msg = "Please add a title and content"
		return render_template('add.html',)


@app.route('/redirectToEdit/<int:post_id>', methods =['GET', 'POST'])
def redirectToEdit(post_id):
	post = Blogpost.query.filter_by(id=post_id).one()
	return render_template('edit.html', post = post)


@app.route('/edit/<int:post_id>', methods =['GET', 'POST'])
def edit(post_id):
	post = Blogpost.query.filter_by(id=post_id).one()
	postAuthor = post.author

	title = request.form['title']
	subtitle = request.form['subtitle']
	editor = session['username']
	content = request.form['content']

	if(title=='' and content==''):
		return render_template('edit.html', post = post,msg="Please enter the Title and Content")
	
	if(title==''):
		return render_template('edit.html', post = post,msg="Please enter the Title ")

	if(content==''):
		return render_template('edit.html', post = post,msg="Please enter the Content")

	if(postAuthor == editor):
		post.title = title
		post.subtitle = subtitle
		post.content = content
		dtn = datetime.now()
		post.date_posted = dtn
		post = Editlogs(id =post.id, title=title, subtitle=subtitle, date_posted=dtn, content=content)
		db.session.add(post)
		db.session.commit()
	return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods =['GET', 'POST'])
def delete(post_id):
	print(post_id)
	Blogpost.query.filter(Blogpost.id == post_id).delete()
	db.session.commit()

	Editlogs.query.filter(Editlogs.id == post_id).delete()
	db.session.commit()
	return redirect(url_for('index'))


@app.route('/profile/<string:username>', methods =['GET', 'POST'])
def profile(username):
	posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).filter(Blogpost.author == username).all()
	return  render_template('profile.html', posts = posts,username = username)


if __name__ == '__main__':
    app.run(debug=True)

