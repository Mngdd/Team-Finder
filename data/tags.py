import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


projects_to_tags = sqlalchemy.Table(
    'projects_to_tags',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('project_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('projects.id'), primary_key=True),
    sqlalchemy.Column('tag_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('tags.id'), primary_key=True)
)


class Tags(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tags'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tag = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)

    def __repr__(self):
        return f'<Tag> {self.id}'

    def get_projects(self):
        return ' '.join(str(project.id) for project in self.projects)
