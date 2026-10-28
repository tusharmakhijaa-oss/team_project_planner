# Team Project Planner API

A lightweight project management API built with **Python and Django** to manage users, teams, project boards, and tasks using JSON-based file storage.

## Overview

The Team Project Planner provides a structured way to organize team members, create project boards, assign tasks to eligible team members, track task progress, and export board details. It uses JSON requests and responses, with application data stored locally in JSON files.

## Key Features

- **User Management:** Create, list, describe, and update users.
- **Team Management:** Create and update teams, manage memberships, and retrieve team members.
- **Project Boards:** Create boards, list open boards, and close completed boards.
- **Task Management:** Create tasks and update their statuses.
- **Board Export:** Export project board details to text files.
- **Validation:** Validate incoming request data and required fields.
- **Error Handling:** Handle invalid requests, missing resources, duplicate entries, and conflicting operations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Django | HTTP request handling and URL routing |
| JSON | Data persistence and API request/response format |
| Git | Version control |

## Design Decisions

The project was designed to prioritize simplicity, modularity, maintainability, and clear separation of responsibilities.

### 1. Django Framework

Django was selected because it provides URL routing, request processing, and HTTP response handling out of the box. It allows the application to expose API endpoints without introducing an additional API framework or unnecessary dependencies.

### 2. JSON-Based File Storage

JSON files were chosen to keep the project lightweight and easy to set up without requiring a separate database server. This approach is suitable for demonstrating CRUD operations and data handling in a small assignment.

Application data is stored in `db/`, while generated board exports are saved in `out/`.

### 3. Modular Architecture

User, team, and project board operations are organized into separate API modules. This keeps related functionality together and makes the code easier to read, test, maintain, and extend.

### 4. Base Classes

The supplied base classes are extended to preserve the required interfaces and separate the expected structure from the concrete implementations. This supports consistency across the different API modules.

### 5. Shared Validation and Error Handling

Common validation helpers check incoming JSON data and required fields. Custom exceptions represent errors such as invalid input, missing resources, duplicate entries, and conflicting operations.

This approach reduces repeated validation logic and helps keep error responses consistent.

### 6. Separate Storage and Export Directories

The `db/` and `out/` directories separate persistent application data from generated reports. The `.gitkeep` files preserve these directories in Git, while `.gitignore` excludes runtime data, generated exports, and local development files.

These choices prioritize simplicity, modularity, maintainability, and clear separation of responsibilities while meeting the project requirements.

## Project Structure

```text
team_project_planner/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── db/
│   └── .gitkeep
├── out/
│   └── .gitkeep
├── planner/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── api/
    ├── base/
    │   ├── user_base.py
    │   ├── team_base.py
    │   └── project_board_base.py
    ├── user_api.py
    ├── team_api.py
    ├── board_api.py
    ├── storage.py
    ├── validators.py
    ├── exceptions.py
    ├── utils.py
    ├── views.py
    └── urls.py
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip

### 1. Clone the repository

```bash
git clone <repository-url>
cd team_project_planner
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

On Windows:

```bash
env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the development server

```bash
python manage.py runserver
```

The application will be available at:

`http://127.0.0.1:8000/`

The API endpoints are available under `/api/`.

## API Endpoints

All API endpoints are prefixed with `/api/`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `users/create/` | Create a user |
| GET | `users/` | List users |
| POST | `users/describe/` | Retrieve user details |
| PUT/PATCH | `users/update/` | Update a user |
| POST | `users/teams/` | Retrieve a user's teams |
| POST | `teams/create/` | Create a team |
| GET | `teams/` | List teams |
| POST | `teams/describe/` | Retrieve team details |
| PUT/PATCH | `teams/update/` | Update a team |
| POST | `teams/users/add/` | Add team members |
| POST | `teams/users/remove/` | Remove team members |
| POST | `teams/users/` | List team members |
| POST | `boards/create/` | Create a project board |
| POST | `boards/close/` | Close a project board |
| POST | `boards/` | List open boards for a team |
| POST | `boards/export/` | Export board details |
| POST | `tasks/add/` | Create a task |
| PUT/PATCH | `tasks/status/` | Update task status |

## Postman API Testing — Sample Request and Response Data

**Base URL:** `http://127.0.0.1:8000`

> Note: The IDs and timestamps below are from a local test run. New IDs and timestamps will be generated when the application is run with fresh data.

### 1. Create Users

**Endpoint:** `POST /api/users/create/`

**DevOps Lead — Request**
```json
{
  "name": "devops_lead",
  "display_name": "Rahul Sharma"
}
```

