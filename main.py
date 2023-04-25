import os

from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from requests import get, post, delete

from data import db_session, users_resourse, projects_resourse, tags_resourse
from data.users import User
from forms.user import RegisterForm, LoginForm, ProjectForm, FilterForm

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


def transform_project_data(project):  # Transforms project data into useful info
    names = {user['id']: user['nickname'] for user in
             get(f'http://{request.host}/api/users').json()['users']}
    tags = {tag['id']: tag['tag'] for tag in get(f'http://{request.host}/api/tags').json()['tags']}
    project['team_leader'] = int(project['team_leader'])
    project['team_leader_name'] = names[project['team_leader']]
    project['collaborators'] = list(map(int, project['collaborators'].split()))
    project['collaborators_names'] = [names[user_id] for user_id in project['collaborators']]
    project['tags'] = list(map(int, project['tags'].split()))
    project['tags_str'] = [tags[tag_id] for tag_id in project['tags']]


def get_project(project_id=None):  # Returns usable info about project(s)
    if project_id is not None:
        project = get(f'http://{request.host}/api/projects/{project_id}').json()['project']
        transform_project_data(project)
        return project
    projects = get(f'http://{request.host}/api/projects').json()['projects']
    for project in projects:
        transform_project_data(project)
    return projects


def get_filename(filename):  # get filename for projects with duplicate names
    images = tuple(project['image'] for project in get_project() if project['image'] is not None)
    n = 0
    while f'./static/img/{filename}_{n}.jpg' in images:
        n += 1
    return f'./static/img/{filename}_{n}.jpg'


def get_location_image(ll, spn, filename):  # write location image
    params = {
        'll': ll,
        'spn': spn,
        'pt': f'{ll},pm2bll',  # set marker on exact location
        'l': 'map'
    }
    map_request = 'http://static-maps.yandex.ru/1.x/'
    response = get(map_request, params=params)

    if response:
        with open(filename, 'wb') as f:
            f.write(response.content)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():  # Main page displays available projects and search/filter form
    form = FilterForm()
    form.tags.choices = [(int(tag['id']), tag['tag']) for tag in
                         get(f'http://{request.host}/api/tags').json()['tags']]
    projects = [project for project in get_project() if not project['archived']]
    if form.validate_on_submit():
        if 'clear' not in request.form:
            if form.tags.data:
                projects = [project for project in projects if any(tag in project['tags'] for tag in form.tags.data)]
            if form.search.data:
                try:  # оказывается поле поиска сохраняется, и если у нас поиск выдает 0 резов, оно может упасть
                    projects = [project for project in projects if
                                any(form.search.data.lower().strip() in
                                    (project[k].lower() if isinstance(project[k], str)
                                     else list(map(lambda x: x.lower(), project[k]))) for k in
                                    ('team_leader_name', 'title', 'description', 'collaborators_names', 'tags_str'))]
                except AttributeError:  # ниче страшного
                        ...
        else:
            form.tags.data = None
            form.search.data = ''
            form.show_all.data = False
    return render_template("index.html", title='Team Finder', projects=projects, form=form)


@app.route('/projects/<nickname>/<status>')
@login_required
def user_projects(nickname, status):  # Displays created, collaborative and archived projects
    if nickname != current_user.nickname or status not in ('created', 'collaborative', 'archived'):
        return redirect('/')
    if status == 'created':
        projects = [project for project in get_project()
                    if project['team_leader'] == current_user.id and not project['archived']]
    elif status == 'collaborative':
        projects = [project for project in get_project()
                    if current_user.id in project['collaborators'] and not project['archived']]
    else:
        projects = [project for project in get_project()
                    if project['team_leader'] == current_user.id and project['archived']]
    return render_template("user_projects.html", title='My projects', projects=projects)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Passwords don't match")
        res = post(f'http://{request.host}/api/users',
                   json={'email': form.email.data,
                         'password': form.password.data,
                         'nickname': form.nickname.data}).json()
        if res.get('message', False):
            return render_template('register.html', title='Register', form=form, message=res['message'])
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
        return render_template('login.html', title='Log in', message="Incorrect login or password", form=form)
    return render_template('login.html', title='Log in', form=form)


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    form.tags.choices = [(int(tag['id']), tag['tag']) for tag in
                         get(f'http://{request.host}/api/tags').json()['tags']]
    if form.validate_on_submit():
        additional_tags = []
        if form.additional_tags.data:  # add tags by user
            for tag in form.additional_tags.data.split(', '):
                res = post(f'http://{request.host}/api/tags', json={'tag': tag}).json()
                if res.get('message', False):
                    return render_template('add_project.html', title='Add project', form=form, message=res['message'])
                additional_tags.append(res['id'])
        res_json = {'team_leader': current_user.id,
                    'title': form.title.data,
                    'description': form.description.data,
                    'tags': ' '.join(map(str, form.tags.data + additional_tags)),
                    'location': form.location.data}
        if form.image.data:
            filename = get_filename("_".join(form.title.data.strip().split()).lower())
            with open(filename, 'wb') as f:
                f.write(form.image.data.read())
            res_json['image'] = filename
        res = post(f'http://{request.host}/api/projects', json=res_json).json()
        if res.get('message', False):
            return render_template('add_project.html', title='Add project', form=form, message=res['message'])
        return redirect('/')
    return render_template('add_project.html', title='Add project', action='Add', form=form, remove_image=False)


