from flask_wtf import FlaskForm
from app import app
from app.models import User, Post, Thread
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.widgets import TextArea
from flask_wtf.file import FileAllowed, FileRequired
from time import time
from subprocess import run, PIPE
import hashlib
import urllib
import urllib.error
import urllib.request
import base64


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    def validate_password(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not user.check_password(self.password.data):
            raise ValidationError(f'Incorrect username or password!')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_password(self, password):
        passwd = base64.b64decode(password.data)
        p = run(['/usr/app/app/check_pass'], stdout=PIPE, input=passwd)
        if (p.returncode) or (p.stdout == b'WEAK\n'):
            raise ValidationError(f'Password too weak.')
        if len(password.data) > 512:
            raise ValidationError('Password too long.')

    def validate_username(self, username):
        if len(username.data) > 32:
            raise ValidationError('Username too long.')
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class ChangePasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Change password')

    def validate_password2(self, password2):
        if len(password2.data) > 512:
            raise ValidationError('New password too long')


class ThemeCreateForm(FlaskForm):
    theme_name = StringField('Theme name', validators=[DataRequired()])
    body = StringField(u'Text', validators=[DataRequired()], widget=TextArea())
    is_private = BooleanField('is private')
    file = FileField()
    submit = SubmitField('Create theme')

    def validate_theme_name(self, theme_name):
        if len(theme_name.data) > 256:
            raise ValidationError('Theme name too long.')

    def validate_body(self, body):
        if len(body.data) > 4096:
            raise ValidationError('Body too long.')

    def validate_file(self, file):
        if (not file) and (file.data.filename != '') and (file.data.filename.split('.')[-1] not in app.config['ALLOWED_EXTENSIONS']):
            raise ValidationError('Upload only images!')


class DeleteForm(FlaskForm):
    submit1 = SubmitField('Delete thread')


class CommentForm(FlaskForm):
    body = StringField(u'Text', validators=[DataRequired()], widget=TextArea())
    submit2 = SubmitField('Comment')
    
    def validate_body(self, body):
        if len(body.data) > 4096:
            raise ValidationError('Body too long.')