**Response**
```json
{
  "id": "usr_3fd044fd818c47bfb2b24a49f8712f39"
}
```

**Backend Developer — Request**
```json
{
  "name": "backend_developer",
  "display_name": "Amit Patil"
}
```

**Response**
```json
{
  "id": "usr_5f544c2babd243bd883a31fef47fb49f"
}
```

**Frontend Developer — Request**
```json
{
  "name": "frontend_developer",
  "display_name": "Priya Deshmukh"
}
```

**Response**
```json
{
  "id": "usr_823da059f7864d509c1bc14b9235cbc1"
}
```

**QA Engineer — Request**
```json
{
  "name": "qa_engineer",
  "display_name": "Neha Joshi"
}
```

**Response**
```json
{
  "id": "usr_54b258e68edb4897b9673092898a777e"
}
```

**Cloud Engineer — Request**
```json
{
  "name": "cloud_engineer",
  "display_name": "Vikram Kulkarni"
}
```

**Response**
```json
{
  "id": "usr_ea9ee91b8ae74556bf899ee964495ced"
}
```

### 2. List Users

**Endpoint:** `GET /api/users/`

**Response**
```json
[
  {
    "name": "tushar",
    "display_name": "Tushar Developer",
    "creation_time": "2026-10-24T10:28:42.887276+00:00"
  },
  {
    "name": "sachin",
    "display_name": "sachin khade",
    "creation_time": "2026-10-24T11:58:08.657994+00:00"
  },
  {
    "name": "Sagar",
    "display_name": "Sagar senior MR",
    "creation_time": "2026-10-27T09:48:42.681647+00:00"
  },
  {
    "name": "devops_lead",
    "display_name": "Rahul Sharma",
    "creation_time": "2026-10-27T18:28:13.417907+00:00"
  },
  {
    "name": "backend_developer",
    "display_name": "Amit Patil",
    "creation_time": "2026-10-27T18:28:56.908047+00:00"
  },
  {
    "name": "frontend_developer",
    "display_name": "Priya Deshmukh",
    "creation_time": "2026-10-27T18:29:22.822717+00:00"
  },
  {
    "name": "qa_engineer",
    "display_name": "Neha Joshi",
    "creation_time": "2026-10-27T18:29:41.405775+00:00"
  },
  {
    "name": "cloud_engineer",
    "display_name": "Vikram Kulkarni",
    "creation_time": "2026-10-27T18:30:16.705601+00:00"
  }
]
```

### 3. Describe User

**Endpoint:** `POST /api/users/describe/`

**Request**
```json
{
  "id": "usr_ea9ee91b8ae74556bf899ee964495ced"
}
```

**Response**
```json
{
  "name": "cloud_engineer",
  "description": "Vikram Kulkarni",
  "creation_time": "2026-10-27T18:30:16.705601+00:00"
}
```

### 4. Update User

**Endpoint:** `PATCH /api/users/update/`

**Request**
```json
{
  "id": "usr_3fd044fd818c47bfb2b24a49f8712f39",
  "user": {
    "display_name": "Rahul Sharma - Senior DevOps Engineer"
  }
}
```

**Response**
```json
{
  "message": "User updated successfully."
}
```

### 5. Create Development Team

**Endpoint:** `POST /api/teams/create/`

**Request**
```json
{
  "name": "Development_Team",
  "description": "Core software development and application engineering team",
  "admin": "usr_3fd044fd818c47bfb2b24a49f8712f39"
}
```

**Response**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

### 6. Create DevOps Team

**Endpoint:** `POST /api/teams/create/`

**Request**
```json
{
  "name": "DevOps Team",
  "description": "CI/CD infrastructure cloud and deployment automation team",
  "admin": "usr_ea9ee91b8ae74556bf899ee964495ced"
}
```

**Response**
```json
{
  "id": "team_05157f46da2641839e7f0eae1287f378"
}
```

### 7. List Teams

**Endpoint:** `GET /api/teams/`

