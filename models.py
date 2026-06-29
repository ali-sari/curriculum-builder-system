# Base class for all people in the system
class Person:
    def __init__(self, first_name, last_name, id_number):
        self.first_name = first_name
        self.last_name = last_name
        self.id_number = id_number # National ID or University ID

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# Student class inheriting from Person
class Student(Person):
    def __init__(self, first_name, last_name, id_number, enrollment_year):
        # super() calls the constructor of the parent class (Person)
        super().__init__(first_name, last_name, id_number)
        self.enrollment_year = enrollment_year

    def display_info(self):
        print(f"Student: {self.get_full_name()} - Enrolled: {self.enrollment_year}")

# Instructor class inheriting from Person
class Instructor(Person):
    def __init__(self, first_name, last_name, id_number, department):
        super().__init__(first_name, last_name, id_number)
        self.department = department

    def display_info(self):
        print(f"Instructor: {self.get_full_name()} - Dept: {self.department}")

class Course:
    # Constructor method to initialize a new Course object
    def __init__(self, course_code, course_name, credit):
        self.course_code = course_code  # Unique identifier for the course (e.g., CENG204)
        self.course_name = course_name  # The full name of the course
        self.credit = credit            # The credit value of the course

    # Method to print the course details to the console (useful for debugging)
    def display_info(self):
        print(f"Course: {self.course_code} - {self.course_name} ({self.credit} Credits)")

# --- CURRICULUM MODELS ---

# Class 10: Represents an academic semester (e.g., Fall 2026)
class Semester:
    def __init__(self, term_name, year):
        self.term_name = term_name # e.g., "Fall" or "Spring"
        self.year = year           # e.g., 2026

    # Returns a formatted string of the semester
    def get_semester_info(self):
        return f"{self.term_name} {self.year}"

# Class 11: Represents a specific course assigned to an instructor for a semester
class CourseAssignment:
    def __init__(self, course_code, instructor_id, term_info):
        self.course_code = course_code
        self.instructor_id = instructor_id
        self.term_info = term_info # Uses the format from Semester class

# Class 12: Represents the overall curriculum containing multiple assignments
class Curriculum:
    def __init__(self, department_name):
        self.department_name = department_name
        self.assignments = [] # List to hold multiple CourseAssignment objects

    # Adds a new assignment to the curriculum list
    def add_assignment(self, assignment):
        self.assignments.append(assignment)

# --- AUTHENTICATION MODELS ---

# Class 14: Represents a system user for login
class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role # e.g., "Admin" or "Student"        