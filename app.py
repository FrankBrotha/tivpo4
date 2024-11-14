from flask import Flask, flash
from config import Config
from extensions import db, login_manager
from routes import admin_login, admin_dashboard, logout, login, home, dashboard, register, rooms, review, mybookings, \
    myreviews, bookroom, admin_dashboard, admin_users, admin_rooms, admin_bookings, admin_reviews, admin_admins, \
    admin_rooms_edit, admin_rooms_delete, admin_rooms_create, admin_users_create, admin_users_edit, admin_users_delete, \
    admin_admins_create, admin_admins_delete, admin_admins_edit, admin_reviews_edit, admin_reviews_create, \
    admin_reviews_delete, admin_bookings_delete, admin_bookings_create, admin_bookings_edit, admin_query, admin_search
from sqlalchemy.exc import IntegrityError, PendingRollbackError

app = Flask(__name__)
app.config.from_object(Config)

login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходима авторизация.'
db.init_app(app)

app.add_url_rule('/', view_func=home)
app.add_url_rule('/admin/login', view_func=admin_login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout)
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=dashboard)
app.add_url_rule('/rooms', view_func=rooms)
app.add_url_rule('/rooms/book/<string:roomnumber>', view_func=bookroom, methods=['GET', 'POST'])
app.add_url_rule('/mybookings/review/<int:bookid>', view_func=review, methods=['GET', 'POST'])
app.add_url_rule('/mybookings', view_func=mybookings)
app.add_url_rule('/myreviews', view_func=myreviews)
app.add_url_rule('/admin/dashboard', view_func=admin_dashboard)
app.add_url_rule('/admin/users', view_func=admin_users)
app.add_url_rule('/admin/rooms', view_func=admin_rooms)
app.add_url_rule('/admin/bookings', view_func=admin_bookings)
app.add_url_rule('/admin/reviews', view_func=admin_reviews)
app.add_url_rule('/admin/admins', view_func=admin_admins)
app.add_url_rule('/admin/rooms/edit/<int:id>', view_func=admin_rooms_edit, methods=['GET', 'POST'])
app.add_url_rule('/admin/rooms/delete/<int:id>', view_func=admin_rooms_delete, methods=['GET', 'POST'])
app.add_url_rule('/admin/rooms/create', view_func=admin_rooms_create, methods=['GET', 'POST'])

app.add_url_rule('/admin/users/edit/<int:id>', view_func=admin_users_edit, methods=['GET', 'POST'])
app.add_url_rule('/admin/users/delete/<int:id>', view_func=admin_users_delete, methods=['GET', 'POST'])
app.add_url_rule('/admin/users/create', view_func=admin_users_create, methods=['GET', 'POST'])
app.add_url_rule('/admin/admins/edit/<int:id>', view_func=admin_admins_edit, methods=['GET', 'POST'])
app.add_url_rule('/admin/admins/delete/<int:id>', view_func=admin_admins_delete, methods=['GET', 'POST'])
app.add_url_rule('/admin/admins/create', view_func=admin_admins_create, methods=['GET', 'POST'])

app.add_url_rule('/admin/reviews/edit/<int:id>', view_func=admin_reviews_edit, methods=['GET', 'POST'])
app.add_url_rule('/admin/reviews/delete/<int:id>', view_func=admin_reviews_delete, methods=['GET', 'POST'])
app.add_url_rule('/admin/reviews/create', view_func=admin_reviews_create, methods=['GET', 'POST'])

app.add_url_rule('/admin/bookings/edit/<int:id>', view_func=admin_bookings_edit, methods=['GET', 'POST'])
app.add_url_rule('/admin/bookings/delete/<int:id>', view_func=admin_bookings_delete, methods=['GET', 'POST'])
app.add_url_rule('/admin/bookings/create', view_func=admin_bookings_create, methods=['GET', 'POST'])

app.add_url_rule('/admin/query', view_func=admin_query, methods=['GET', 'POST'])
app.add_url_rule('/admin/search', view_func=admin_search, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
