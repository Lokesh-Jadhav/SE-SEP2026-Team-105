from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import (
    User,
    StudentProfile,
    MentorProfile,
    Match,
    Message,
    Availability,
    Meeting,
    Feedback,
    Goal
)

app = create_app()


def utc_now():
    return datetime.now(timezone.utc)


def days_from_now(days, hour=10):
    date = utc_now() + timedelta(days=days)
    return date.replace(hour=hour, minute=0, second=0, microsecond=0)


with app.app_context():
    db.drop_all()
    db.create_all()

    # ---------------- Admin ----------------
    admin = User(
        email="admin@mentorbridge.com",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        profile_completed=True
    )
    db.session.add(admin)

    # ---------------- Students ----------------
    student_users = []

    student_data = [
        {
            "email": "ahmed@student.com",
            "password": "student123",
            "full_name": "Ahmed Rahman",
            "university": "Dalhousie University",
            "goal": "masters",
            "desired_job_title": "",
            "target_country": "Canada",
            "target_degree": "MSc Computer Science",
            "field_of_interest": "Machine Learning",
            "questions": "How should I prepare applications for Canadian CS master's programs?",
            "status": "approved"
        },
        {
            "email": "sara@student.com",
            "password": "student123",
            "full_name": "Sara Ahmed",
            "university": "Saint Mary's University",
            "goal": "job",
            "desired_job_title": "Software Engineer",
            "target_country": "Canada",
            "target_degree": "",
            "field_of_interest": "Software Engineering",
            "questions": "What projects should I build to get a junior software engineering job?",
            "status": "approved"
        },
        {
            "email": "james@student.com",
            "password": "student123",
            "full_name": "James Miller",
            "university": "Dalhousie University",
            "goal": "both",
            "desired_job_title": "Data Scientist",
            "target_country": "Canada",
            "target_degree": "MSc Data Science",
            "field_of_interest": "Data Science",
            "questions": "Should I apply for jobs first or pursue a master's degree?",
            "status": "approved"
        },
        {
            "email": "priya@student.com",
            "password": "student123",
            "full_name": "Priya Sharma",
            "university": "University of Toronto",
            "goal": "masters",
            "desired_job_title": "",
            "target_country": "Canada",
            "target_degree": "MASc Electrical and Computer Engineering",
            "field_of_interest": "Machine Learning",
            "questions": "How important are research publications for master's admissions?",
            "status": "pending"
        }
    ]

    for item in student_data:
        user = User(
            email=item["email"],
            password_hash=generate_password_hash(item["password"]),
            role="student",
            profile_completed=True
        )

        profile = StudentProfile(
            user=user,
            full_name=item["full_name"],
            university=item["university"],
            goal=item["goal"],
            desired_job_title=item["desired_job_title"],
            target_country=item["target_country"],
            target_degree=item["target_degree"],
            field_of_interest=item["field_of_interest"],
            questions=item["questions"],
            status=item["status"]
        )

        db.session.add(user)
        db.session.add(profile)
        student_users.append(user)

    # ---------------- Mentors ----------------
    mentor_users = []

    mentor_data = [
        {
            "email": "ali@mentor.com",
            "password": "mentor123",
            "full_name": "Ali Khan",
            "current_status": "studying_abroad",
            "university": "University of Toronto",
            "country": "Canada",
            "degree": "MSc Applied Computing",
            "job_title": "",
            "company": "",
            "expertise": "Machine Learning, Masters in Canada, Graduate Applications",
            "bio": "Currently pursuing a master's degree in Canada and helping students with graduate applications.",
            "status": "approved",
            "available": True
        },
        {
            "email": "emma@mentor.com",
            "password": "mentor123",
            "full_name": "Emma Wilson",
            "current_status": "working",
            "university": "Dalhousie University",
            "country": "Canada",
            "degree": "BSc Computer Science",
            "job_title": "Software Engineer",
            "company": "Shopify",
            "expertise": "Software Engineering, Software Engineer, Career Advice, Technical Interviews",
            "bio": "Software engineer helping students prepare for junior developer roles and interviews.",
            "status": "approved",
            "available": True
        },
        {
            "email": "david@mentor.com",
            "password": "mentor123",
            "full_name": "David Chen",
            "current_status": "working",
            "university": "University of Waterloo",
            "country": "Canada",
            "degree": "MSc Data Science",
            "job_title": "Data Scientist",
            "company": "RBC",
            "expertise": "Data Science, Machine Learning, Data Scientist, Career Transition",
            "bio": "Data scientist with experience in banking, analytics, and machine-learning projects.",
            "status": "approved",
            "available": True
        },
        {
            "email": "fatima@mentor.com",
            "password": "mentor123",
            "full_name": "Fatima Noor",
            "current_status": "studying_abroad",
            "university": "McGill University",
            "country": "Canada",
            "degree": "MEng Electrical and Computer Engineering",
            "job_title": "",
            "company": "",
            "expertise": "Electrical Engineering, Masters in Canada, Research Applications",
            "bio": "Graduate student helping students apply to engineering programs in Canada.",
            "status": "approved",
            "available": True
        },
        {
            "email": "omar@mentor.com",
            "password": "mentor123",
            "full_name": "Omar Hassan",
            "current_status": "working",
            "university": "University of British Columbia",
            "country": "Canada",
            "degree": "BSc Computer Science",
            "job_title": "Machine Learning Engineer",
            "company": "Telus",
            "expertise": "Machine Learning, Machine Learning Engineer, Python, Deep Learning",
            "bio": "Machine-learning engineer helping students enter AI and ML roles.",
            "status": "pending",
            "available": True
        }
    ]

    for item in mentor_data:
        user = User(
            email=item["email"],
            password_hash=generate_password_hash(item["password"]),
            role="mentor",
            profile_completed=True
        )

        profile = MentorProfile(
            user=user,
            full_name=item["full_name"],
            current_status=item["current_status"],
            university=item["university"],
            country=item["country"],
            degree=item["degree"],
            job_title=item["job_title"],
            company=item["company"],
            expertise=item["expertise"],
            bio=item["bio"],
            status=item["status"],
            available=item["available"]
        )

        db.session.add(user)
        db.session.add(profile)
        mentor_users.append(user)

    db.session.commit()

    ahmed = student_users[0]
    sara = student_users[1]
    james = student_users[2]
    priya = student_users[3]

    ali = mentor_users[0]
    emma = mentor_users[1]
    david = mentor_users[2]
    fatima = mentor_users[3]

    # ---------------- Active match: Ahmed <-> Ali ----------------
    active_match = Match(
        student_id=ahmed.id,
        mentor_id=ali.id,
        status="active"
    )
    db.session.add(active_match)
    db.session.flush()

    # Message statuses:
    # sent = no delivered_at or read_at
    # delivered = delivered_at set, read_at empty
    # read = both delivered_at and read_at set
    db.session.add_all([
        Message(
            match_id=active_match.id,
            sender_id=ali.id,
            body="Hi Ahmed, welcome! I reviewed your profile. What specific master's programs are you targeting?",
            created_at=utc_now() - timedelta(minutes=90),
            delivered_at=utc_now() - timedelta(minutes=88),
            read_at=utc_now() - timedelta(minutes=80)
        ),
        Message(
            match_id=active_match.id,
            sender_id=ahmed.id,
            body="Hi Ali, thank you! I am mainly targeting MSc Computer Science programs in Canada.",
            created_at=utc_now() - timedelta(minutes=75),
            delivered_at=utc_now() - timedelta(minutes=73)
        ),
        Message(
            match_id=active_match.id,
            sender_id=ali.id,
            body="That is a good target. Focus on your statement of purpose, recommendation letters, and a strong research or project portfolio.",
            created_at=utc_now() - timedelta(minutes=60)
        )
    ])

    # ---------------- Mentorship goals ----------------
    db.session.add_all([
        Goal(
            match_id=active_match.id,
            created_by_id=ali.id,
            title="Finalize CV",
            description="Update your CV with research projects, technical skills, and relevant coursework.",
            due_date=(utc_now() + timedelta(days=7)).date(),
            completed=True,
            completed_at=utc_now() - timedelta(days=1)
        ),
        Goal(
            match_id=active_match.id,
            created_by_id=ali.id,
            title="Shortlist 10 master's programs",
            description="Create a spreadsheet with deadlines, admission requirements, and funding options.",
            due_date=(utc_now() + timedelta(days=14)).date(),
            completed=False
        ),
        Goal(
            match_id=active_match.id,
            created_by_id=ali.id,
            title="Draft statement of purpose",
            description="Write a first draft explaining your academic background, research interests, and career goals.",
            due_date=(utc_now() + timedelta(days=21)).date(),
            completed=False
        )
    ])

    # ---------------- Mentor availability ----------------
    availability_slots = []

    availability_data = [
        (ali, days_from_now(2, 15), days_from_now(2, 16)),
        (ali, days_from_now(4, 18), days_from_now(4, 19)),
        (emma, days_from_now(1, 14), days_from_now(1, 15)),
        (david, days_from_now(3, 11), days_from_now(3, 12)),
        (fatima, days_from_now(5, 16), days_from_now(5, 17))
    ]

    for mentor, start, end in availability_data:
        slot = Availability(
            mentor_id=mentor.id,
            start_time=start,
            end_time=end
        )
        db.session.add(slot)
        availability_slots.append(slot)

    db.session.flush()

    # ---------------- Pending meeting request ----------------
    pending_meeting = Meeting(
        match_id=active_match.id,
        availability_id=availability_slots[0].id,
        student_id=ahmed.id,
        mentor_id=ali.id,
        status="pending"
    )
    db.session.add(pending_meeting)

    # ---------------- Ended mentorship with feedback ----------------
    ended_match = Match(
        student_id=sara.id,
        mentor_id=emma.id,
        status="ended",
        student_end_requested=True,
        mentor_end_requested=True,
        created_at=utc_now() - timedelta(days=30),
        ended_at=utc_now() - timedelta(days=2)
    )
    db.session.add(ended_match)
    db.session.flush()

    db.session.add_all([
        Message(
            match_id=ended_match.id,
            sender_id=emma.id,
            body="Hi Sara, I reviewed your resume. Let's focus on building two strong full-stack projects.",
            created_at=utc_now() - timedelta(days=25),
            delivered_at=utc_now() - timedelta(days=25),
            read_at=utc_now() - timedelta(days=24)
        ),
        Message(
            match_id=ended_match.id,
            sender_id=sara.id,
            body="Thank you! I will start with a React and Flask project this week.",
            created_at=utc_now() - timedelta(days=24),
            delivered_at=utc_now() - timedelta(days=24),
            read_at=utc_now() - timedelta(days=23)
        )
    ])

    db.session.add_all([
        Goal(
            match_id=ended_match.id,
            created_by_id=emma.id,
            title="Build a full-stack project",
            description="Create a React and Flask application with authentication and a database.",
            due_date=(utc_now() - timedelta(days=10)).date(),
            completed=True,
            completed_at=utc_now() - timedelta(days=11)
        ),
        Goal(
            match_id=ended_match.id,
            created_by_id=emma.id,
            title="Complete mock technical interview",
            description="Practice data structures, algorithms, and behavioral questions.",
            due_date=(utc_now() - timedelta(days=5)).date(),
            completed=True,
            completed_at=utc_now() - timedelta(days=6)
        )
    ])

    db.session.add_all([
        Feedback(
            match_id=ended_match.id,
            user_id=sara.id,
            rating=5,
            comments="Emma gave very practical advice about projects and interview preparation."
        ),
        Feedback(
            match_id=ended_match.id,
            user_id=emma.id,
            rating=4,
            comments="Sara was engaged and asked thoughtful questions."
        )
    ])

    db.session.commit()

    print("Database seeded successfully.")
    print("\nLogin accounts:")
    print("Admin:  admin@mentorbridge.com / admin123")
    print("\nStudents:")
    for user in student_users:
        print(f"  {user.email} / student123")
    print("\nMentors:")
    for user in mentor_users:
        print(f"  {user.email} / mentor123")