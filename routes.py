from math import floor

from flask import render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy import text

from forms import AdminLoginForm, UserLoginForm, UserRegistrationForm, BookingForm, ReviewForm, AdminRoomsForm, \
    AdminUserForm, AdminAdminsForm, AdminReviewsForm, AdminBookingsForm
from models import Admin, User, Rooms, Bookings, Reviews
from extensions import login_manager, db
from sqlalchemy import or_, and_, desc
from functools import wraps
from datetime import datetime

translations = {
    "Single": "Одноместный",
    "Double": "Двухместный",
    "Suite": "Люкс",
    "Room": "Комната",
}


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith("admin_"):
        user_id = user_id.split("_")[1]
        return Admin.query.get(int(user_id))
    else:
        user_id = user_id.split("_")[1]
        return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)

    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, User):
            return redirect(url_for('home'))
        return f(*args, **kwargs)

    return decorated_function


@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Авторизация успешна!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Авторизация неуспешна, пожалуйста перепроверьте корректность введеных данных',
                  'danger')
    return render_template('login.html', form=form)


def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = User().query.filter_by(email=form.email.data).first()
        if user:
            flash("Данная почта уже используется!", 'danger')
            return redirect(url_for('register'))
        last_user_id = db.session.query(User.id).order_by(User.id.desc()).first()

        if last_user_id:
            new_id = last_user_id[0] + 1
        else:
            new_id = 1
        new_user = User(
            id=new_id,
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            phonenumber=form.phonenumber.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


def home():
    get_flashed_messages()
    if isinstance(current_user, User):
        return redirect(url_for('dashboard'))
    elif isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    return render_template('home.html')


@login_required
@user_required
def dashboard():
    return render_template('dashboard.html', username=current_user.name)


@login_required
@user_required
def rooms():
    all_rooms = Rooms.query.all()
    for room in all_rooms:
        translated_type = translations.get(room.roomtype)  # используем перевод
        room.roomtype = translated_type
    return render_template('rooms.html', username=current_user.name, rooms=all_rooms)


@login_required
@user_required
def bookroom(roomnumber):
    room = Rooms.query.filter_by(roomnumber=roomnumber).first()

    if not room:
        return redirect(url_for('rooms'))
    today = datetime.now().strftime(('%Y-%m-%d'))
    bookings = Bookings.query.order_by(Bookings.id.desc()).first()
    if bookings:
        new_id = bookings.id + 1
    else:
        new_id = 1
    bookings = Bookings.query.filter(
        and_(
            Bookings.roomid == room.id,
            or_(
                Bookings.startdate >= today,
                Bookings.enddate >= today
            )
        )
    ).all()
    busylist = []
    for book in bookings:
        new_startdate = book.startdate.strftime(('%d-%m-%Y'))
        new_enddate = book.enddate.strftime(('%d-%m-%Y'))
        busylist.append([new_startdate, new_enddate])
    form = BookingForm()
    new_booking = Bookings(id=new_id,
                           userid=current_user.id,
                           roomid=room.id,
                           )
    if form.validate_on_submit():
        startdate = form.startdate.data
        enddate = form.enddate.data
        if startdate >= enddate:
            flash('Некорректно указаны даты бронирования, дата окончания должна быть позже даты начала',
                  'danger')
            return redirect(url_for('bookroom', roomnumber=roomnumber))
        bookings = Bookings.query.filter(
            and_(
                Bookings.roomid == room.id,
                or_(
                    Bookings.startdate >= startdate,
                    Bookings.enddate >= enddate
                )
            )
        ).all()
        if bookings:
            flash('Некорректно указаны даты бронирования, данные даты уже заняты',
                  'danger')
            return redirect(url_for('bookroom', roomnumber=roomnumber))
        nights = (enddate - startdate).days
        totalprice = nights * room.pricepernight
        new_booking.startdate = startdate.strftime(('%Y-%m-%d'))
        new_booking.enddate = enddate.strftime(('%Y-%m-%d'))
        new_booking.totalprice = totalprice

        db.session.add(new_booking)
        db.session.commit()
        flash('Бронирование успешно создано!', 'success')
        return redirect(url_for('bookroom', roomnumber=roomnumber))

    return render_template('book.html', username=current_user.name,
                           roomnumber=roomnumber, form=form, price_per_night=room.pricepernight,
                           today=today, busylist=busylist)


@login_required
@user_required
def review(bookid):
    booking = Bookings.query.filter(and_(Bookings.userid == current_user.id, Bookings.id == bookid)).first()
    if not booking:
        return redirect(url_for('mybookings'))
    room = Rooms.query.filter(Rooms.id == booking.roomid).first()
    form = ReviewForm()
    if form.validate_on_submit():
        review = Reviews.query.filter(Reviews.bookingid == bookid).first()
        if not review:
            last_review = Reviews.query.order_by(Reviews.id.desc()).first()
            if last_review:
                new_id = last_review.id + 1
            else:
                new_id = 1
            review = Reviews(
                id=new_id,
                bookingid=bookid
            )
        review.rating = form.rating.data
        review.reviewtext = form.reviewtext.data
        db.session.add(review)
        db.session.commit()
        flash('Отзыв успешно оставлен', 'info')
    return render_template('review.html', username=current_user.name, form=form, bookid=bookid,
                           roomnumber=room.roomnumber)


@login_required
@user_required
def mybookings():
    bookings = Bookings.query.filter(Bookings.userid == current_user.id, ).order_by(desc(Bookings.startdate)).all()

    bookings_list = []
    for booking in bookings:
        room = Rooms.query.filter_by(id=booking.roomid).first()
        bookings_list.append([room.roomnumber, booking.startdate, booking.enddate,
                              (booking.enddate - booking.startdate).days, booking.totalprice, booking.id])
    return render_template('mybookings.html', username=current_user.name,
                           bookings_list=bookings_list)


@login_required
@user_required
def myreviews():
    bookings = Bookings.query.filter(Bookings.userid == current_user.id, ).order_by(desc(Bookings.startdate)).all()

    review_list = []
    for booking in bookings:
        room = Rooms.query.filter_by(id=booking.roomid).first()
        review = Reviews.query.filter_by(bookingid=booking.id).first()
        if not room or not review:
            continue
        review_list.append(
            [room.roomnumber, booking.startdate, booking.enddate, (booking.enddate - booking.startdate).days,
             review.rating, review.reviewtext])
    return render_template('myreviews.html', username=current_user.name, review_list=review_list)


def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Повторите попытку', 'danger')
    return render_template('admin_login.html', form=form)


@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html', username=current_user.username)


@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.id).all()
    return render_template('admin_users.html', username=current_user.username, users=users)


