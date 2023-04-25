from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .tags import Tags
from .reqparse import add_tag_parser, edit_tag_parser


def abort_if_tag_not_found(tag_id):
    session = db_session.create_session()
    tag = session.query(Tags).get(tag_id)
    session.close()
    if not tag:
        abort(404, message=f"Project {tag_id} not found")


class TagsResource(Resource):
    def get(self, tag_id):
        abort_if_tag_not_found(tag_id)
        session = db_session.create_session()
        tag = session.query(Tags).get(tag_id)
        session.close()
        return jsonify({'tag': tag.to_dict(only=('id', 'tag'))})

    def delete(self, tag_id):
        abort_if_tag_not_found(tag_id)
        session = db_session.create_session()
        tag = session.query(Tags).get(tag_id)
        session.delete(tag)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def post(self, tag_id):
        abort_if_tag_not_found(tag_id)
        args = edit_tag_parser.parse_args()
        session = db_session.create_session()
        if args['tags']:
            if session.query(Tags).filter(Tags.tag == args['tag']).first():
                abort(400, message=f"Tag {args['tag']} already exists")
        session.query(Tags).filter(Tags.id == tag_id).update({k: v for k, v in args.items() if v is not None})
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class TagsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tags = session.query(Tags).all()
        session.close()
        return jsonify({'tags': [tag.to_dict(only=('id', 'tag')) for tag in tags]})

    def post(self):
        args = add_tag_parser.parse_args()
        session = db_session.create_session()
        if session.query(Tags).filter(Tags.tag == args['tag']).first():
            abort(400, message=f"Tag {args['tag']} already exists")
        tag = Tags(**{k: v for k, v in args.items() if v is not None})
        session.add(tag)
        session.commit()
        tag_id = tag.id
        session.close()
        return jsonify({'success': 'OK', 'id': tag_id})  # returns id for further use
