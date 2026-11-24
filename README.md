# MentorBridge

**A student mentoring and career support platform for the IITM BS Degree community.**

![Project Status](https://img.shields.io/badge/status-in%20development-orange)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![Vue.js](https://img.shields.io/badge/Vue.js-Frontend-4FC08D?logo=vuedotjs)

## Overview

MentorBridge is a mentoring and career support platform designed to connect current IITM BS students with experienced graduates and alumni.

Students can communicate their career interests, goals and mentoring needs. Mentors can share their professional backgrounds and areas of expertise, while administrators oversee profiles, approvals and mentoring assignments.

The project is developed as part of the **IIT Madras BS Degree – Software Engineering course (September 2026 term)**, based on **Problem Statement 2: Student Mentoring and Career Support Platform**.

## Key Features

The following features describe the platform's intended functionality. Implementation and integration are being developed incrementally across the project sprints.

### Student

- Register and create a student profile with career interests and goals.
- View profile approval status and assigned mentor.
- Communicate with an assigned mentor through chat.
- View mentor availability and request meetings.
- Track mentor-assigned goals and progress.
- Submit feedback and review previous mentorships.

### Mentor

- Register and create a professional profile.
- Specify professional background, qualifications and areas of expertise.
- Manage availability for new mentees.
- Communicate with assigned students.
- Publish availability and manage meeting requests.
- Create goals for mentees and track their progress.
- Submit feedback and manage mentorship completion.

### Administrator

- Review and approve or reject student and mentor profiles.
- View platform activity and dashboard metrics.
- Generate ranked mentor recommendations for eligible students.
- Assign mentors based on matching results and availability.
- Review submitted feedback and manage user accounts.

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| Database | SQLite, Flask-SQLAlchemy |
| Authentication | JWT, Werkzeug password hashing |
| Frontend | Vue 3, JavaScript |
| Frontend state management | Pinia |
| Frontend routing | Vue Router |
| HTTP requests | Axios |
| Frontend tooling | Vite, npm |
| Cross-origin requests | Flask-CORS |
| Testing | pytest |

## Architecture

MentorBridge follows a frontend–backend architecture.

- **Frontend:** Vue.js application containing the user interface, routing, authentication state and reusable components.
- **Backend:** Flask application exposing API routes and handling application logic.
- **Database:** SQLite database managed through Flask-SQLAlchemy.
- **Authentication:** JWT-based authentication with role-specific application access.

The backend organizes API functionality into separate route modules for authentication, profiles, administration, matching, chat and goals.

The frontend communicates with the backend through HTTP requests using Axios.

## Project Structure

```text
MentorBridge/
├── README.md
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── goals.py
│   │   │   ├── matching.py
│   │   │   └── profiles.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_smoke.py
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── AvailabilityCalendar.vue
    │   │   ├── ChatPanel.vue
    │   │   ├── DashboardPanel.vue
    │   │   ├── FeedbackForm.vue
    │   │   ├── GoalsPanel.vue
    │   │   └── ProfileFields.vue
    │   ├── router/
    │   │   └── index.js
    │   ├── stores/
    │   │   └── auth.js
    │   ├── views/
    │   │   ├── AdminDashboard.vue
    │   │   ├── FeedbackView.vue
    │   │   ├── LandingView.vue
    │   │   ├── LoginView.vue
    │   │   ├── MentorDashboard.vue
    │   │   ├── ProfileSetupView.vue
    │   │   ├── RegisterView.vue
    │   │   └── StudentDashboard.vue
    │   ├── api.js
    │   ├── App.vue
    │   ├── main.js
    │   ├── style.css
    │   └── utils.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Getting Started

### Prerequisites

Ensure the following are installed:

- Python 3
- pip
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone <repository-url>
cd MentorBridge
```

### 2. Set up the backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment.

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

Run the database seeding script:

```bash
python seed.py
```

This creates the database and populates it with sample users and demonstration data.

> **Note:** The seed script drops and recreates existing database tables. Running it again will reset the local database and erase its current data. Use it only for local development and demonstration purposes.

### 4. Start the backend

```bash
python run.py
```

The Flask development server runs at:

```text
http://127.0.0.1:5000
```

### 5. Set up the frontend

Open a separate terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser. The default Vite development address is usually:

```text
http://localhost:5173
```

### 6. Access the API Documentation

The API documentation can be accessed using:

```text
http://localhost:5000/docs
```

## Demo Accounts

The database seeding script creates sample accounts for testing the application.

| Role | Email | Password | Seeded profile status |
|---|---|---|---|
| Administrator | admin@mentorbridge.com | admin123 | — |
| Student | ahmed@student.com | student123 | Approved |
| Student | sara@student.com | student123 | Approved |
| Student | james@student.com | student123 | Approved |
| Student | priya@student.com | student123 | Pending |
| Mentor | ali@mentor.com | mentor123 | Approved |
| Mentor | emma@mentor.com | mentor123 | Approved |
| Mentor | david@mentor.com | mentor123 | Approved |
| Mentor | fatima@mentor.com | mentor123 | Approved |
| Mentor | omar@mentor.com | mentor123 | Pending |

These are demonstration credentials for local development only. Do not use them in a production deployment.

## API Documentation

The backend API is organized into the following registered route modules:

| Module | Base path |
|---|---|
| Authentication | `/api/auth` |
| Profiles | `/api/profiles` |
| Administration | `/api/admin` |
| Matching | `/api/matching` |
| Chat | `/api/chat` |
| Goals | `/api/goals` |

API endpoint documentation and the Swagger-compatible OpenAPI specification are being developed alongside the sprint implementation.

## Database Design

The application uses SQLite with Flask-SQLAlchemy for database management.

The current data model includes the following entities:

- `User`
- `StudentProfile`
- `MentorProfile`
- `Match`
- `Message`
- `Availability`
- `Meeting`
- `Feedback`
- `Goal`

The database tables are created through the Flask application setup. The `seed.py` script populates the local database with demonstration accounts and related sample records.

## Testing

The backend uses **pytest** for automated testing.

### Test structure

Test configuration and test cases are maintained in:

```text
backend/
└── tests/
    ├── conftest.py
    └── test_smoke.py
```

The test configuration uses a temporary SQLite database for test execution, keeping test data separate from the local development database.

### Running tests

The backend uses **pytest** for automated testing.

From the backend directory, run:

```bash
python -m pytest -v
```

To save test output in a file using PowerShell:

```powershell
python -m pytest -v --color=yes 2>&1 | Tee-Object -FilePath test-results.txt -Append
```

Test cases are maintained in the `backend/tests/` directory.

### Current test coverage

The initial smoke test verifies that the backend health-check route (`GET /`) responds successfully and returns the expected JSON status.

API-specific test coverage for the selected user stories is being expanded during the current sprint. Test cases will document inputs, expected outputs, actual outputs and results.

## Development Progress

MentorBridge is being developed through the project milestones and two API implementation sprints.

| Phase | Timeline | Focus |
|---|---|---|
| Milestone 1 | Oct 18 – Oct 25 | User identification, requirements and user stories |
| Milestone 2 | Oct 26 – Nov 07 | Scheduling, storyboarding, wireframes, database and frontend design |
| Sprint 1 (Milestone 3) | Nov 08 – Nov 22 | API implementation and testing for User Stories 1, 3, 6 and 7 |
| Sprint 2 (Milestone 4) | Nov 23 – Dec 06 | Feedback incorporation and API implementation and testing for User Stories 2, 4, 5 and 8 |
| Final Submission (Milestone 5) | Dec 07 – Dec 20 | Final working prototype and project reporting |

### Current sprint scope

The current API implementation and testing work focuses on:

- **User Story 1:** Student profile creation.
- **User Story 3:** Mentor profile creation.
- **User Story 6:** Verification of mentor profiles.
- **User Story 7:** Management of user accounts.

The API implementation, Swagger documentation and pytest coverage will be updated as these deliverables progress.

## Team

**IIT Madras BS – Software Engineering Project, Team 105**

<!-- | Contributor | Role / Contribution | LinkedIn | Email |
|---|---|---|---|
| Arnav | [Contribution] | [LinkedIn URL] | [Email] |
| Lokesh | [Contribution] | [LinkedIn URL] | [Email] |
| Lovepreet | [Contribution] | [LinkedIn URL] | [Email] |
| Mohit | [Contribution] | [LinkedIn URL] | [Email] |
| Mayank | [Contribution] | [LinkedIn URL] | [Email] | -->

## Acknowledgements

Developed as part of the IIT Madras BS Degree Programme, Software Engineering course (September 2026 term).