**Response**
```json
[
  {
    "name": "Development Team",
    "description": "Django project development",
    "creation_time": "2026-10-24T10:39:30.586203+00:00",
    "admin": "usr_842dafd4a08946eeb62c0187607ca669"
  },
  {
    "name": "Development Team 2",
    "description": "Django project development",
    "creation_time": "2026-10-24T12:03:49.711306+00:00",
    "admin": "usr_842dafd4a08946eeb62c0187607ca669"
  },
  {
    "name": "Development Team Updated",
    "description": "Backend and API development team",
    "creation_time": "2026-10-27T10:17:56.913350+00:00",
    "admin": "usr_a2dcb52313ca4c5f9095b8915db0e0f0"
  },
  {
    "name": "Development_Team",
    "description": "Core software development and application engineering team",
    "creation_time": "2026-10-27T18:35:09.369829+00:00",
    "admin": "usr_3fd044fd818c47bfb2b24a49f8712f39"
  },
  {
    "name": "DevOps Team",
    "description": "CI/CD infrastructure cloud and deployment automation team",
    "creation_time": "2026-10-27T18:36:33.270998+00:00",
    "admin": "usr_ea9ee91b8ae74556bf899ee964495ced"
  }
]
```

### 8. Describe Team

**Endpoint:** `POST /api/teams/describe/`

**Request**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

**Response**
```json
{
  "name": "Development_Team",
  "description": "Core software development and application engineering team",
  "creation_time": "2026-10-27T18:35:09.369829+00:00",
  "admin": "usr_3fd044fd818c47bfb2b24a49f8712f39"
}
```

### 9. Update Team

**Endpoint:** `PATCH /api/teams/update/`

**Request**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2",
  "team": {
    "name": "Application Development Team",
    "description": "Backend frontend and application development team",
    "admin": "usr_3fd044fd818c47bfb2b24a49f8712f39"
  }
}
```

**Response**
```json
{
  "message": "Team updated successfully."
}
```

### 10. Add Users to Team

**Endpoint:** `POST /api/teams/users/add/`

**Request**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2",
  "users": [
    "usr_5f544c2babd243bd883a31fef47fb49f",
    "usr_823da059f7864d509c1bc14b9235cbc1",
    "usr_54b258e68edb4897b9673092898a777e"
  ]
}
```

**Response**
```json
{
  "message": "Users added to team successfully.",
  "team_id": "team_650d65a8561148f3ac4513a899c9b6b2",
  "added_count": 3
}
```

### 11. List Team Members

**Endpoint:** `POST /api/teams/users/`

**Request**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

**Response**
```json
[
  {
    "id": "usr_3fd044fd818c47bfb2b24a49f8712f39",
    "name": "devops_lead",
    "display_name": "Rahul Sharma - Senior DevOps Engineer"
  },
  {
    "id": "usr_5f544c2babd243bd883a31fef47fb49f",
    "name": "backend_developer",
    "display_name": "Amit Patil"
  },
  {
    "id": "usr_823da059f7864d509c1bc14b9235cbc1",
    "name": "frontend_developer",
    "display_name": "Priya Deshmukh"
  },
  {
    "id": "usr_54b258e68edb4897b9673092898a777e",
    "name": "qa_engineer",
    "display_name": "Neha Joshi"
  }
]
```

### 12. Get Teams for a User

**Endpoint:** `POST /api/users/teams/`

**Request**
```json
{
  "id": "usr_5f544c2babd243bd883a31fef47fb49f"
}
```

**Response**
```json
[
  {
    "name": "Application Development Team",
    "description": "Backend frontend and application development team",
    "creation_time": "2026-10-27T18:35:09.369829+00:00"
  }
]
```

### 13. Create Application Development Board

**Endpoint:** `POST /api/boards/create/`

