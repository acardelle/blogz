from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cake2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337'

# classes ----------------------
class Blog(db.Model):

   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(120))
   body_text = db.Column(db.String(240))
   owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   completed = db.Column(db.Boolean)   

   def __init__(self, title, body_text, owner):
       self.title = title
       self.body_text = body_text
       self.owner = owner
       self.completed = False
      

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    postings = db.relationship('Blog', backref='owner')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# functions ------------------

def is_blank(word):
  if word == '':
    return True
  else:
    return False

def invalid_char(word):
  if (len(word) < 3) or (len(word)> 20) or (' ' in word):
    return True
  else:
    return False

def invalid_emal(word):
  if (len(word) < 3) or (len(word)> 20) or (' ' in word) or ("@" not in word) or ("." not in word) or (word.count('@') >1) or (word.count('.') >1):
    return True
  else:
    return False

#app.routes -------------

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
 
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        username = request.form['usr_name']
        email    = request.form['e_mail']
        password = request.form['pas_word']
        veriword = request.form['ver_word']

        user_error = ''
        pass_error = ''
        veri_error = ''
        emal_error = ''

        #Username checks
        if invalid_char(username) == True:
            user_error = 'Invalid username'
        if is_blank(username) == True:
            user_error = 'No username input detected (Must be 3-20 characters with no whitespaces)'

        #Password checks
        if invalid_char(password) == True:
            pass_error = 'Invalid password (Must be 3-20 characters with no whitespaces)'
        if is_blank(password) == True:
            pass_error = 'No password input detected'

        #Verify checks
        if veriword != password:
            veri_error = 'Passwords do not match'

        #Email checks
        if (email != '') and invalid_emal(email) == True:
            emal_error = 'Invalid email address (Must be include a valid domain)'
        
        #Success condition
        if not user_error and not pass_error and not veri_error and not emal_error:

            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, email, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            
            else:
                # TODO - user better response messaging
                return "<h1>Duplicate user</h1>"
        
        #Error redirection
        else:
            return render_template('register.html',
            user_error=user_error,
            user_field = username,
            pass_error=pass_error,
            veri_error=veri_error,
            emal_error=emal_error,
            emal_field = email)

        # TODO - validate user's data




    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/', methods=['POST','GET'])
def index():

    postings = Blog.query.filter_by(completed = False).all()
    completed_postings = Blog.query.filter_by(completed = True).all()

    return render_template('blog.html', title="Get It Bloged!", postings=postings, completed_postings=completed_postings)

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        posting_title = request.form['posting_title']
        posting_text = request.form['posting_text']
        if (posting_title == '') or (posting_text == ''):
            post_error = 'Please provide a blog post title and post body.'
            return render_template('newpost.html',post_error=post_error)
        else:
            new_posting = Blog(posting_title, posting_text, owner)
            db.session.add(new_posting)
            db.session.commit()
            grab_id = str(new_posting.id)
            return redirect('/indypost?id=' + grab_id)
    else:
        return render_template('newpost.html')

@app.route('/indypost', methods=['POST','GET'])
def indypost():
    
    id_d = request.args.get('id')
    case_post = Blog.query.filter_by(id=id_d).first()

    return render_template('indypost.html', case_post=case_post)

"""@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")"""

if __name__ == '__main__':
    app.run()