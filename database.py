import sqlite3

# 1. TEMEL SINIF: Bağlantı ve Kurulum
class DatabaseCore:
    def __init__(self, db_name="curriculum.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS Courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT NOT NULL UNIQUE, course_name TEXT NOT NULL, credit INTEGER NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, id_number TEXT NOT NULL UNIQUE, enrollment_year INTEGER NOT NULL, department TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Instructors (
                id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, id_number TEXT NOT NULL UNIQUE, department TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Curriculum (
                id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT NOT NULL, instructor_id TEXT NOT NULL, term_info TEXT NOT NULL, UNIQUE(term_info, course_code, instructor_id))''') 

        cursor.execute('''INSERT OR IGNORE INTO Users (username, password, role) VALUES ('admin', 'admin123', 'Admin')''')
        
        conn.commit() 
        conn.close()

# 2. ADMIN & AUTH SINIFI
class AdminDB(DatabaseCore):
    def authenticate_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT role FROM Users WHERE username=? AND password=?", (username, password))
        admin_user = cursor.fetchone()
        if admin_user:
            conn.close()
            return True, admin_user[0], None

        cursor.execute('''SELECT department FROM Students WHERE first_name || ' ' || last_name COLLATE NOCASE = ? AND id_number = ?''', (username, password))
        student_user = cursor.fetchone()
        if student_user:
            conn.close()
            return True, "Student", student_user[0]

        cursor.execute('''SELECT department FROM Instructors WHERE first_name || ' ' || last_name COLLATE NOCASE = ? AND id_number = ?''', (username, password))
        instructor_user = cursor.fetchone()
        if instructor_user:
            conn.close()
            return True, "Instructor", instructor_user[0]

        conn.close()
        return False, None, None

    def add_admin(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, 'Admin')", (username, password))
            conn.commit()
            return True, "Admin added successfully."
        except sqlite3.IntegrityError:
            return False, "This admin username already exists!"
        finally:
            conn.close()

    def get_all_admins(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM Users WHERE role='Admin'")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_admin(self, old_username, new_username, new_password):
        if old_username.lower() == 'admin' and new_username.lower() != 'admin':
            return False, "Cannot change the username of the default root admin!"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Users SET username=?, password=? WHERE username=?", (new_username, new_password, old_username))
            conn.commit()
            return True, "Admin updated successfully."
        except sqlite3.IntegrityError:
            return False, "This username already exists!"
        finally:
            conn.close()

    def delete_admin(self, username):
        if username.lower() == 'admin': return False, "Cannot delete the default root admin!"
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE username=?", (username,))
        conn.commit()
        conn.close()
        return True, "Admin deleted successfully."

# 3. DERS SINIFI
class CourseDB(DatabaseCore):
    def add_course(self, course_code, course_name, credit):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Courses (course_code, course_name, credit) VALUES (?, ?, ?)', (course_code, course_name, credit))
            conn.commit()
            return True, "Course added successfully."
        except sqlite3.IntegrityError:
            return False, "This Course Code already exists!"
        finally:
            conn.close()

    def get_all_courses(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_code, course_name, credit FROM Courses")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_course(self, old_code, new_code, course_name, credit):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE Courses SET course_code=?, course_name=?, credit=? WHERE course_code=?''', (new_code, course_name, credit, old_code))
            cursor.execute('''UPDATE Curriculum SET course_code=? WHERE course_code=?''', (new_code, old_code))
            conn.commit()
            return True, "Course updated successfully."
        except sqlite3.IntegrityError:
            return False, "This Course Code already exists!"
        finally:
            conn.close()

    def delete_course(self, course_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Courses WHERE course_code=?", (course_code,))
        cursor.execute("DELETE FROM Curriculum WHERE course_code=?", (course_code,))
        conn.commit()
        conn.close()
        return True, "Course deleted successfully."

# 4. ÖĞRENCİ SINIFI
class StudentDB(DatabaseCore):
    def add_student(self, first_name, last_name, id_number, enrollment_year, department):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Students (first_name, last_name, id_number, enrollment_year, department) VALUES (?, ?, ?, ?, ?)', (first_name, last_name, id_number, enrollment_year, department))
            conn.commit()
            return True, "Student added successfully."
        except sqlite3.IntegrityError:
            return False, "A student with this ID is already registered!"
        finally:
            conn.close()

    def get_all_students(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, id_number, enrollment_year, department FROM Students")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_student(self, old_id, new_id, first_name, last_name, enrollment_year, department):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE Students SET id_number=?, first_name=?, last_name=?, enrollment_year=?, department=? WHERE id_number=?''', (new_id, first_name, last_name, enrollment_year, department, old_id))
            conn.commit()
            return True, "Student updated successfully."
        except sqlite3.IntegrityError:
            return False, "This Student ID already exists!"
        finally:
            conn.close()

    def delete_student(self, id_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Students WHERE id_number=?", (id_number,))
        conn.commit()
        conn.close()
        return True, "Student deleted successfully."

# 5. EĞİTMEN SINIFI
class InstructorDB(DatabaseCore):
    def add_instructor(self, first_name, last_name, id_number, department):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Instructors (first_name, last_name, id_number, department) VALUES (?, ?, ?, ?)', (first_name, last_name, id_number, department))
            conn.commit()
            return True, "Instructor added successfully."
        except sqlite3.IntegrityError:
            return False, "An instructor with this ID already exists!"
        finally:
            conn.close()

    def get_all_instructors(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, id_number, department FROM Instructors")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_instructor(self, old_id, new_id, first_name, last_name, department):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE Instructors SET id_number=?, first_name=?, last_name=?, department=? WHERE id_number=?''', (new_id, first_name, last_name, department, old_id))
            cursor.execute('''UPDATE Curriculum SET instructor_id=? WHERE instructor_id=?''', (new_id, old_id))
            conn.commit()
            return True, "Instructor updated successfully."
        except sqlite3.IntegrityError:
            return False, "This Instructor ID already exists!"
        finally:
            conn.close()

    def delete_instructor(self, id_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Instructors WHERE id_number=?", (id_number,))
        cursor.execute("DELETE FROM Curriculum WHERE instructor_id=?", (id_number,))
        conn.commit()
        conn.close()
        return True, "Instructor deleted successfully."

    def get_all_departments(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT department FROM Instructors")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_instructors_by_dept(self, dept):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, id_number, department FROM Instructors WHERE department=?", (dept,))
        rows = cursor.fetchall()
        conn.close()
        return rows

# 6. MÜFREDAT SINIFI (YENİ BİR DERSİN 2. KEZ EKLENMESİNİ ENGELLEYEN MANTIK BURADA)
class CurriculumDB(DatabaseCore):
    def assign_course(self, course_code, instructor_id, term_info):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Hangi departmana atama yapıldığını bulalım
            cursor.execute("SELECT department FROM Instructors WHERE id_number=?", (instructor_id,))
            dept = cursor.fetchone()[0]

            # 2. Bu departmanda bu ders zaten herhangi bir dönemde var mı kontrol edelim
            cursor.execute('''
                SELECT c.id FROM Curriculum c
                JOIN Instructors i ON c.instructor_id = i.id_number
                WHERE c.course_code = ? AND i.department = ?
            ''', (course_code, dept))
            
            if cursor.fetchone():
                return False, f"This course is already assigned to the {dept} department in another term!"

            cursor.execute('''INSERT INTO Curriculum (course_code, instructor_id, term_info)
                              VALUES (?, ?, ?)''', (course_code, instructor_id, term_info))
            conn.commit()
            return True, "Course assigned to curriculum successfully."
        except sqlite3.IntegrityError:
            return False, "This exact assignment already exists!"
        finally:
            conn.close()

    def update_assignment(self, old_term, old_course_code, new_term, new_course_code, new_instructor_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Yeni atanan hocanın departmanını bul
            cursor.execute("SELECT department FROM Instructors WHERE id_number=?", (new_instructor_id,))
            new_dept = cursor.fetchone()[0]

            # 2. Kopya kontrolü: Bu departmanda bu ders zaten var mı?
            # (Şu an güncellediğimiz satırı bu kontrolün dışında bırakıyoruz ki kendi kendini engellemesin)
            cursor.execute('''
                SELECT c.id FROM Curriculum c
                JOIN Instructors i ON c.instructor_id = i.id_number
                WHERE c.course_code = ? AND i.department = ? 
                AND NOT (c.term_info = ? AND c.course_code = ?)
            ''', (new_course_code, new_dept, old_term, old_course_code))
            
            if cursor.fetchone():
                return False, f"The course {new_course_code} is already assigned to the {new_dept} department!"

            # 3. Her şey uygunsa güncellemeyi yap
            cursor.execute('''UPDATE Curriculum SET term_info=?, course_code=?, instructor_id=? WHERE term_info=? AND course_code=?''', (new_term, new_course_code, new_instructor_id, old_term, old_course_code))
            conn.commit()
            return True, "Assignment updated successfully."
        except sqlite3.IntegrityError:
            return False, "This exact assignment already exists in the selected term!"
        finally:
            conn.close()

    def delete_assignment(self, term_info, course_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Curriculum WHERE term_info=? AND course_code=?", (term_info, course_code))
        conn.commit()
        conn.close()
        return True, "Assignment removed from curriculum."

    def get_curriculum(self, filter_dept=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = '''SELECT c.term_info, c.course_code, co.course_name, i.first_name, i.last_name, i.department FROM Curriculum c JOIN Courses co ON c.course_code = co.course_code JOIN Instructors i ON c.instructor_id = i.id_number'''
        
        if filter_dept:
            query += " WHERE i.department = ? ORDER BY c.term_info ASC"
            cursor.execute(query, (filter_dept,))
        else:
            query += " ORDER BY c.term_info ASC"
            cursor.execute(query)
            
        rows = cursor.fetchall()
        conn.close()
        return rows