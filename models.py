# models.py
from app import db
from datetime import date

# Students (imported from CSV)
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10))
    year = db.Column(db.String(20))

    # convenience properties
    def full_name(self):
        return self.name or ""

    @property
    def last_name(self):
        if not self.name:
            return ""
        parts = self.name.strip().split()
        return parts[-1] if parts else ""

    def __repr__(self):
        return f"<Student {self.name}>"

# Productions (one production can have many roles, songs, etc.)
class Production(db.Model):
    __tablename__ = 'productions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    subtitle = db.Column(db.String(256))
    cover_filename = db.Column(db.String(256))  # path under static/uploads (relative)
    dates_text = db.Column(db.String(256))       # simple string: "Dec 1, Dec 2"
    location = db.Column(db.String(256))
    price = db.Column(db.String(64))
    copyright = db.Column(db.String(256))
    notes = db.Column(db.Text)

    roles = db.relationship('Role', backref='production', cascade='all, delete-orphan')
    songs = db.relationship('Song', backref='production', cascade='all, delete-orphan')
    team = db.relationship('TeamMember', backref='production', cascade='all, delete-orphan')
    crew = db.relationship('CrewAssignment', backref='production', cascade='all, delete-orphan')

# Roles (individual roles or grouped roles)
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    is_group = db.Column(db.Boolean, default=False)  # groups like "Ensemble"
    order_index = db.Column(db.Integer, default=0)

    assignments = db.relationship('RoleAssignment', backref='role', cascade='all, delete-orphan')

# Assignment table linking students to roles (many-to-many with extra row)
class RoleAssignment(db.Model):
    __tablename__ = 'role_assignments'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    student = db.relationship('Student')  # convenience

# Crew (student crew members)
class CrewAssignment(db.Model):
    __tablename__ = 'crew_assignments'
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    responsibility = db.Column(db.String(200))

    student = db.relationship('Student')

# Creative team (adults)
class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.String(256))

# Songs
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    act = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    performers_text = db.Column(db.String(512))

class Thanks(db.Model):
    __tablename__ = 'thanks'
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)