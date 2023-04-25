from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .project import Project
from .tags import Tags
from .users import User
from .reqparse import add_project_parser, edit_project_parser
from maps_api.geocoder import geocode, get_ll_span


def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    session.close()
    if not project:
        abort(404, message=f"Project {project_id} not found")


class ProjectsResource(Resource):
    def get(self, project_id):
        abort_if_project_not_found(project_id)
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        project_json = project.to_dict(only=('id', 'team_leader', 'title', 'description',
                                             'image', 'archived', 'location', 'll', 'spn'))
        project_json['collaborators'] = project.get_collaborators()
        project_json['tags'] = project.get_tags()
        session.close()
        return jsonify({'project': project_json})

    def delete(self, project_id):
        abort_if_project_not_found(project_id)
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        image = project.image
        session.delete(project)
        session.commit()
        session.close()
        return jsonify({'success': 'OK', 'image': image})

    def post(self, project_id):
        """Edit a project
        Collaborators are edited in or out one by one, tags are updated as a whole."""
        abort_if_project_not_found(project_id)
        args = edit_project_parser.parse_args()
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if args['collaborators']:
            for user_id in map(int, args['collaborators'].split()):
                if user_id > 0:
                    project.collaborators.append(session.query(User).get(user_id))
                else:
                    project.collaborators.remove(session.query(User).get(-user_id))
        if args['tags']:
            project.tags = [session.query(Tags).get(tag_id) for tag_id in map(int, args['tags'].split())]
        try:
            ll, spn = get_ll_span(args['location'])
            location = geocode(args['location'])['metaDataProperty']['GeocoderMetaData']['text']
            if args['location']:
                project.ll = ll
                project.spn = spn
                project.location = location
            else:
                project.ll, project.spn, project.location = None, None, None
        except RuntimeError:
            project.ll, project.spn, project.location = None, None, None
        if any(v is not None for k, v in args.items() if k not in ('collaborators', 'tags')):
            session.query(Project).filter(Project.id == project_id).update({k: v for k, v in args.items()
                                                                            if v is not None and k not in
                                                                            ('collaborators', 'tags', 'location')})
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Project).all()
        projects_list = []
        for project in projects:
            project_json = project.to_dict(only=('id', 'team_leader', 'title',
                                                 'description', 'image', 'archived', 'location', 'll', 'spn'))
            project_json['collaborators'] = project.get_collaborators()
            project_json['tags'] = project.get_tags()
            projects_list.append(project_json)
        session.close()
        return jsonify({'projects': projects_list})

    def post(self):
        args = add_project_parser.parse_args()
        session = db_session.create_session()
        project = Project(**{k: v for k, v in args.items() if v is not None
                             and k not in ('collaborators', 'tags', 'location')})
        if args['collaborators']:
            for user_id in map(int, args['collaborators'].split()):
                project.collaborators.append(session.query(User).get(user_id))
        if args['tags']:
            project.tags = [session.query(Tags).get(tag_id) for tag_id in map(int, args['tags'].split())]
        if args['location']:
            project.ll, project.spn = get_ll_span(args['location'])
        session.add(project)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