@login_required
@admin_required
def admin_rooms():
    rooms = Rooms.query.order_by(Rooms.id).all()
    return render_template('admin_rooms.html', username=current_user.username, rooms=rooms)


@login_required
@admin_required
def admin_bookings():
    bookings = Bookings.query.order_by(Bookings.id).all()
    nights = []
    for book in bookings:
        nights.append((book.enddate - book.startdate).days)
    return render_template('admin_bookings.html', username=current_user.username,
                           bookings=bookings, nights=nights)


@login_required
@admin_required
def admin_reviews():
    reviews = Reviews.query.order_by(Reviews.id).all()
    return render_template('admin_reviews.html', username=current_user.username, reviews=reviews)


@login_required
@admin_required
def admin_admins():
    admins = Admin.query.order_by(Admin.id).all()
    return render_template('admin_admins.html', username=current_user.username, admins=admins)


@login_required
@admin_required
def admin_rooms_edit(id):
    form = AdminRoomsForm()
    room = Rooms.query.filter_by(id=id).first()
    if not room:
        return redirect(url_for('admin_rooms'))
    if form.validate_on_submit():
        room.id = form.id.data
        room.roomtype = form.roomtype.data
        room.roomnumber = form.roomnumber.data
        room.floor = form.floor.data
        room.hastv = form.hastv.data
        room.haswifi = form.haswifi.data
        room.hasminibar = form.hasminibar.data
        room.pricepernight = form.pricepernight.data
        room.capacity = form.capacity.data
        try:
            db.session.add(room)
            db.session.commit()
            flash("Успешно изменены данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_rooms_edit', id=id))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_rooms_edit', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_rooms_edit', id=id))
        return redirect(url_for('admin_rooms_edit', id=room.id))
    return render_template('admin_rooms_edit.html', username=current_user.username, form=form,
                           id=id, room=room)


@login_required
@admin_required
def admin_rooms_delete(id):
    room = Rooms.query.filter_by(id=id).first()
    if not room:
        return redirect(url_for('admin_rooms'))
    try:
        db.session.delete(room)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", 'danger')
        return redirect(url_for('admin_rooms_edit', id=room.id))
    return redirect(url_for('admin_rooms'))


@login_required
@admin_required
def admin_rooms_create():
    form = AdminRoomsForm()
    room = Rooms()
    if form.validate_on_submit():
        room.id = form.id.data
        room.roomtype = form.roomtype.data
        room.roomnumber = form.roomnumber.data
        room.floor = form.floor.data
        room.hastv = form.hastv.data
        room.haswifi = form.haswifi.data
        room.hasminibar = form.hasminibar.data
        room.pricepernight = form.pricepernight.data
        room.capacity = form.capacity.data
        try:
            db.session.add(room)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_rooms_create'))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_rooms_create'))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_rooms_create'))
        return redirect(url_for('admin_rooms_edit', id=room.id))
    return render_template('admin_rooms_create.html', username=current_user.username, form=form)


