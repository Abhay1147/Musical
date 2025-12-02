#!/usr/bin/env python
# seed_mermaid.py
"""Seed the database with The Little Mermaid production data."""

from models import Production, Role, RoleAssignment, Student, CrewAssignment, TeamMember, Song, Thanks

def seed_mermaid(app, db):
    """Populate the database with The Little Mermaid production."""
    
    with app.app_context():
        # Check if production already exists
        existing = Production.query.filter_by(title="The Little Mermaid").first()
        if existing:
            print("The Little Mermaid production already exists. Skipping seed.")
            return
        
        # Create production
        prod = Production(
            title="The Little Mermaid",
            subtitle="Disney's",
            location="School Auditorium",
            price="$10-$15",
            copyright="Disney Theatrical Productions",
            notes="Video/audio recording strictly prohibited. Licensed through MTI.",
            dates_text="TBD"
        )
        db.session.add(prod)
        db.session.flush()
        prod_id = prod.id
        
        # Create/get students from cast list
        cast_data = {
            "Ariel": "Tristan Kuhse",
            "Prince Eric": "Josiah Gearhart",
            "Sebastian": "Tytus Stansbery",
            "Ursula": "Sylvia Sims",
            "King Triton": "Gabe Stansbery",
            "Flounder": "Jackson Zywiec",
            "Scuttle": "Brody Grove",
            "Grimsby": "Esten Moellering",
            "Flotsam": "Trinity Starrett",
            "Jetsam": "Cora Steines",
            "Aquata (Mersister)": "Megan Tudahl",
            "Atina (Mersister)": "Adaleigh Gearhart",
            "Arista (Mersister)": "Kassie Tilleraas",
            "Alana (Mersister)": "Lydia Van Gelder",
            "Andrina (Mersister)": "Alexa Popenhagen",
            "Adela (Mersister)": "Emily Herman",
            "Pilot / Chef Louis": "Peyton Elliott",
            "Carlotta": "Emmaliyah Rohde",
            "Seahorse": "Amelia Pollock",
            "Corlinda Johnson": "Corlinda Johnson",
            "AJ Klusman": "AJ Klusman",
            "Payton Allan": "Payton Allan",
            "Annie Murray": "Annie Murray",
            "Cam Guyer": "Cam Guyer",
            "Jasper Durnan": "Jasper Durnan",
            "Josie Michael": "Josie Michael",
            "Aralyn Keller": "Aralyn Keller",
            "Faith Gable": "Faith Gable",
            "Chloe Wander": "Chloe Wander",
        }
        
        students_map = {}
        for role_name, actor_name in cast_data.items():
            s = Student.query.filter_by(name=actor_name).first()
            if not s:
                s = Student(name=actor_name, sex="", year="")
                db.session.add(s)
                db.session.flush()
            students_map[role_name] = s
        
        # Add main cast roles
        main_roles = [
            ("Ariel", False),
            ("Prince Eric", False),
            ("Sebastian", False),
            ("Ursula", False),
            ("King Triton", False),
            ("Flounder", False),
            ("Scuttle", False),
            ("Grimsby", False),
            ("Flotsam", False),
            ("Jetsam", False),
        ]
        
        for role_name, is_group in main_roles:
            role = Role(production_id=prod_id, name=role_name, is_group=is_group)
            db.session.add(role)
            db.session.flush()
            student = students_map.get(role_name)
            if student:
                assign = RoleAssignment(role_id=role.id, student_id=student.id)
                db.session.add(assign)
        
        # Add Mersisters as a group
        mersisters_role = Role(production_id=prod_id, name="Mersisters", is_group=True)
        db.session.add(mersisters_role)
        db.session.flush()
        for mersister_key in ["Aquata (Mersister)", "Atina (Mersister)", "Arista (Mersister)", 
                              "Alana (Mersister)", "Andrina (Mersister)", "Adela (Mersister)"]:
            student = students_map.get(mersister_key)
            if student:
                assign = RoleAssignment(role_id=mersisters_role.id, student_id=student.id)
                db.session.add(assign)
        
        # Add Gulls as a group
        gulls_role = Role(production_id=prod_id, name="Gulls", is_group=True)
        db.session.add(gulls_role)
        db.session.flush()
        for gull_name in ["Annie Murray", "Alexa Popenhagen", "AJ Klusman"]:
            student = students_map.get(gull_name)
            if student:
                assign = RoleAssignment(role_id=gulls_role.id, student_id=student.id)
                db.session.add(assign)
        
        # Add Sea Creature Ensemble as a group
        ensemble_role = Role(production_id=prod_id, name="Sea Creature Ensemble", is_group=True)
        db.session.add(ensemble_role)
        db.session.flush()
        for ensemble_member in ["Corlinda Johnson", "AJ Klusman", "Payton Allan", "Faith Gable", 
                                "Chloe Wander", "Amelia Pollock"]:
            student = students_map.get(ensemble_member)
            if student:
                assign = RoleAssignment(role_id=ensemble_role.id, student_id=student.id)
                db.session.add(assign)
        
        # Add crew
        crew_names = [
            "Leo Yauk", "Tarynn Harris", "Robert Huck", "Joslyn Kraft",
            "Timothy Eggers", "Alex Mohlis-Alloway", "Lucias Braun"
        ]
        for crew_name in crew_names:
            s = Student.query.filter_by(name=crew_name).first()
            if not s:
                s = Student(name=crew_name, sex="", year="")
                db.session.add(s)
                db.session.flush()
            ca = CrewAssignment(production_id=prod_id, student_id=s.id, responsibility="Stage Crew / Tech")
            db.session.add(ca)
        db.session.flush()
        
        # Add creative team
        team_data = [
            ("Bryan Wendt", "Musical Director"),
            ("Makinzie Dugger", "Drama Director"),
            ("Bergen Wendt", "Assistant Musical Director / Make-up Artist"),
            ("Lauren Falck", "Choreographer"),
            ("Kennedy Balk", "Choreographer"),
            ("Stephanie Herman", "Costuming Director"),
            ("Alex Snyder", "PAC / Tech Director"),
        ]
        for name, position in team_data:
            tm = TeamMember(production_id=prod_id, name=name, position=position)
            db.session.add(tm)
        db.session.flush()
        
        # Add songs
        songs_data = [
            # Act I
            (1, "The World Above", "Ariel"),
            (1, "Fathoms Below", "Prince Eric, Grimsby, Pilot, Sailors"),
            (1, "Daughters of Triton", "Mersisters"),
            (1, "If Only (Triton's Lament)", "Triton"),
            (1, "Daddy's Little Angel", "Ursula, Flotsam, Jetsam"),
            (1, "Part of Your World", "Ariel"),
            (1, "Part of Your World (Reprise)", "Ariel"),
            (1, "She's In Love", "Flounder, Mersisters"),
            (1, "Her Voice", "Prince Eric"),
            (1, "Under the Sea", "Sebastian, Sea Creatures"),
            (1, "If Only (Ariel's Lament)", "Ariel"),
            (1, "Sweet Child", "Flotsam, Jetsam"),
            (1, "Poor Unfortunate Souls", "Ursula"),
            # Act II
            (2, "Positoovity", "Scuttle, Sea Gulls"),
            (2, "Beyond My Wildest Dreams", "Ariel, Grimsby, Maids"),
            (2, "Les Poissons", "Chef Louis"),
            (2, "Les Poissons (Reprise)", "Chef Louis, Chefs"),
            (2, "One Step Closer", "Prince Eric"),
            (2, "Daddy's Little Angel (Reprise)", "Ursula, Flotsam, Jetsam"),
            (2, "Kiss the Girl", "Sebastian, Sea Creatures"),
            (2, "If Only (Quartet)", "Ariel, Prince Eric, Sebastian, King Triton"),
            (2, "The Contest", "Grimsby, Princesses"),
            (2, "Poor Unfortunate Souls (Reprise)", "Ursula"),
            (2, "Finale", "Ariel, Prince Eric, Triton, Ensemble"),
        ]
        
        for act, title, performers in songs_data:
            s = Song(production_id=prod_id, title=title, act=act, performers_text=performers)
            db.session.add(s)
        db.session.flush()
        
        # Add thanks/copyright
        thanks_data = [
            "Disney Theatrical Productions",
            "Video/audio recording strictly prohibited. Licensed through MTI.",
            "Special thanks to the cast, crew, and creative team!"
        ]
        for text in thanks_data:
            t = Thanks(production_id=prod_id, text=text)
            db.session.add(t)
        db.session.flush()
        
        db.session.commit()

if __name__ == '__main__':
    seed_mermaid()
