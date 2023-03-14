import flask
from flask import request, jsonify

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint('jobs_api', __name__, template_folder='templates')


@blueprint.route('/api/jobs')
def get_news():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {'jobs': [job.to_dict(only=('id', 'team_leader', 'job', 'work_size', 'collaborators',
                                    'start_date', 'end_date', 'is_finished')) for job in jobs]})


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_news(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).get(job_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify({'jobs': jobs.to_dict(only=('id', 'team_leader', 'job', 'work_size', 'collaborators',
                                               'start_date', 'end_date', 'is_finished'))})


@blueprint.route('/api/jobs', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    if 'id' in request.json:
        if request.json['id'] in tuple(job.id for job in db_sess.query(Jobs).all()):
            return jsonify({'error': 'Id already exists'})

    jobs = Jobs(**request.json)
    db_sess.add(jobs)
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
