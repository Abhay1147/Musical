from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from models import db, Student, Production, Role, RoleAssignment, CrewAssignment, TeamMember, Song, Thanks
from werkzeug.utils import secure_filename
import os, csv

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}
view_bp = Blueprint('view', __name__)
edit_bp = Blueprint('edit', __name__)

@view_bp.before_request
def create_tables():
    db.create_all()

def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def import_students_from_csv(filepath):
    try:
        with open(filepath, 'r') as f:
            for row in csv.DictReader(f):
                if not Student.query.filter_by(name=row['name']).first():
                    db.session.add(Student(name=row['name'], sex=row.get('sex', ''), year=row.get('year', '')))
        db.session.commit()
    except FileNotFoundError:
        pass


# VIEWER ROUTES
@view_bp.route('/')
def home():
    return render_template('home.jinja')


@view_bp.route('/viewer')
def viewer_home():
    prods = Production.query.order_by(Production.title).all()
    return render_template('viewer.jinja', productions=prods)


@view_bp.route('/viewer/production/<int:production_id>')
def viewer_production(production_id):
    prod = Production.query.get_or_404(production_id)
    roles = Role.query.filter_by(production_id=prod.id).order_by(Role.is_group, Role.name).all()
    cast = [{'role': r.name, 'students': [a.student.full_name() for a in r.assignments]} for r in roles]
    crew = CrewAssignment.query.filter_by(production_id=prod.id).all()
    team = TeamMember.query.filter_by(production_id=prod.id).all()
    songs = Song.query.filter_by(production_id=prod.id).order_by(Song.act, Song.title).all()
    thanks = Thanks.query.filter_by(production_id=prod.id).all()
    return render_template('viewer_production.jinja', production=prod, cast=cast, crew=crew, team=team, songs=songs, thanks=thanks)


# DIRECTOR ROUTES
@view_bp.route('/director')
def director_home():
    prods = Production.query.order_by(Production.title).all()
    return render_template('production.jinja', production=None, productions=prods)


@view_bp.route('/view/production/<int:production_id>')
def view_production(production_id):
    prod = Production.query.get_or_404(production_id)
    roles = Role.query.filter_by(production_id=prod.id).order_by(Role.is_group, Role.name).all()
    cast = [{'role': r.name, 'students': [a.student.full_name() for a in r.assignments]} for r in roles]
    crew = CrewAssignment.query.filter_by(production_id=prod.id).all()
    team = TeamMember.query.filter_by(production_id=prod.id).all()
    songs = Song.query.filter_by(production_id=prod.id).order_by(Song.act, Song.title).all()
    thanks = Thanks.query.filter_by(production_id=prod.id).all()
    return render_template('production.jinja', production=prod, cast=cast, crew=crew, team=team, songs=songs, thanks=thanks, productions=Production.query.order_by(Production.title).all())


@view_bp.route('/view/production/<int:production_id>/cast')
def view_cast(production_id):
    prod = Production.query.get_or_404(production_id)
    roles = Role.query.filter_by(production_id=prod.id).order_by(Role.is_group, Role.name).all()
    cast = [{'id': r.id, 'role': r.name, 'students': [a.student.full_name() for a in r.assignments]} for r in roles]
    students = sorted(Student.query.all(), key=lambda s: s.name)
    return render_template('cast.jinja', production=prod, cast=cast, students=students)


@view_bp.route('/view/production/<int:production_id>/crew')
def view_crew(production_id):
    prod = Production.query.get_or_404(production_id)
    crew = CrewAssignment.query.filter_by(production_id=prod.id).all()
    students = sorted(Student.query.all(), key=lambda s: s.name)
    return render_template('crew.jinja', production=prod, crew=crew, students=students)


@view_bp.route('/view/production/<int:production_id>/songs')
def view_songs(production_id):
    prod = Production.query.get_or_404(production_id)
    songs = Song.query.filter_by(production_id=prod.id).order_by(Song.act, Song.title).all()
    return render_template('songs.jinja', production=prod, songs=songs)


