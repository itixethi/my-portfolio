# Formula 1 Web Application — FastAPI + Firebase

## Overview

This is a full-featured Formula 1 backend web application built using FastAPI, Firebase Firestore, and Jinja2Templates. It allows users to interact with a rich database of F1 drivers and teams — offering features like secure login, driver/team comparison, custom query filters, and global search.

Created from my interest in both Formula 1 and backend systems, this project demonstrates my ability to design a modular, secure, and scalable backend system with real-world usability.

## Tech Stack

- Framework: FastAPI
- Database: Firebase Firestore (NoSQL)
- Frontend Rendering: Jinja2Templates
- Auth: Firebase Authentication (ID Token verification)
- Language: Python 3.10+
- Other Tools: Git, pip, Firebase Admin SDK

## Key Features

- Secure Login via Firebase ID tokens  
- Add, Update, and Delete driver and team records  
- Global Search across teams and drivers  
- Driver and Team Comparison by multiple performance metrics  
- Structured Query Filters (e.g., find drivers with > 500 points or teams founded before 1990)  
- Modular FastAPI routes, controller files, and helper logic  

## Project Structure

```
FORMULA 1/
├── main.py                       # FastAPI app entry point
├── firebase/
│   └── helpers.py               # Firebase token validation
├── controllers/
│   ├── driver.py                # Driver data handling
│   ├── team.py                  # Team data handling
│   ├── compare.py               # Driver comparison controller
│   ├── compare_teams.py         # Team comparison controller
│   ├── query_drivers.py         # Attribute-based driver queries
│   ├── query_teams.py           # Attribute-based team queries
│   ├── search.py                # Global search logic
│   └── login.py                 # Login rendering and token handling
├── templates/                   # HTML pages (Jinja2)
├── static/                      # styles/js
├── .gitignore                   # Git tracking exclusions
└── README.md                    # This file
```

## How to Run Locally

1. Clone the repo
   ```bash
   git clone https://github.com/itixethi/my-portfolio.git
   cd "FORMULA 1"
   ```

2. Create a virtual environment
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server
   ```bash
   uvicorn main:app --reload
   ```

5. Open in browser:  
   Visit http://127.0.0.1:8000

## Functional Modules

| Module                     | Functionality |
|----------------------------|---------------|
| main.py                    | Orchestrates routes, Firebase setup |
| controllers/driver.py      | Add/update/delete/view driver profiles |
| controllers/team.py        | Manage F1 team records |
| controllers/compare.py     | Compare two drivers |
| controllers/compare_teams.py | Compare two teams |
| controllers/search.py      | Case-insensitive global search |
| controllers/query_drivers.py | Filter drivers by stats |
| controllers/query_teams.py   | Filter teams by metrics |
| controllers/login.py       | Login form & Firebase auth handling |
| firebase/helpers.py        | Token validation logic |

## Firebase Data Models

**Drivers Collection**:
- Name, Age, Team, Points, Titles, Pole Positions, Fastest Laps

**Teams Collection**:
- Name, Year Founded, Wins, Titles, Season Finish, Pole Positions

## What I Learned

- Structuring a scalable FastAPI application with modular routing
- Integrating Firebase Authentication and Firestore securely
- Building form-based logic for CRUD operations
- Designing user-friendly comparison and query features
- Managing secrets, .gitignore, and GitHub Push Protection

## Future Improvements

- Add real-time updates via Firebase listeners or WebSockets  
- Add pagination and sorting to search and list pages  
- Extend to RESTful APIs or frontends with React or Streamlit  
- Add unit tests and role-based access controls  

## Author

Osabohien P. Igiehon  
GitHub: [@itixethi](https://github.com/itixethi)
