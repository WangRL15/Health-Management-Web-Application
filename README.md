# Health-Management-Web-Application
A comprehensive health management system built with Flask and MySQL that helps users track their fitness journey, diet, and exercise routines.

## Features

### User Authentication
- Secure user registration and login system
- Password encryption for enhanced security
- Session management for user authentication

### Profile Management
- Update and manage personal information
- Track basic health metrics like height and weight
- Personalized dashboard for each user

### Health Tracking

#### Exercise Planning
- Create and manage workout schedules
- Record exercise details including:
  - Date and time
  - Exercise type
  - Number of sets and repetitions
  - Weight/resistance used

#### Diet Tracking
- Comprehensive food diary system
- Record nutritional information:
  - Calorie intake
  - Protein content
  - Carbohydrate content
  - Fat content

#### Exercise Logging
- Track workout duration
- Monitor calories burned
- Record exercise intensity

### Data Analysis
- Visual representation of health data
- Progress tracking through interactive charts
- Compare actual results with health goals

## Technical Implementation

### Technologies Used
- **Backend Framework**: Flask
- **Database**: MySQL
- **ORM**: Flask-SQLAlchemy
- **Database Connector**: PyMySQL
- **Data Format**: JSON for dynamic chart data

### Key Technical Features
- Configured `SQLALCHEMY_DATABASE_URI` for database connection
- Session management for user authentication
- JSON data processing for dynamic chart generation
- Secure password handling and encryption

## Installation and Setup
### Requirements
To run this code, ensure the following are installed:

Python 3.8+
Required Python libraries:
  ```bash
flask, flask_sqlalchemy, datetime, werkzeug.security
  ```