@view_bp.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'static/uploads'), filename)


# EDIT ROUTES
@edit_bp.route('/create_production', methods=['POST'])
def create_production():
    title = request.form.get('title', '').strip()
    if not title:
        flash('Title required', 'error')
        return redirect(url_for('view.director_home'))
    p = Production(title=title, subtitle=request.form.get('subtitle', ''), location=request.form.get('location', ''),
                   price=request.form.get('price', ''), copyright=request.form.get('copyright', ''),
                   notes=request.form.get('notes', ''), dates_text=request.form.get('dates', ''))
    file = request.files.get('cover')
    if file and allowed_file(file.filename):
        fname = secure_filename(file.filename)
        os.makedirs(os.path.join(current_app.root_path, 'static/uploads'), exist_ok=True)
        file.save(os.path.join(current_app.root_path, 'static/uploads', fname))
        p.cover_filename = f'/uploads/{fname}'
    db.session.add(p)
    db.session.commit()
    flash('Production created', 'success')
    return redirect(url_for('view.view_production', production_id=p.id))


@edit_bp.route('/production/<int:production_id>/edit', methods=['GET', 'POST'])
def edit_production(production_id):
    p = Production.query.get_or_404(production_id)
    if request.method == 'POST':
        p.title = request.form.get('title', p.title)
        p.subtitle = request.form.get('subtitle', '')
        p.location = request.form.get('location', '')
        p.price = request.form.get('price', '')
        p.copyright = request.form.get('copyright', '')
        p.notes = request.form.get('notes', '')
        p.dates_text = request.form.get('dates', '')
        file = request.files.get('cover')
        if file and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            os.makedirs(os.path.join(current_app.root_path, 'static/uploads'), exist_ok=True)
            file.save(os.path.join(current_app.root_path, 'static/uploads', fname))
            p.cover_filename = f'/uploads/{fname}'
        db.session.commit()
        flash('Production updated', 'success')
        return redirect(url_for('view.view_production', production_id=p.id))
    return render_template('production_edit.jinja', production=p)


@edit_bp.route('/production/<int:production_id>/delete', methods=['POST'])
def delete_production(production_id):
    p = Production.query.get_or_404(production_id)
    try:
        Thanks.query.filter_by(production_id=production_id).delete()
    except:
        pass
    db.session.delete(p)
    db.session.commit()
    flash('Production deleted', 'success')
    return redirect(url_for('view.director_home'))


@edit_bp.route('/production/<int:production_id>/cast', methods=['POST'])
def add_role_assignment(production_id):
    student_id = request.form.get('student_id')
    role_name = request.form.get('role', '').strip()
    is_group = bool(request.form.get('is_group'))
    if not role_name or not student_id:
        flash('Role and student required', 'error')
        return redirect(url_for('view.view_cast', production_id=production_id))
    role = Role.query.filter_by(production_id=production_id, name=role_name, is_group=is_group).first()
    if not role:
        role = Role(production_id=production_id, name=role_name, is_group=is_group)
        db.session.add(role)
        db.session.flush()
    assign = RoleAssignment(role_id=role.id, student_id=int(student_id))
    db.session.add(assign)
    db.session.commit()
    flash('Assigned', 'success')
    return redirect(url_for('view.view_cast', production_id=production_id))


@edit_bp.route('/role_assignment/<int:assign_id>/delete', methods=['POST'])
def delete_role_assignment(assign_id):
    ra = RoleAssignment.query.get_or_404(assign_id)
    pid = ra.role.production_id
    db.session.delete(ra)
    db.session.commit()
    flash('Removed', 'success')
    return redirect(url_for('view.view_cast', production_id=pid))


@edit_bp.route('/production/<int:production_id>/crew', methods=['POST'])
def add_crew(production_id):
    student_id = request.form.get('student_id')
    if not student_id:
        flash('Student required', 'error')
        return redirect(url_for('view.view_crew', production_id=production_id))
    ca = CrewAssignment(production_id=production_id, student_id=int(student_id), 
                        responsibility=request.form.get('responsibility', 'Crew'))
    db.session.add(ca)
    db.session.commit()
    flash('Crew added', 'success')
    return redirect(url_for('view.view_crew', production_id=production_id))


