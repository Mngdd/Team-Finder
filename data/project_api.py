import flask
from flask import request, jsonify

from . import db_session
from .project import Project

blueprint = flask.Blueprint('project_api', __name__, template_folder='templates')


@blueprint.route('/api/projects')
def get_projects():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()
    return jsonify(
        {'projects': [project.to_dict(only=('id', 'team_leader', 'title', 'description', 'link', 'collaborators',
                                            'is_finished')) for project in projects]})


@blueprint.route('/api/projects/<int:project_id>', methods=['GET'])
def get_one_project(project_id):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).get(project_id)
    if not project:
        return jsonify({'error': 'Not found'})
    return jsonify({'project': project.to_dict(only=('id', 'team_leader', 'title', 'description', 'link',
                                                     'collaborators', 'is_finished'))})


@blueprint.route('/api/projects', methods=['POST'])
def create_project():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader', 'title', 'description', 'link', 'collaborators', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    if 'id' in request.json:
        if request.json['id'] in tuple(project.id for project in db_sess.query(Project).all()):
            return jsonify({'error': 'Id already exists'})

    project = Project(**request.json)
    db_sess.add(project)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# @blueprint.route('/api/news/<int:news_id>', methods=['DELETE'])
# def delete_news(news_id):
#     db_sess = db_session.create_session()
#     news = db_sess.query(News).get(news_id)
#     if not news:
#         return jsonify({'error': 'Not found'})
#     db_sess.delete(news)
#     db_sess.commit()
#     return jsonify({'success': 'OK'})
