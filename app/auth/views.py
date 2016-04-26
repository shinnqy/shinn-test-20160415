from flask import request, render_template, session, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from google.appengine.ext import ndb

from . import auth
from ..models import User, DatastoreFile
from ..email import send_email, send_mail

import random

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		# if not current_user.confirmed and request.endpoint[:5] != 'auth.':
		# 	return redirect(url_for('auth.unconfirmed'))

@auth.route('/login', methods = ['GET', 'POST'])
# @oid.loginhandler
def login():
	if request.method == 'GET':
		if current_user is not None and current_user.is_authenticated:
			return redirect(url_for('main.index'))
		else:
			return render_template('auth/login.html')

	if request.method == 'POST':
		email = request.form.get("email")
		password = request.form.get("password")

		qry = User.query(User.key == ndb.Key(User, email))
		result = qry.fetch()
		if (len(result) > 0):
			user = result[0]
			if (result[0].verify_password(password)):
				login_user(user)
				return "correctPassword"
			else:
				return "wrongPassword"
		else:
			return "noSuchEmail"

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@auth.route('/register', methods = ['GET', 'POST'])
def register():
	if request.method == 'GET':
		if current_user.is_authenticated:
			return redirect(url_for('main.index'))
		else:
			return render_template('auth/register.html')

	if request.method == 'POST':
		name = request.form.get("name")
		password = request.form.get("password")
		email = request.form.get("email")
		isConfirmed = False
		# confirm_key = random.randint(99999, 999999)

		user = User(key = ndb.Key(User, email))
		user.name = name
		user.password = password
		user.email = email
		# user.avator_link = url_for('static', filename='images/defaultAvator.jpg', _external=True)
		# user.confirm_key = confirm_key
		user.isConfirmed = isConfirmed
		user.put()

		token = user.generate_confirmation_token()
		# send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user = user, token = token)

		# content = "<p>Hello, '%s':</p><br><br><p>Please click this to confirm your registration: '%s'</p>" % (user.name, token)
		# send_mail([user.email], 'Confirm Your Account', content)
		return "ok"

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.isConfirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))

# @auth.before_app_request
# def before_request():
# 	if current_user.is_authenticated() \
# 			and not current_user.isConfirmed \
# 			and request.endpoint[:5] != 'auth.'\
# 			and request.endpoint != 'static':
# 		return redirect(url_for('auth.unconfirmed'))
#
# @auth.route('/unconfirmed')
# def unconfirmed():
# 	if current_user.is_anonymous() or current_user.isConfirmed:
# 		return redirect(url_for('main.index'))
# 	return render_template('auth/unconfirmed.html')
#
# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
# 	token = current_user.generate_confirmation_token()
# 	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
# 	flash('A new confirmation email has been sent to you by email.')
# 	return redirect(url_for('main.index'))

@auth.route('/find_password', methods = ['POST'])
def find_password():
	email = request.form.get("email")
	password = request.form.get("password")

	qry = User.query(User.key == ndb.Key(User, email))
	result = qry.fetch()
	if (len(result) > 0):
		user = result[0]
		user.password = password
		user.email = email
		user.put()
		return "success"

@auth.route('/editProfile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	if request.method == 'POST':
		name = request.form.get("name")
		location = request.form.get("location")
		aboutMe = request.form.get("aboutMe")
		if name or location or aboutMe:
			if name:
				current_user.name = name
			if location:
				current_user.location = location
			if aboutMe:
				current_user.about_me = aboutMe
			current_user.put()
			flash('Profile update successfully!')
			# return redirect(url_for('main.user_account', username = current_user.name))
	return render_template('editProfile.html')

@auth.route('/editAccount', methods=['GET', 'POST'])
@login_required
def edit_account():
	if request.method == 'POST':
		oldPassword = request.form.get("oldPassword")
		newPassword = request.form.get("newPassword")
		if oldPassword and newPassword:

			current_user.put()
			flash('Profile update successfully!')
			# return redirect(url_for('main.user_account', username = current_user.name))
	return render_template('editAccount.html')

@auth.route('/changeItemStatus/<id>', methods = ['POST'])
@login_required
def changeItemStatus(id):
	haveExchange = request.form.get("haveExchange")
	entity = DatastoreFile.get_by_id(int(id))
	entity.haveExchange = bool(haveExchange)
	entity.put()
	return "success"
