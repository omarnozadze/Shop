from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('auth.login'))


@auth.route('/user-profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        raise LookupError("User not found")

    if request.method == 'POST':
        # Get the updated information from the form
        new_email = request.form.get('email')
        new_phone_Number = request.form.get('phone_Number')
        new_address = request.form.get('address')
        new_first_name = request.form.get('first_name')

        

        # Update the user's information
        user.email = new_email
        user.phone_Number = new_phone_Number
        user.address = new_address
        user.first_name = new_first_name

        # Update other user attributes as needed (e.g., address)

        # Commit the changes to the database
        db.session.commit()

        flash('Profile updated successfully!', category='success')

    return render_template("user_profile.html", user=user,current_user=current_user)




@auth.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template("admin.html",user=current_user.id)
    else:
        flash("you must be admin")
        return redirect(url_for('views.home'))






@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        address = request.form.get('address')
        phone_Number = request.form.get('phone_Number')  
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        

        user = User.query.filter_by(email=email).first()
        existing_phone = User.query.filter_by(phone_Number=phone_Number).first()
        if user:
            flash('Email already exists.', category='error')
        if existing_phone:
            flash('Phone number already exists. Please use a different phone number.', 'warning')
            return redirect(url_for('auth.sign_up'))
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email = email, first_name = first_name, phone_Number = phone_Number,address = address,
            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
