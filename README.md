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

## Development Standards

The project follows PEP 8 for Python code style and PEP 257 for docstrings. Validation, storage, business logic, and request handling are organized into separate modules.

## License

Developed as a Team Project Planner assignment.
