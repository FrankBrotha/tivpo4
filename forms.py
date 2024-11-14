from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, Length, Email, email
import email_validator


class AdminLoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserRegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=255)])
    phonenumber = StringField('Номер телефона', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Зарегистрироваться')

class BookingForm(FlaskForm):
    startdate = DateField('Дата заезда', format='%Y-%m-%d', validators=[DataRequired()])
    enddate = DateField('Дата выезда', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Забронировать')

class ReviewForm(FlaskForm):
    rating = SelectField('Оценка',choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    reviewtext = StringField('Текст отзыва', validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')

class AdminRoomsForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    roomtype = StringField('Тип комнаты',validators=[DataRequired(), Length(max=255)])
    roomnumber = StringField('Номер комнаты', validators=[DataRequired(), Length(max=20)])
    floor = IntegerField('Этаж',validators=[DataRequired()])
    hastv = BooleanField('С телевизоров')
    haswifi = BooleanField('С Wi-Fi')
    hasminibar = BooleanField('С мини-баром')
    pricepernight = IntegerField('Цена за ночь',validators=[DataRequired()])
    capacity = IntegerField('Вместимость',validators=[DataRequired()])
    submit = SubmitField('Изменить')

class AdminUserForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    password = StringField('Пароль', validators=[DataRequired(), Length(max=255)])
    phonenumber = StringField('Номер телефона', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Изменить')

class AdminAdminsForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    username = StringField('Юзернейм',validators=[DataRequired(), Length(max=255)])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')

class AdminReviewsForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    bookingid = IntegerField('ID аренды', validators=[DataRequired()])
    rating = IntegerField("Оценка", validators=[DataRequired()])
    reviewtext = StringField('Текст отзыва', validators=[DataRequired()])
    submit = SubmitField('Изменить')

class AdminBookingsForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()])
    userid = IntegerField('ID пользователя', validators=[DataRequired()])
    roomid = IntegerField('ID комнаты', validators=[DataRequired()])
    startdate = DateField('Дата заезда', format='%Y-%m-%d', validators=[DataRequired()])
    enddate = DateField('Дата выезда', format='%Y-%m-%d', validators=[DataRequired()])
    totalprice = IntegerField('Конечная цена', validators=[DataRequired()])
    submit = SubmitField('Изменить')