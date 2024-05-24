from flask import Flask, render_template, request, redirect, flash
import re, os
from models import session, User, select, Picture
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message


app = Flask(__name__)


app.secret_key = 'secret_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rosulka.abaldui@gmail.com'
app.config['MAIL_PASSWORD'] = 'axvzkwqljxnoraxx'

mail = Mail(app)

current_name = None
current_email = None
data_type = 'users'

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

def is_valid_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)

@app.route('/send-email')
def send_test_email(receiver, password):
    subject = "Успішна регістрація"
    sender = "kursac2024@gmail.com"
    recipients = [f"{receiver}",]
    text_body = f"Ви успішно зареєструвались.\nВаш логін та пароль:\n{receiver}\n{password}"
    html_body = f"Ви успішно зареєструвались.\nВаш логін та пароль:\n{receiver}\n{password}"
    send_email(subject, sender, recipients, text_body, html_body)
    return "0"

@app.route('/forgot_password', methods=['POST','GET'])
def forgot_password():
    return render_template('forgot_password.html', error_messages={})

@app.route('/send_password', methods=['POST', 'GET'])
def send_password():
    error_messages = {'email': '', 'password': ''}

    email = request.form['email']

    if not email:
        error_messages['email'] = 'Please enter your email address.'
        return render_template('forgot_password.html', error_messages=error_messages)

    user = session.query(User).filter(User.email == email).first()
    if user:
        password = user.password
    else:
        error_messages['email'] = 'Email address not found.'
        return render_template('forgot_password.html', error_messages=error_messages)

    subject = "Відновлення паролю"
    sender = "kursac2024@gmail.com"
    recipients = [email]
    text_body = f"Ви не змогли зайти.\nВаш пароль: {password}"
    html_body = f"Ви не змогли зайти.\nВаш пароль: {password}"
    send_email(subject, sender, recipients, text_body, html_body)

    error_messages['password_success'] = 'Your password is waiting for you in the email. Try again in 60 seconds.'
    return redirect('/login')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error_messages = {'name': '', 'email': '', 'password': ''}
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not name:
            error_messages['name'] = 'Please enter your name.'
        if not email:
            error_messages['email'] = 'Please enter your email address.'
        elif not is_valid_email(email):
            error_messages['email'] = 'Invalid email address.'
        if not password:
            error_messages['password'] = 'Please enter your password.'
        elif not is_valid_password(password):
            error_messages['password_requirements'] = 'Password must be at least 8 characters long, contain at least one uppercase letter and at least one digit.'

        if not all(error == '' for error in error_messages.values()):
            return render_template('registration.html', error_messages=error_messages)

        stmt = select(User)
        result = session.execute(stmt)
        for user in result.scalars():
            if user.email == email:
                error_messages['email'] = 'You are already registered.'
                return redirect('login')
        else:
            user = User(name=name, email=email, password=password)
            session.add(user)
            session.commit()

        
            send_test_email(email, password)

            return redirect('/login')

    return render_template('registration.html', error_messages=error_messages)

@app.route('/')
def index():
    global current_name, current_email

    if current_email is None and current_name is None:
        return redirect('/login')

    user = session.query(User).filter_by(email=current_email).first()
    if user:
        drawings = session.query(Picture).filter_by(user_id=user.id).all()
        return render_template('mainpage.html', current_name=current_name, current_email=current_email, drawings=drawings)
    else:
        return render_template('mainpage.html', current_name=current_name, current_email=current_email, drawings=[])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_messages = {'email': '', 'password': ''}

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email:
            error_messages['email'] = 'Please enter your email address.'
        elif not is_valid_email(email):
            error_messages['email'] = 'Invalid email address.'

        if not password:
            error_messages['password'] = 'Please enter your password.'
        elif not is_valid_password(password):
            error_messages['password_requirements'] = 'Password must be at least 8 characters long, contain at least one uppercase letter and at least one digit.'

        if not all(error == '' for error in error_messages.values()):
            return render_template('login.html', error_messages=error_messages)

        stmt = select(User)
        result = session.execute(stmt)

        for user in result.scalars():
            if user.email == email and user.password == password:
                global current_email, current_name
                current_name = user.name
                current_email = email
                if current_email == 'admin@gmail.com' and current_name == 'admin':
                    return redirect('/admin')
                return render_template('profile.html', current_email=current_email, current_name=current_name)
        else:
            error_messages['password'] = 'Invalid password or email'
            return render_template('login.html', error_messages=error_messages)
        

    return render_template('login.html', error_messages={})

@app.route('/profile')
def profile():
    global current_name, current_email

    if current_email is None and current_name is None:
        return redirect('login')
    
    user = session.query(User).filter_by(email=current_email).first()
    if user:
        drawings = session.query(Picture).filter_by(user_id=user.id).all()
        return render_template('profile.html', current_name=current_name, current_email=current_email, drawings=drawings)
    else:
        return render_template('profile.html', current_name=current_name, current_email=current_email, drawings=[])

