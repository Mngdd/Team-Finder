from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from requests import get, post, delete
from wtforms import SelectMultipleField

from data import db_session, users_resourse, projects_resourse, tags_resourse
from data.users import User
from forms.user import RegisterForm, LoginForm, ProjectForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app, catch_all_404s=True)
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/team_finder.db")
    api.add_resource(users_resourse.UsersListResource, '/api/users')
    api.add_resource(users_resourse.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(projects_resourse.ProjectsListResource, '/api/projects')
    api.add_resource(projects_resourse.ProjectsResource, '/api/projects/<int:project_id>')
    api.add_resource(tags_resourse.TagsListResource, '/api/tags')
    api.add_resource(tags_resourse.TagsResource, '/api/tags/<int:tag_id>')
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():  # Main page displays available projects
    projects = get('http://127.0.0.1:5000/api/projects').json()['projects']
    names = {user['id']: user['nickname'] for user in get('http://127.0.0.1:5000/api/users').json()['users']}
    tags = {tag['id']: tag['tag'] for tag in get('http://127.0.0.1:5000/api/tags').json()['tags']}
    for project in projects:
        project['team_leader'] = names[project['team_leader']]
        project['collaborators'] = ', '.join(names[int(user_id)] for user_id in project['collaborators'].split())
        project['tags'] = ', '.join(tags[int(tag_id)] for tag_id in project['tags'].split())
    return render_template("index.html", projects=projects)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Passwords don't match")
        if post('http://127.0.0.1:5000/api/users',
                json={'email': form.email.data,
                      'password': form.password.data,
                      'nickname': form.nickname.data}).json().get('message', False):
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="User already exists")
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():  # flask_login wouldn't let make it the RESTful way
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
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    form.tags.choices = [(tag['id'], tag['tag']) for tag in
                         get('http://127.0.0.1:5000/api/tags').json()['tags']]
    if form.validate_on_submit():
        print(form.tags.data)
        # if post('http://127.0.0.1:5000/api/projects',
        #         json={'team_leader': current_user.id,
        #               'title': form.title.data,
        #               'description': form.description.data,
        #               'tags': form.tags.data}).json().get('message', False):
        #     return render_template('register.html', title='Add project',
        #                            form=form,
        #                            message="Error")
        return redirect('/')
    return render_template('add_project.html', title='Add project', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
