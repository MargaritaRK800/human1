from flask import Flask
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/my_db.sqlite")
    session = db_session.create_session()

    user = User()
    user.surname = "Scott"
    user.name = "Ridley"
    user.age = 21
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"

    user = User()
    user.surname = "What"
    user.name = "Am"
    user.age = 1
    user.position = "doing"
    user.speciality = "on"
    user.address = "Mars"
    user.email = "help_me@mars.org"

    user = User()
    user.surname = "Perley"
    user.name = "Jack"
    user.age = 23
    user.position = "regular engineer"
    user.speciality = "engineer"
    user.address = "section_4_3"
    user.email = "Perley_Jack@mars.org"

    user = User()
    user.surname = "Servey"
    user.name = "Scott"
    user.age = 27
    user.position = "captain_advisor"
    user.speciality = "researcher"
    user.address = "main_section"
    user.email = "Servey_Scott@mars.org"

    session.commit()


if __name__ == '__main__':
    main()