@app.route('/log_in_or_out')
def log_in_or_out():
    global current_name, current_email
    if current_email is None:
        return redirect('login')
        
    current_email = None
    current_name = None
    return redirect('/')

@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if request.method == 'POST':
        global current_name, current_email

        error_messages = {'old-password': '', 'password': ''}

        old_password = request.form['old-password']
        new_password = request.form['password']

        if not old_password:
            error_messages['old-password'] = 'Please enter your old password.'
        elif not is_valid_password(old_password):
            error_messages['old-password'] = 'Password must be at least 8 characters long, contain at least one uppercase letter and at least one digit.'

        if not new_password:
            error_messages['password'] = 'Please enter your new password.'
        elif not is_valid_password(new_password):
            error_messages['password'] = 'Password must be at least 8 characters long, contain at least one uppercase letter and at least one digit.'

        if any(error_messages.values()):
            return render_template('change_password.html', error_messages=error_messages)

        user = session.query(User).filter(User.email == current_email).first()

        if user and user.password == old_password:
            user.password = new_password
            session.commit()

            subject = "Пароль успішно змінено"
            sender = "kursac2024@gmail.com"
            recipients = [current_email]
            text_body = f"Ви змінили пароль.\nВаш новий пароль: {new_password}"
            html_body = f"Ви змінили пароль.\nВаш новий пароль: {new_password}"
            send_email(subject, sender, recipients, text_body, html_body)

            return render_template('profile.html', current_email=current_email, current_name=current_name)
        else:
            error_messages['old-password'] = 'Invalid old password'
            return render_template('change_password.html', error_messages=error_messages)

    return render_template('change_password.html', error_messages={})

@app.route('/drawCanwas')
def drawCanwas():
    global current_name, current_email

    if current_email is None:
        return redirect('login')

    image_path = request.args.get('image_path')
    return render_template('drawCanwas.html', current_name=current_name, current_email=current_email, image_path=image_path, error_messages='')

@app.route('/delete_account')
def delete_account():
    global current_email, current_name
    user = session.query(User).filter(User.email == current_email).first()
    
    if user:
        pictures = session.query(Picture).filter(Picture.user_id == user.id).all()
        for picture in pictures:
            os.remove(picture.path)
        for picture in pictures:
            session.delete(picture)
        session.delete(user)
        session.commit()

    subject = "Видалення аккаунту"
    sender = "kursac2024@gmail.com"
    recipients = [current_email]
    text_body = f"На жаль ви видалили аккаунт.\nДо нових зустрічей!"
    html_body = f"На жаль ви видалили аккаунт.\nДо нових зустрічей!"
    send_email(subject, sender, recipients, text_body, html_body)

    current_name = None
    current_email = None

    return redirect('/login')

