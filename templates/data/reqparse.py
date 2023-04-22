from flask_restful import reqparse

add_user_parser = reqparse.RequestParser()
add_user_parser.add_argument('nickname', required=True)
add_user_parser.add_argument('email', required=True)
add_user_parser.add_argument('password', required=True)
add_user_parser.add_argument('projects')

edit_user_parser = reqparse.RequestParser()
edit_user_parser.add_argument('nickname')
edit_user_parser.add_argument('email')
edit_user_parser.add_argument('password')
edit_user_parser.add_argument('projects')

add_project_parser = reqparse.RequestParser()
add_project_parser.add_argument('team_leader', required=True, type=int)
add_project_parser.add_argument('title', required=True)
add_project_parser.add_argument('description', required=True)
add_project_parser.add_argument('image')
add_project_parser.add_argument('location')
add_project_parser.add_argument('collaborators')
add_project_parser.add_argument('archived', type=bool)
add_project_parser.add_argument('tags')

edit_project_parser = reqparse.RequestParser()
edit_project_parser.add_argument('team_leader', type=int)
edit_project_parser.add_argument('title')
edit_project_parser.add_argument('description')
edit_project_parser.add_argument('image')
add_project_parser.add_argument('location')
edit_project_parser.add_argument('collaborators')
edit_project_parser.add_argument('archived', type=bool)
edit_project_parser.add_argument('tags')

add_tag_parser = reqparse.RequestParser()
add_tag_parser.add_argument('tag', required=True)

edit_tag_parser = reqparse.RequestParser()
edit_tag_parser.add_argument('tag')