@login_required
@admin_required
def admin_users_edit(id):
    form = AdminUserForm()
    user = User.query.filter_by(id=id).first()
    if not user:
        return redirect(url_for('admin_users'))
    if form.validate_on_submit():
        user.id = form.id.data
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data
        user.phonenumber = form.phonenumber.data
        try:
            db.session.add(user)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_users_edit', id=id))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_users_edit', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_users_edit', id=id))
        return redirect(url_for('admin_users_edit', id=user.id))
    return render_template('admin_users_edit.html', username=current_user.username, form=form,
                           id=id, user=user)


@login_required
@admin_required
def admin_users_delete(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return redirect(url_for('admin_users'))
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", 'danger')
        return redirect(url_for('admin_users_edit', id=user.id))
    return redirect(url_for('admin_users'))


@login_required
@admin_required
def admin_users_create():
    form = AdminUserForm()
    user = User()
    if form.validate_on_submit():
        user.id = form.id.data
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data
        user.phonenumber = form.phonenumber.data
        try:
            db.session.add(user)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_users_create'))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_users_create'))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_users_create'))
        return redirect(url_for('admin_users_edit', id=user.id))
    return render_template('admin_users_create.html', username=current_user.username, form=form)


@login_required
@admin_required
def admin_admins_edit(id):
    form = AdminAdminsForm()
    admin = Admin.query.filter_by(id=id).first()
    if not admin:
        return redirect(url_for('admin_admins'))
    if form.validate_on_submit():
        admin.id = form.id.data
        admin.username = form.username.data
        admin.password = form.password.data
        try:
            db.session.add(admin)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_admins_edit', id=id))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_admins_edit', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_admins_edit', id=id))
        return redirect(url_for('admin_admins_edit', id=admin.id))
    return render_template('admin_admins_edit.html', username=current_user.username, form=form,
                           id=id, admin=admin)


@login_required
@admin_required
def admin_admins_delete(id):
    admin = Admin.query.filter_by(id=id).first()
    if not admin:
        return redirect(url_for('admin_admins'))
    try:
        db.session.delete(admin)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", 'danger')
        return redirect(url_for('admin_users_edit', id=admin.id))
    return redirect(url_for('admin_admins'))