@app.route('/project/<project_id>')
def project_page(project_id):  # Detailed info + actions
    project = get_project(project_id)
    loc_image = None
    if project.get('ll', False) and project.get('spn', False):
        loc_image = './static/img/location.png'
        get_location_image(project['ll'], project['spn'], loc_image)
    return render_template('project.html', title=f'Project {project_id}', project=project, loc_image=loc_image)


@app.route('/edit_project/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    form = ProjectForm()
    form.tags.choices = [(int(tag['id']), tag['tag']) for tag in
                         get(f'http://{request.host}/api/tags').json()['tags']]
    project = get_project(project_id)
    if request.method == "GET":  # restore project data
        form.title.data = project['title']
        form.description.data = project['description']
        form.location.data = project['location']
        form.tags.data = project['tags']
    if form.validate_on_submit():
        additional_tags = []
        if form.additional_tags.data:  # add tags by user
            for tag in form.additional_tags.data.split(', '):
                res = post(f'http://{request.host}/api/tags', json={'tag': tag}).json()
                if res.get('message', False):
                    return render_template('add_project.html', title='Edit project', form=form, message=res['message'])
                additional_tags.append(res['id'])
        res_json = {'title': form.title.data,
                    'description': form.description.data,
                    'tags': ' '.join(map(str, form.tags.data + additional_tags)),
                    'location': form.location.data}
        if form.no_location.data:
            res_json['location'] = 'no location'
        if form.remove_image.data:
            res_json['image'] = ''
            os.remove(project['image'])
        elif form.image.data:  # to avoid pointless file writing
            if project['image']:  # overwrite image file if it already exists
                filename = project['image']
            else:
                filename = get_filename("_".join(form.title.data.strip().split()).lower())
            with open(filename, 'wb') as f:
                f.write(form.image.data.read())
            res_json['image'] = filename
        res = post(f'http://{request.host}/api/projects/{project_id}', json=res_json).json()
        if res.get('message', False):
            return render_template('add_project.html', title='Edit project', form=form, message=res['message'])
        return redirect(f'/project/{project_id}')
    return render_template('add_project.html', title='Edit project', action='Edit',
                           form=form, remove_image=project['image'])


@app.route('/delete_project/<project_id>')
@login_required
def delete_project(project_id):
    res = delete(f'http://{request.host}/api/projects/{project_id}').json()
    if os.path.isfile(res['image']):
        os.remove(res['image'])
    return redirect(url_for('index'))


@app.route('/leave_project/<project_id>')
@login_required
def leave_project(project_id):
    post(f'http://{request.host}/api/projects/{project_id}',
         json={'collaborators': str(-current_user.id)})
    return redirect(f'/project/{project_id}')


@app.route('/collaborate/<project_id>')
@login_required
def collaborate(project_id):
    post(f'http://{request.host}/api/projects/{project_id}',
         json={'collaborators': str(current_user.id)})
    return redirect(f'/project/{project_id}')


@app.route('/archive_project/<project_id>')
@login_required
def archive(project_id):
    archived = get_project(project_id)['archived']
    post(f'http://{request.host}/api/projects/{project_id}',
         json={'archived': not archived})
    return redirect(f'/project/{project_id}')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    main()