@app.route('/save_image', methods=['POST'])
def save_image():
    global current_email

    if current_email is None:
        return redirect('login')

    user = session.query(User).filter(User.email == current_email).first()

    if 'image' not in request.files:
        return 'No file part', 400

    image_file = request.files['image']

    old_image_path = request.form['imagePath']
    old_image_name = request.form['imageName']

    print(old_image_path)
    print(old_image_name)

    if image_file.filename == '':
        return 'No selected file', 400

    if str(old_image_path) == 'null' and str(old_image_name) == 'null':
        pictures = session.query(Picture).filter(Picture.user_id == user.id).all()

        if len(pictures) == 0:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads", filename + ".png")
                image_file.save(image_path)

                picture = Picture(path=image_path, name=filename, user=user)
                session.add(picture)
                session.commit()
        if len(pictures) == 1:
            if pictures[0].name == image_file.filename:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads", filename + ".png")
                print('-')
                print(filename)
                print(image_path)
                
                picture = session.query(Picture).filter(Picture.path == image_path).first()
                os.remove(image_path)
                session.delete(picture)
                session.commit()

                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads", filename + ".png")
                image_file.save(image_path)

                picture = Picture(path=image_path, name=filename, user=user)
                session.add(picture)
                session.commit()
            else:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads", filename + ".png")
                image_file.save(image_path)

                picture = Picture(path=image_path, name=filename, user=user)
                session.add(picture)
                session.commit()
        elif len(pictures) > 1:
            for picture in pictures:
                if picture.name == image_file.filename:   
                    filename = secure_filename(image_file.filename)
                    image_path = os.path.join("static/uploads", filename + ".png")

                    picture = session.query(Picture).filter(Picture.path == image_path).first()
                    os.remove(image_path)
                    session.delete(picture)
                    session.commit()

                    filename = secure_filename(image_file.filename)
                    image_path = os.path.join("static/uploads", filename + ".png")
                    image_file.save(image_path)

                    picture = Picture(path=image_path, name=filename, user=user)
                    session.add(picture)
                    session.commit()
                    
                    break
            else:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join("static/uploads", filename + ".png")
                image_file.save(image_path)

                picture = Picture(path=image_path, name=filename, user=user)
                session.add(picture)
                session.commit()


        return render_template('mainpage.html')
    else:
        pictures = session.query(Picture).filter(Picture.user_id == user.id).all()

        if len(pictures) == 1:
            if pictures[0].name == old_image_name:
                picture = session.query(Picture).filter(Picture.path == old_image_path).first()
                os.remove(old_image_path)
                session.delete(picture)
                session.commit()

                image_path = os.path.join("static/uploads", old_image_name + ".png")
                image_file.save(image_path)

                picture = Picture(path=image_path, name=old_image_name, user=user)
                session.add(picture)
                session.commit()
        elif len(pictures) > 1:
            for picture in pictures:
                if picture.name == old_image_name:
                    picture = session.query(Picture).filter(Picture.path == old_image_path).first()
                    os.remove(old_image_path)
                    session.delete(picture)
                    session.commit()

                    image_path = os.path.join("static/uploads", old_image_name + ".png")
                    image_file.save(image_path)

                    picture = Picture(path=image_path, name=old_image_name, user=user)
                    session.add(picture)
                    session.commit()
                    
                    break

    return render_template('mainpage.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global data_type
    try:
        users = session.query(User).all()
        data_type = 'users'
        session.commit()
    except Exception:
        flash('An error occurred while getting users')
    return render_template('admin.html',
                           users=users,
                           data_type=data_type,
                           current_name=current_name, 
                           current_email=current_email)

@app.route('/delete', methods=['POST'])
def delete_image():
    global data_type
    if data_type == 'users' or data_type == 'user':
        try:
            id = request.form['id']
            if id == '1':
                return get_users_db()
            user = session.query(User).filter(User.id == id).first()
            if user:
                pictures = session.query(Picture).filter(Picture.user_id == user.id).all()
                for picture in pictures:
                    os.remove(picture.path)
                for picture in pictures:
                    session.delete(picture)
                session.delete(user)
                session.commit()
            if user is None:
                return get_users_db()
        except Exception as e:
            flash('An error occurred while getting user')
            print(f"Error: {e}")
        return get_users_db()
    elif data_type == 'pictures' or data_type == 'picture':
        try:
            id = request.form['id']
            picture = session.query(Picture).filter(Picture.id == id).first()
            if picture:
                os.remove(picture.path)
                session.delete(picture)
                session.commit()
            if picture is None:
                return get_pictures_db()
        except Exception as e:
            flash('An error occurred while getting picture')
            print(f"Error: {e}")
        return get_pictures_db()


@app.route('/users_db', methods=['GET'])
def get_users_db():
    global data_type
    try:
        users = session.query(User).all()
        data_type = 'users'
        session.commit()
    except Exception:
        flash('An error occurred while getting users')
    return render_template('admin.html', 
                           users=users, 
                           data_type=data_type, 
                           current_name=current_name, 
                           current_email=current_email)

@app.route('/pictures_db', methods=['GET'])
def get_pictures_db():
    global data_type
    try:
        pictures = session.query(Picture).all()
        data_type = 'pictures'
        session.commit()
    except Exception:
        flash('An error occurred while getting users')
    return render_template('admin.html', 
                           pictures=pictures, 
                           data_type=data_type, 
                           current_name=current_name, 
                           current_email=current_email)

@app.route('/search', methods=['POST'])
def get_user():
    global data_type
    if data_type == 'users' or data_type == 'user':
        try:
            id = request.form['id']
            user = session.query(User).filter(User.id == id).first()
            session.commit()
            if user is None:
                return render_template('admin.html', 
                            data_type='', 
                            current_name=current_name, 
                            current_email=current_email)
        except Exception:
            flash('An error occurred while getting user')
        return render_template('admin.html',
                            user=user,
                            data_type='user', 
                            current_name=current_name, 
                            current_email=current_email)
    elif data_type == 'pictures' or data_type == 'picture':
        try:
            id = request.form['id']
            picture = session.query(Picture).filter(Picture.id == id).first()
            session.commit()
            if picture is None:
                return render_template('admin.html',
                            data_type='', 
                            current_name=current_name, 
                            current_email=current_email)
        except Exception:
            flash('An error occurred while getting picture')
        return render_template('admin.html',
                            picture=picture, 
                            data_type='picture', 
                            current_name=current_name, 
                            current_email=current_email)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    app.secret_key = "secret"