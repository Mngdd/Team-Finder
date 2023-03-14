from flask import Flask, render_template, redirect, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.users import User
from data.project import Project
from data import db_session, project_api
from forms.user import RegisterForm, LoginForm, ProjectForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/team_finder.db")
    app.register_blueprint(project_api.blueprint)
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()
    users = db_sess.query(User).all()
    names = {user.id: user.nickname for user in users}
    return render_template("index.html", projects=projects, names=names)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="User already exists")
        user = User()
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.github_profile = form.github_profile.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        project = Project()
        project.team_leader = current_user.id
        project.title = form.title.data
        project.description = form.description.data
        project.collaborators = form.collaborators.data
        db_sess.add(project)
        db_sess.commit()
        return redirect('/')
    return render_template('add_project.html', title='Add project', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()