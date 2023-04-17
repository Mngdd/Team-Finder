import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


projects_to_users = sqlalchemy.Table(
    'projects_to_users',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('project_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('projects.id'), primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True)
)


class Project(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    archived = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    users = orm.relationship("User")
    collaborators = orm.relationship("User", secondary="projects_to_users", backref="projects")
    tags = orm.relationship("Tags", secondary="projects_to_tags", backref="projects")

    def __repr__(self):
        return f'<Project> {self.id}'

    def get_collaborators(self):
        return ' '.join(str(user.id) for user in self.collaborators)

    def get_tags(self):
        return ' '.join(str(tag.id) for tag in self.tags)