@edit_bp.route('/crew/<int:crew_id>/delete', methods=['POST'])
def delete_crew(crew_id):
    c = CrewAssignment.query.get_or_404(crew_id)
    pid = c.production_id
    db.session.delete(c)
    db.session.commit()
    flash('Removed', 'success')
    return redirect(url_for('view.view_crew', production_id=pid))


@edit_bp.route('/production/<int:production_id>/songs', methods=['POST'])
def add_song(production_id):
    title = request.form.get('title', '').strip()
    if not title:
        flash('Title required', 'error')
        return redirect(url_for('view.view_songs', production_id=production_id))
    s = Song(production_id=production_id, title=title, performers_text=request.form.get('performers', ''),
             act=int(request.form.get('act', 1)))
    db.session.add(s)
    db.session.commit()
    flash('Song added', 'success')
    return redirect(url_for('view.view_songs', production_id=production_id))


@edit_bp.route('/song/<int:song_id>/edit', methods=['POST'])
def edit_song(song_id):
    s = Song.query.get_or_404(song_id)
    s.title = request.form.get('title', s.title)
    s.performers_text = request.form.get('performers', '')
    s.act = int(request.form.get('act', s.act))
    db.session.commit()
    flash('Updated', 'success')
    return redirect(url_for('view.view_songs', production_id=s.production_id))


@edit_bp.route('/song/<int:song_id>/delete', methods=['POST'])
def delete_song(song_id):
    s = Song.query.get_or_404(song_id)
    pid = s.production_id
    db.session.delete(s)
    db.session.commit()
    flash('Removed', 'success')
    return redirect(url_for('view.view_songs', production_id=pid))


@edit_bp.route('/production/<int:production_id>/team', methods=['POST'])
def add_team(production_id):
    name = request.form.get('name', '').strip()
    position = request.form.get('position', '').strip()
    if not name or not position:
        flash('Name and position required', 'error')
        return redirect(url_for('view.view_production', production_id=production_id))
    tm = TeamMember(production_id=production_id, name=name, position=position)
    db.session.add(tm)
    db.session.commit()
    flash('Added', 'success')
    return redirect(url_for('view.view_production', production_id=production_id))


@edit_bp.route('/team/<int:tm_id>/delete', methods=['POST'])
def delete_team(tm_id):
    t = TeamMember.query.get_or_404(tm_id)
    pid = t.production_id
    db.session.delete(t)
    db.session.commit()
    flash('Removed', 'success')
    return redirect(url_for('view.view_production', production_id=pid))


@edit_bp.route('/production/<int:production_id>/thanks', methods=['POST'])
def add_thanks(production_id):
    text = request.form.get('text', '').strip()
    if not text:
        flash('Text required', 'error')
        return redirect(url_for('view.view_production', production_id=production_id))
    t = Thanks(production_id=production_id, text=text)
    db.session.add(t)
    db.session.commit()
    flash('Added', 'success')
    return redirect(url_for('view.view_production', production_id=production_id))


@edit_bp.route('/thanks/<int:thanks_id>/delete', methods=['POST'])
def delete_thanks(thanks_id):
    t = Thanks.query.get_or_404(thanks_id)
    pid = t.production_id
    db.session.delete(t)
    db.session.commit()
    flash('Removed', 'success')
    return redirect(url_for('view.view_production', production_id=pid))


@edit_bp.route('/import_students', methods=['POST'])
def import_students():
    file = request.files.get('file')
    if not file or file.filename.split('.')[-1].lower() != 'csv':
        flash('CSV file required', 'error')
        return redirect(url_for('view.director_home'))
    filepath = os.path.join(current_app.root_path, 'static/uploads', secure_filename(file.filename))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    import_students_from_csv(filepath)
    flash('Students imported', 'success')
    return redirect(url_for('view.director_home'))