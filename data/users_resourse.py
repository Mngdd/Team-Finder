import datetime
from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .users import User
from .project import Project
from .reqparse import add_user_parser, edit_user_parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('id', 'nickname', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def post(self, user_id):  # edit user
        abort_if_user_not_found(user_id)
        args = edit_user_parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if args['email']:
            if session.query(User).filter(User.email == args['email'], User.id != user.id).first():
                abort(400, message=f"User with email {args['email']} already exists")
        if args['password']:
            user.set_password(args['password'])
        if args['projects']:
            for project_id in map(int, args['projects'].split()):
                if project_id > 0:
                    user.projects.append(session.query(Project).get(project_id))
                else:
                    user.projects.remove(session.query(Project).get(-project_id))
        if any(v is not None for k, v in args.items() if k not in ('password', 'projects')):
            session.query(User).filter(User.id == user_id).update({k: v for k, v in args.items() if k not in
                                                                   ('password', 'projects') and v is not None})
        user.modified_date = datetime.datetime.now()
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'email')) for user in users]})

    def post(self):  # add user
        args = add_user_parser.parse_args()
        session = db_session.create_session()
        if session.query(User).filter(User.email == args['email']).first():
            abort(400, message=f"User with email {args['email']} already exists")
        user = User(**{k: v for k, v in args.items() if k not in ('password', 'projects') and v is not None})
        user.set_password(args['password'])
        if args['projects']:
            for project_id in map(int, args['projects'].split()):
                user.projects.append(session.query(Project).get(project_id))
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