@login_required
@admin_required
def admin_admins_create():
    form = AdminAdminsForm()
    admin = Admin()
    if form.validate_on_submit():
        admin.id = form.id.data
        admin.username = form.username.data
        admin.password = form.password.data
        try:
            db.session.add(admin)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_admins_create'))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_admins_create'))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_admins_create'))
        return redirect(url_for('admin_admins_edit', id=admin.id))
    return render_template('admin_admins_create.html', username=current_user.username, form=form)


@login_required
@admin_required
def admin_reviews_edit(id):
    form = AdminReviewsForm()
    review = Reviews.query.filter_by(id=id).first()
    if not review:
        return redirect(url_for('admin_reviews'))
    if form.validate_on_submit():
        review.id = form.id.data
        review.bookingid = form.bookingid.data
        review.rating = form.rating.data
        review.reviewtext = form.reviewtext.data
        try:
            db.session.add(review)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_reviews_edit', id=id))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_reviews_edit', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_reviews_edit', id=id))
        return redirect(url_for('admin_reviews_edit', id=review.id))
    return render_template('admin_reviews_edit.html', username=current_user.username, form=form,
                           id=id, review=review)


@login_required
@admin_required
def admin_reviews_delete(id):
    review = Reviews.query.filter_by(id=id).first()
    if not review:
        return redirect(url_for('admin_reviews'))
    try:
        db.session.delete(review)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", 'danger')
        return redirect(url_for('admin_reviews_edit', id=review.id))
    return redirect(url_for('admin_reviews'))


@login_required
@admin_required
def admin_reviews_create():
    form = AdminReviewsForm()
    review = Reviews()
    if form.validate_on_submit():
        review.id = form.id.data
        review.bookingid = form.bookingid.data
        review.rating = form.rating.data
        review.reviewtext = form.reviewtext.data
        try:
            db.session.add(review)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_reviews_create'))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_reviews_create'))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_reviews_create'))
        return redirect(url_for('admin_reviews_edit', id=review.id))
    return render_template('admin_reviews_create.html', username=current_user.username, form=form)


@login_required
@admin_required
def admin_bookings_edit(id):
    form = AdminBookingsForm()
    booking = Bookings.query.filter_by(id=id).first()
    if not booking:
        return redirect(url_for('admin_bookings'))
    nights = (booking.enddate - booking.startdate).days
    if form.validate_on_submit():
        booking.id = form.id.data
        booking.userid = form.userid.data
        booking.roomid = form.roomid.data
        booking.startdate = form.startdate.data
        booking.enddate = form.enddate.data
        booking.totalprice = form.totalprice.data
        try:
            db.session.add(booking)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_bookings_edit', id=id))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_bookings_edit', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_bookings_edit', id=id))
        return redirect(url_for('admin_bookings_edit', id=booking.id))
    return render_template('admin_bookings_edit.html', username=current_user.username,
                           form=form, id=id, booking=booking, nights=nights)


