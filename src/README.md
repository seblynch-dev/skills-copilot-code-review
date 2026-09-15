# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign in as a teacher to register students
- View current school announcements
- Add, modify, and delete dated announcements as a signed-in teacher

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/activities` | Get activities, with optional day and time filters |
| POST | `/activities/{activity_name}/signup` | Register a student as a signed-in teacher |
| POST | `/activities/{activity_name}/unregister` | Unregister a student as a signed-in teacher |
| POST | `/auth/login` | Sign in and receive a session token |
| GET | `/auth/check-session` | Validate an existing session token |
| POST | `/auth/logout` | Invalidate a session token |
| GET | `/announcements` | Get announcements active today |
| GET | `/announcements/manage` | Get all announcements as a signed-in teacher |
| POST | `/announcements` | Create an announcement as a signed-in teacher |
| PUT | `/announcements/{announcement_id}` | Modify an announcement as a signed-in teacher |
| DELETE | `/announcements/{announcement_id}` | Delete an announcement as a signed-in teacher |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Teachers** - Uses username as identifier and stores a hashed password.

3. **Announcements** - Stores a message, optional start date, and required expiration date.

Application data is stored in MongoDB. Teacher session tokens are held in server memory and expire when the server restarts or the user logs out.
