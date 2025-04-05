# Micro-Learn - E-Learning Platform

![Micro-Learn Logo](static/images/logo.png)

Micro-Learn is a Django-based e-learning platform that provides a comprehensive learning management system with features for students, instructors, and administrators.

## Features

### Student Features
- User registration and authentication
- Course enrollment and progress tracking
- Interactive assignments with automatic grading
- Course completion certificates
- Progress visualization with charts
- Academic report generation
- Course prerequisites enforcement

### Instructor Features
- Course creation and management
- Assignment creation with multiple-choice questions
- Student progress monitoring
- Grade management
- Course content organization

### Admin Features
- User management (students and instructors)
- System-wide oversight
- Instructor account management

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **Reporting**: ReportLab for PDF generation
- **Authentication**: Django's built-in auth system with custom role management

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/micro-learn.git
   cd micro-learn