@login_required
@admin_required
def admin_bookings_delete(id):
    booking = Bookings.query.filter_by(id=id).first()
    if not booking:
        return redirect(url_for('admin_bookings'))
    try:
        db.session.delete(booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", 'danger')
        return redirect(url_for('admin_bookings_edit', id=booking.id))
    return redirect(url_for('admin_reviews'))


@login_required
@admin_required
def admin_bookings_create():
    form = AdminBookingsForm()
    booking = Bookings()
    if form.validate_on_submit():
        booking.id = form.id.data
        booking.userid = form.userid.data
        booking.roomid = form.roomid.data
        booking.startdate = form.startdate.data
        booking.enddate = form.enddate.data
        booking.totalprice = form.totalprice.data
        try:
            db.session.add(booking)
            db.session.commit()
            flash("Успешно созданы данные", 'success')
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_bookings_create'))
        except PendingRollbackError as e:
            db.session.rollback()
            flash(f"Ошибка бд:{str(e)}", 'danger')
            return redirect(url_for('admin_bookings_create'))
        except Exception as e:
            db.session.rollback()
            flash(f"Неизвестная ошибка: {str(e)}", 'danger')
            return redirect(url_for('admin_bookings_create'))
        return redirect(url_for('admin_bookings_edit', id=booking.id))
    return render_template('admin_bookings_create.html', username=current_user.username,
                           form=form)


def execute_sql_query(query):
    try:
        # Выполнение запроса
        result = db.session.execute(text(query))
        db.session.commit()

        if query.strip().lower().startswith('select'):
            return result.fetchall()
        else:
            return "Запрос выполнен успешно"
    except Exception as e:
        db.session.rollback()
        return str(e)


@login_required
@admin_required
def admin_query():
    result = None
    error = None
    if request.method == 'POST':
        sql_query = request.form['query']
        result = execute_sql_query(sql_query)
        if isinstance(result, str):
            # Если ошибка, показываем сообщение
            error = result
        else:
            # Форматируем результат для отображения
            result = '\n'.join(str(row) for row in result)
    return render_template('admin_query.html', username=current_user.username, result=result)


@login_required
@admin_required
def admin_search():
    table = request.args.get('table', 'rooms')  # По умолчанию таблица комнат
    form, results, columns = None, None, None

    # Определяем форму и модель на основе выбранной таблицы
    if table == 'rooms':
        form = AdminRoomsForm()
        model = Rooms
    elif table == 'users':
        form = AdminUserForm()
        model = User
    elif table == 'admins':
        form = AdminAdminsForm()
        model = Admin
    elif table == 'reviews':
        form = AdminReviewsForm()
        model = Reviews
    elif table == 'bookings':
        form = AdminBookingsForm()
        model = Bookings

    if form.is_submitted():
        query = model.query
        if form.id.data:
            query = query.filter_by(id=form.id.data)
        if table == 'rooms':
            if form.roomtype.data:
                query = query.filter(model.roomtype.ilike(f'%{form.roomtype.data}%'))
            if form.roomnumber.data:
                query = query.filter(model.roomnumber.ilike(f'%{form.roomnumber.data}%'))
            if form.floor.data:
                query = query.filter_by(floor=form.floor.data)
            if form.hastv.data is not None:
                query = query.filter_by(hastv=form.hastv.data)
            if form.haswifi.data is not None:
                query = query.filter_by(haswifi=form.haswifi.data)
            if form.hasminibar.data is not None:
                query = query.filter_by(hasminibar=form.hasminibar.data)
            if form.pricepernight.data:
                query = query.filter_by(pricepernight=form.pricepernight.data)
            if form.capacity.data:
                query = query.filter_by(capacity=form.capacity.data)

            # Для таблицы users
        elif table == 'users':
            if form.name.data:
                query = query.filter(model.name.ilike(f'%{form.name.data}%'))
            if form.email.data:
                query = query.filter(model.email.ilike(f'%{form.email.data}%'))
            if form.phonenumber.data:
                query = query.filter(model.phonenumber.ilike(f'%{form.phonenumber.data}%'))

            # Для таблицы admins
        elif table == 'admins':
            if form.username.data:
                query = query.filter(model.username.ilike(f'%{form.username.data}%'))

            # Для таблицы reviews
        elif table == 'reviews':
            if form.bookingid.data:
                query = query.filter_by(bookingid=form.bookingid.data)
            if form.rating.data:
                query = query.filter_by(rating=form.rating.data)
            if form.reviewtext.data:
                query = query.filter(model.reviewtext.ilike(f'%{form.reviewtext.data}%'))

            # Для таблицы bookings
        elif table == 'bookings':
            if form.userid.data:
                query = query.filter_by(userid=form.userid.data)
            if form.roomid.data:
                query = query.filter_by(roomid=form.roomid.data)
            if form.startdate.data:
                query = query.filter_by(startdate=form.startdate.data)
            if form.enddate.data:
                query = query.filter_by(enddate=form.enddate.data)
            if form.totalprice.data:
                query = query.filter_by(totalprice=form.totalprice.data)

        # (Добавьте дополнительные условия для других полей, как нужно
        results = query.all()
        columns = [column.name for column in model.__table__.columns]

    return render_template('admin_search.html', username=current_user.username, table=table,
                           results=results, form=form,
                           columns=columns)
