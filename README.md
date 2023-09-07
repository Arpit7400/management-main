# management-main

Usage
To use this application, follow the API endpoints listed below.

API Endpoints

Class and Section Management
GET /class: Fetch all available classes.
POST /class/{class_id}: Create a class section by providing the class ID, section name, and strength.
GET /class/all_section/{classname}: Get all sections for a given class name.
GET /class/section/{class_id}: Get class details by ID.
GET /class/names/{name}: Get class details by name.
PUT /class/{class_id}: Update class details.

Subject Management
GET /subject: Fetch all subjects from the curriculum.
POST /subject/save/{name}: Save a subject in the management system.
GET /subject_m: Fetch all subjects from the management system.
POST /api/create_subject: Create a subject in the management system.

School Schedule Management
POST /api/create_days: Create a new day.
POST /api/create_teacher: Create a new teacher.
POST /api/create_activity: Create a new activity.
POST /api/create_break: Create a new break.
POST /api/create_schedule: Create a new lecture schedule.
GET /api/get_teachers: Fetch all teachers.
GET /api/get_activities: Fetch all activities.
GET /api/get_breaks: Fetch all breaks.