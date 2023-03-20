from flask import jsonify
from flask_login import login_required
from flask_restful import abort, Resource

from . import db_session
from .tags import Tags
from .reqparse import add_tag_parser, edit_tag_parser


def abort_if_tag_not_found(tag_id):
    session = db_session.create_session()
    tag = session.query(Tags).get(tag_id)
    if not tag:
        abort(404, message=f"Project {tag_id} not found")


class TagsResource(Resource):
    def get(self, tag_id):
        abort_if_tag_not_found(tag_id)
        session = db_session.create_session()
        tag = session.query(Tags).get(tag_id)
        return jsonify({'tag': tag.to_dict(only=('id', 'tag'))})

    @login_required
    def delete(self, tag_id):
        abort_if_tag_not_found(tag_id)
        session = db_session.create_session()
        tag = session.query(Tags).get(tag_id)
        session.delete(tag)
        session.commit()
        return jsonify({'success': 'OK'})

    @login_required
    def post(self, tag_id):
        abort_if_tag_not_found(tag_id)
        args = edit_tag_parser.parse_args()
        session = db_session.create_session()
        session.query(Tags).filter(Tags.id == tag_id).update({k: v for k, v in args.items() if v is not None})
        session.commit()
        return jsonify({'success': 'OK'})


class TagsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tags = session.query(Tags).all()
        return jsonify({'tags': [tag.to_dict(only=('id', 'tag')) for tag in tags]})

    @login_required
    def post(self):
        args = add_tag_parser.parse_args()
        session = db_session.create_session()
        tag = Tags(**{k: v for k, v in args.items() if v is not None})
        session.add(tag)
        session.commit()
        return jsonify({'success': 'OK'})