**Request**
```json
{
  "name": "Sprint 1 - Application Development",
  "description": "Sprint board for application development and testing",
  "team_id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

**Response**
```json
{
  "id": "board_845f303c3a8b4f0c8972c0533368a8e7"
}
```

### 14. Create DevOps Board

**Endpoint:** `POST /api/boards/create/`

**Request**
```json
{
  "name": "CI/CD Infrastructure",
  "description": "Board for deployment pipelines cloud infrastructure and automation",
  "team_id": "team_05157f46da2641839e7f0eae1287f378"
}
```

**Response**
```json
{
  "id": "board_f270294738e94852b45152e4ce928def"
}
```

### 15. List Boards for a Team

**Endpoint:** `POST /api/boards/`

**Request**
```json
{
  "team_id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

**Response**
```json
[
  {
    "id": "board_845f303c3a8b4f0c8972c0533368a8e7",
    "name": "Sprint 1 - Application Development"
  }
]
```

### 16. Add Authentication Task

**Endpoint:** `POST /api/tasks/add/`

**Request**
```json
{
  "board_id": "board_845f303c3a8b4f0c8972c0533368a8e7",
  "title": "Implement User Authentication API",
  "description": "Develop login registration and authentication APIs using Django",
  "user_id": "usr_5f544c2babd243bd883a31fef47fb49f"
}
```

**Response**
```json
{
  "id": "task_093d9c1ab5774081aab1251b2b61e729"
}
```

### 17. Add Frontend Dashboard Task

**Endpoint:** `POST /api/tasks/add/`

**Request**
```json
{
  "board_id": "board_845f303c3a8b4f0c8972c0533368a8e7",
  "title": "Develop Login Dashboard",
  "description": "Create responsive login and dashboard interface",
  "user_id": "usr_823da059f7864d509c1bc14b9235cbc1"
}
```

**Response**
```json
{
  "id": "task_80a0062bceb64c2587a257e074030240"
}
```

### 18. Add QA Testing Task

**Endpoint:** `POST /api/tasks/add/`

**Request**
```json
{
  "board_id": "board_845f303c3a8b4f0c8972c0533368a8e7",
  "title": "Test Authentication APIs",
  "description": "Perform functional validation and negative testing of authentication APIs",
  "user_id": "usr_54b258e68edb4897b9673092898a777e"
}
```

**Response**
```json
{
  "id": "task_de282ee7bca942979aa6b6d21d1b19d4"
}
```

### 19. Add CI/CD Pipeline Task

**Endpoint:** `POST /api/tasks/add/`

**Request**
```json
{
  "board_id": "board_f270294738e94852b45152e4ce928def",
  "title": "Configure CI/CD Pipeline",
  "description": "Create automated build test and deployment pipeline",
  "user_id": "usr_ea9ee91b8ae74556bf899ee964495ced"
}
```

**Response**
```json
{
  "id": "task_e9fb53471d84459295c68f7dc806e13d"
}
```

### 20. Update Task Status to In Progress

**Endpoint:** `PATCH /api/tasks/status/`

**Request**
```json
{
  "id": "task_093d9c1ab5774081aab1251b2b61e729",
  "status": "IN_PROGRESS"
}
```

**Response**
```json
{
  "message": "Task status updated successfully.",
  "id": "task_093d9c1ab5774081aab1251b2b61e729",
  "status": "IN_PROGRESS"
}
```

### 21. Update Frontend Task Status to In Progress

**Endpoint:** `PATCH /api/tasks/status/`

**Request**
```json
{
  "id": "task_80a0062bceb64c2587a257e074030240",
  "status": "IN_PROGRESS"
}
```

**Response**
```json
{
  "message": "Task status updated successfully.",
  "id": "task_80a0062bceb64c2587a257e074030240",
  "status": "IN_PROGRESS"
}
```

### 22. Mark Frontend Task as Complete

**Endpoint:** `PATCH /api/tasks/status/`

**Request**
```json
{
  "id": "task_80a0062bceb64c2587a257e074030240",
  "status": "COMPLETE"
}
```

**Response**
```json
{
  "message": "Task status updated successfully.",
  "id": "task_80a0062bceb64c2587a257e074030240",
  "status": "COMPLETE"
}
```

### 23. Remove Users from Team

**Endpoint:** `POST /api/teams/users/remove/`

**Request**
```json
{
  "id": "team_650d65a8561148f3ac4513a899c9b6b2",
  "users": [
    "usr_54b258e68edb4897b9673092898a777e"
  ]
}
```

**Response**
```json
{
    "message": "Users removed from team successfully.",
    "team_id": "team_650d65a8561148f3ac4513a899c9b6b2",
    "removed_count": 1
}
```

### 24. Close Board

**Endpoint:** `POST /api/boards/close/`

**Request**
```json
{
  "id": "board_845f303c3a8b4f0c8972c0533368a8e7"
}
```

**Response**

A board may only be closed if all its tasks satisfy the application's completion rules.
```json
{
    "error": "Cannot close the board until all tasks are complete."
}
```

### 25. Export Board

**Endpoint:** `POST /api/boards/export/`

**Request**
```json
{
  "id": "board_845f303c3a8b4f0c8972c0533368a8e7"
}
```

**Response**
```json
{
    "out_file": "board_845f303c3a8b4f0c8972c0533368a8e7.txt"
}
```


### 26. List Boards After Creation or Closure

**Endpoint:** `POST /api/boards/`

**Request**
```json
{
  "team_id": "team_650d65a8561148f3ac4513a899c9b6b2"
}
```

**Response**

```json
[
    {
        "id": "board_845f303c3a8b4f0c8972c0533368a8e7",
        "name": "Sprint 1 - Application Development"
    }
]
```

## Development Standards

The project follows PEP 8 for Python code style and PEP 257 for docstrings. Validation, storage, business logic, and request handling are organized into separate modules.

## License

Developed as a Team Project Planner assignment.
