import tkinter as tk
from tkinter import ttk, messagebox
from database import AdminDB, CourseDB, StudentDB, InstructorDB, CurriculumDB


# ====================================================================
# Class 15: Handles the user login interface and authentication
# ====================================================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("System Login")
        self.root.geometry("300x250")
        self.db = AdminDB() # Artık sadece AdminDB'yi kullanıyor
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        # YENİ: Bilgi Etiketi
        tk.Label(frame, text="Admins: Use Username & Password", fg="gray", font=("Arial", 8)).pack()
        tk.Label(frame, text="Others: Use 'First Last' Name & ID Number", fg="gray", font=("Arial", 8)).pack(pady=(0, 10))

        tk.Label(frame, text="Username / Name Surname:", font=("Arial", 10)).pack(pady=5)
        self.user_entry = tk.Entry(frame, width=25)
        self.user_entry.pack(pady=5)

        tk.Label(frame, text="Password / ID Number:", font=("Arial", 10)).pack(pady=5)
        self.pass_entry = tk.Entry(frame, width=25, show="*")
        self.pass_entry.pack(pady=5)

        login_btn = tk.Button(frame, text="Login", command=self.login_action, bg="lightgreen", width=15)
        login_btn.pack(pady=15)

    def login_action(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password.")
            return

        # YENİ: Artık 3 değişken dönüyor (success, role, dept)
        success, role, dept = self.db.authenticate_user(username, password)

        if success:
            messagebox.showinfo("Success", f"Logged in successfully as {role}!")
            self.open_dashboard(role, dept) # Dept bilgisini de panele yolluyoruz
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_dashboard(self, role, dept):
        self.root.withdraw()
        dash_window = tk.Toplevel(self.root)
        dash_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        app = DashboardWindow(dash_window, role, dept) # Dept bilgisi Dashboard'a iletildi

# ====================================================================
# Class 6: The main dashboard holding all tabs
# ====================================================================
class DashboardWindow:
    def __init__(self, root, role="Admin", dept=None): 
        self.root = root
        self.role = role
        self.dept = dept
        
        # Başlık
        title_text = f"Curriculum Management System - Logged in as: {self.role}"
        if self.dept:
            title_text += f" ({self.dept} Department)"
        self.root.title(title_text)
        self.root.geometry("700x750")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Yalnızca Admin ise tüm sekmeleri göster
        if self.role == "Admin":
            self.course_frame = ttk.Frame(self.notebook)
            self.student_frame = ttk.Frame(self.notebook)
            self.instructor_frame = ttk.Frame(self.notebook)
            self.admin_frame = ttk.Frame(self.notebook) 
            
            self.notebook.add(self.course_frame, text="Courses")
            self.notebook.add(self.student_frame, text="Students")
            self.notebook.add(self.instructor_frame, text="Instructors")
            self.notebook.add(self.admin_frame, text="Admins")

            # DİKKAT: Artık buralarda db nesnesi yollamıyoruz, her sınıf kendi db'sini yaratıyor
            self.course_tab = CourseManagerTab(self.course_frame)
            self.student_tab = StudentManagerTab(self.student_frame)
            self.instructor_tab = InstructorManagerTab(self.instructor_frame)
            self.admin_tab = AdminManagerTab(self.admin_frame)

        # Herkes için Curriculum sekmesi
        self.curriculum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.curriculum_frame, text="Curriculum Builder" if self.role == "Admin" else "Curriculum View")
        
        # DİKKAT: Burada da self.db yollanmıyor. Sadece frame, role ve dept yollanıyor.
        self.curriculum_tab = CurriculumManagerTab(self.curriculum_frame, self.role, self.dept)

# Class 7: Handles only the Course tab logic
class CourseManagerTab:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.db = CourseDB()
        self.selected_old_code = "" # YENİ: Hafıza değişkeni
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.code_entry = tk.Entry(input_frame, width=30)
        self.code_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Course Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(input_frame, width=30)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Credits:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.credit_entry = tk.Entry(input_frame, width=30)
        self.credit_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- YENİ: BUTONLAR İÇİN ALT ÇERÇEVE ---
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        add_button = tk.Button(button_frame, text="Add", command=self.add_course_action, bg="lightblue", width=10)
        add_button.pack(side=tk.LEFT, padx=5)

        update_button = tk.Button(button_frame, text="Update", command=self.update_course_action, bg="lightgoldenrod", width=10)
        update_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_course_action, bg="lightcoral", width=10)
        delete_button.pack(side=tk.LEFT, padx=5)

        # --- LİSTELEME ALANI ---
        tk.Label(self.frame, text="Registered Courses (Click to Select)", font=("Arial", 12, "bold")).pack(pady=5)
        self.course_listbox = tk.Listbox(self.frame, width=70, height=15)
        self.course_listbox.pack(pady=5)
        
        # YENİ: Listeden bir satıra tıklandığında on_select fonksiyonunu tetikler
        self.course_listbox.bind('<<ListboxSelect>>', self.on_select)

    # YENİ: Listeden veri seçme işlemi (Kutuları otomatik doldurur)
    def on_select(self, event):
        try:
            selected_index = self.course_listbox.curselection()[0]
            selected_item = self.course_listbox.get(selected_index)
            course_code = selected_item.split(" - ")[0]
            course_name = selected_item.split(" - ")[1].split(" (")[0]
            credit = selected_item.split("(")[1].split(" ")[0]
            
            self.clear_entries()
            self.selected_old_code = course_code # YENİ: Eski kodu hafızaya al
            
            self.code_entry.insert(0, course_code)
            self.name_entry.insert(0, course_name)
            self.credit_entry.insert(0, credit)
        except IndexError:
            pass

    def add_course_action(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        credit_str = self.credit_entry.get().strip()

        if not code or not name or not credit_str:
            messagebox.showwarning("Missing Information", "Please fill in all fields!")
            return

        if name.isdigit():
            messagebox.showerror("Invalid Data", "Course Name cannot consist only of numbers!")
            return

        try:
            credit = int(credit_str)
        except ValueError:
            messagebox.showerror("Invalid Data", "Credits must be a numeric value!")
            return

        success, message = self.db.add_course(code, name, credit)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_courses()
        else:
            messagebox.showerror("Error", message)

    # YENİ: Güncelleme İşlemi
    def update_course_action(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        credit_str = self.credit_entry.get().strip()

        if not code or not name or not credit_str or not self.selected_old_code:
            messagebox.showwarning("Missing Information", "Please select a course and fill fields!")
            return
        if name.isdigit():
            messagebox.showerror("Invalid Data", "Course Name cannot consist only of numbers!")
            return
        try:
            credit = int(credit_str)
        except ValueError:
            messagebox.showerror("Invalid Data", "Credits must be a numeric value!")
            return

        # YENİ: Hem eski hem yeni kodu veritabanına gönderiyoruz
        success, message = self.db.update_course(self.selected_old_code, code, name, credit)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_courses()
        else:
            messagebox.showerror("Error", message)

    # YENİ: Silme İşlemi
    def delete_course_action(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Missing Information", "Please select a course to delete!")
            return
        
        # Kullanıcıya emin olup olmadığını soralım
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {code}?\nThis will also remove it from the curriculum!")
        if confirm:
            success, message = self.db.delete_course(code)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_entries()
                self.load_courses()

    def load_courses(self):
        self.course_listbox.delete(0, tk.END)
        courses = self.db.get_all_courses()
        for course in courses:
            self.course_listbox.insert(tk.END, f"{course[0]} - {course[1]} ({course[2]} Credits)")

    # Yardımcı Fonksiyon: Metin kutularını temizler
    def clear_entries(self):
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.credit_entry.delete(0, tk.END)
        self.selected_old_code = "" # YENİ: Hafızayı sıfırla

# Class 8: Handles only the Student tab logic
# ====================================================================
class StudentManagerTab:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.db = StudentDB()
        self.student_data = [] 
        self.selected_old_id = ""
        # YENİ: Sabit Departman Listesi
        self.departments = ["Computer Engineering", "Electrical Engineering", "Software Engineering", "Mechanical Engineering", "Industrial Engineering", "Civil Engineering"]
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.fname_entry = tk.Entry(input_frame, width=30)
        self.fname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.lname_entry = tk.Entry(input_frame, width=30)
        self.lname_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="ID Number:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = tk.Entry(input_frame, width=30)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Enrollment Year:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.year_entry = tk.Entry(input_frame, width=30)
        self.year_entry.grid(row=3, column=1, padx=5, pady=5)

        # YENİ: Departman için Entry yerine Combobox (Açılır Liste) kullanıyoruz
        tk.Label(input_frame, text="Department:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.dept_combo = ttk.Combobox(input_frame, width=27, state="readonly", values=self.departments)
        self.dept_combo.grid(row=4, column=1, padx=5, pady=5)

        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Add", command=self.add_student_action, bg="lightgreen", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_student_action, bg="lightgoldenrod", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_student_action, bg="lightcoral", width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame, text="Registered Students (Click to Select)", font=("Arial", 12, "bold")).pack(pady=5)
        self.student_listbox = tk.Listbox(self.frame, width=80, height=12)
        self.student_listbox.pack(pady=5)
        self.student_listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event):
        try:
            selected_index = self.student_listbox.curselection()[0]
            student = self.student_data[selected_index] 
            
            self.clear_entries()
            self.selected_old_id = student[2]
            
            self.fname_entry.insert(0, student[0])
            self.lname_entry.insert(0, student[1])
            self.id_entry.insert(0, student[2])
            self.year_entry.insert(0, student[3])
            self.dept_combo.set(student[4]) # YENİ: Combobox verisini ayarla
        except IndexError:
            pass

    def add_student_action(self):
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        id_num = self.id_entry.get().strip()
        year_str = self.year_entry.get().strip()
        dept = self.dept_combo.get() # YENİ: Combobox'tan seçileni al

        if not fname or not lname or not id_num or not year_str or not dept:
            messagebox.showwarning("Missing Information", "Please fill in all fields!")
            return
        if not fname.replace(" ", "").isalpha() or not lname.replace(" ", "").isalpha():
            messagebox.showerror("Invalid Data", "First and Last Name must contain only letters!")
            return
        if not id_num.isdigit():
            messagebox.showerror("Invalid Data", "ID Number must contain only numbers!")
            return
        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Invalid Data", "Enrollment Year must be a numeric value!")
            return

        success, message = self.db.add_student(fname, lname, id_num, year, dept)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_students()
        else:
            messagebox.showerror("Error", message)

    def update_student_action(self):
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        id_num = self.id_entry.get().strip()
        year_str = self.year_entry.get().strip()
        dept = self.dept_combo.get()

        if not fname or not lname or not id_num or not year_str or not dept or not self.selected_old_id:
            messagebox.showwarning("Missing Information", "Please select a student and fill fields!")
            return
        if not fname.replace(" ", "").isalpha() or not lname.replace(" ", "").isalpha():
            messagebox.showerror("Invalid Data", "First and Last Name must contain only letters!")
            return
        if not id_num.isdigit():
            messagebox.showerror("Invalid Data", "ID Number must contain only numbers!")
            return
        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Invalid Data", "Enrollment Year must be numeric!")
            return

        success, message = self.db.update_student(self.selected_old_id, id_num, fname, lname, year, dept)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_students()
        else:
            messagebox.showerror("Error", message)

    def delete_student_action(self):
        id_num = self.id_entry.get().strip()
        if not id_num:
            messagebox.showwarning("Missing Information", "Please select a student to delete!")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID: {id_num}?")
        if confirm:
            success, message = self.db.delete_student(id_num)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_entries()
                self.load_students()

    def load_students(self):
        self.student_listbox.delete(0, tk.END)
        self.student_data = self.db.get_all_students()
        for student in self.student_data:
            self.student_listbox.insert(tk.END, f"{student[2]} - {student[0]} {student[1]} (Year: {student[3]}, Dept: {student[4]})")

    def clear_entries(self):
        self.fname_entry.delete(0, tk.END)
        self.lname_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.dept_combo.set('') # YENİ: Combobox'ı temizle
        self.selected_old_id = ""


# Class 9: Handles only the Instructor tab logic
# ====================================================================
# Class 9: Handles only the Instructor tab logic
# ====================================================================
class InstructorManagerTab:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.db = InstructorDB()
        self.instructor_data = []
        self.selected_old_id = ""
        # YENİ: Sabit Departman Listesi
        self.departments = ["Computer Engineering", "Electrical Engineering", "Software Engineering", "Mechanical Engineering", "Industrial Engineering", "Civil Engineering"]
        self.setup_ui()
        self.load_instructors()

    def setup_ui(self):
        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.fname_entry = tk.Entry(input_frame, width=30)
        self.fname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.lname_entry = tk.Entry(input_frame, width=30)
        self.lname_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="ID Number:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.id_entry = tk.Entry(input_frame, width=30)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5)

        # YENİ: Departman için Entry yerine Combobox (Açılır Liste) kullanıyoruz
        tk.Label(input_frame, text="Department:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.dept_combo = ttk.Combobox(input_frame, width=27, state="readonly", values=self.departments)
        self.dept_combo.grid(row=3, column=1, padx=5, pady=5)

        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Add", command=self.add_instructor_action, bg="lightcoral", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_instructor_action, bg="lightgoldenrod", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_instructor_action, bg="lightblue", width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame, text="Registered Instructors (Click to Select)", font=("Arial", 12, "bold")).pack(pady=5)
        self.instructor_listbox = tk.Listbox(self.frame, width=70, height=12)
        self.instructor_listbox.pack(pady=5)
        self.instructor_listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event):
        try:
            selected_index = self.instructor_listbox.curselection()[0]
            inst = self.instructor_data[selected_index]
            
            self.clear_entries()
            self.selected_old_id = inst[2]
            
            self.fname_entry.insert(0, inst[0])
            self.lname_entry.insert(0, inst[1])
            self.id_entry.insert(0, inst[2])
            self.dept_combo.set(inst[3]) # YENİ: Combobox verisini ayarla
        except IndexError:
            pass

    def add_instructor_action(self):
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        id_num = self.id_entry.get().strip()
        dept = self.dept_combo.get() # YENİ

        if not fname or not lname or not id_num or not dept:
            messagebox.showwarning("Missing Information", "Please fill in all fields!")
            return
        if not fname.replace(" ", "").isalpha() or not lname.replace(" ", "").isalpha():
            messagebox.showerror("Invalid Data", "First and Last Name must contain only letters!")
            return
        if not id_num.isdigit():
            messagebox.showerror("Invalid Data", "ID Number must contain only numbers!")
            return

        success, message = self.db.add_instructor(fname, lname, id_num, dept)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_instructors()
        else:
            messagebox.showerror("Error", message)

    def update_instructor_action(self):
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        id_num = self.id_entry.get().strip()
        dept = self.dept_combo.get() # YENİ

        if not fname or not lname or not id_num or not dept or not self.selected_old_id:
            messagebox.showwarning("Missing Information", "Please select an instructor and fill fields!")
            return
        if not fname.replace(" ", "").isalpha() or not lname.replace(" ", "").isalpha():
            messagebox.showerror("Invalid Data", "First and Last Name must contain only letters!")
            return

        success, message = self.db.update_instructor(self.selected_old_id, id_num, fname, lname, dept)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_instructors()
        else:
            messagebox.showerror("Error", message)

    def delete_instructor_action(self):
        id_num = self.id_entry.get().strip()
        if not id_num:
            messagebox.showwarning("Missing Information", "Please select an instructor to delete!")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete instructor ID: {id_num}?\nThis will remove their curriculum assignments too!")
        if confirm:
            success, message = self.db.delete_instructor(id_num)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_entries()
                self.load_instructors()

    def load_instructors(self):
        self.instructor_listbox.delete(0, tk.END)
        self.instructor_data = self.db.get_all_instructors()
        for inst in self.instructor_data:
            self.instructor_listbox.insert(tk.END, f"{inst[2]} - {inst[0]} {inst[1]} (Dept: {inst[3]})")

    def clear_entries(self):
        self.fname_entry.delete(0, tk.END)
        self.lname_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.dept_combo.set('') # YENİ
        self.selected_old_id = ""

# ====================================================================
# Class 13: Handles the Curriculum assignment logic
# ====================================================================
class CurriculumManagerTab:
    def __init__(self, parent_frame, role="Admin", dept=None):
        self.frame = parent_frame
        self.role = role
        self.dept = dept
        
        # DAO (Data Access Object) bağlantıları ayrıldı
        self.db = CurriculumDB()
        self.course_db = CourseDB()
        self.instructor_db = InstructorDB()
        
        self.curriculum_data = []
        self.selected_old_term = ""
        self.selected_old_course = ""
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        if self.role == "Admin":
            input_frame = tk.Frame(self.frame)
            input_frame.pack(pady=15)

            tk.Label(input_frame, text="Academic Term:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.term_combo = ttk.Combobox(input_frame, width=37, state="readonly")
            self.term_combo['values'] = ["1. Fall", "1. Spring", "2. Fall", "2. Spring", "3. Fall", "3. Spring", "4. Fall", "4. Spring"]
            self.term_combo.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(input_frame, text="Select Course:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.course_combo = ttk.Combobox(input_frame, width=37, state="readonly")
            self.course_combo.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(input_frame, text="Select Department:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            self.dept_combo = ttk.Combobox(input_frame, width=37, state="readonly")
            self.dept_combo.grid(row=2, column=1, padx=5, pady=5)
            self.dept_combo.bind('<<ComboboxSelected>>', self.on_dept_select)

            tk.Label(input_frame, text="Select Instructor:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.instructor_combo = ttk.Combobox(input_frame, width=37, state="readonly")
            self.instructor_combo.grid(row=3, column=1, padx=5, pady=5)

            # BUTONLAR
            button_frame = tk.Frame(input_frame)
            button_frame.grid(row=4, column=0, columnspan=2, pady=15)

            tk.Button(button_frame, text="Assign", command=self.assign_action, bg="lightblue", width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Update", command=self.update_assignment_action, bg="lightgoldenrod", width=10).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Delete", command=self.delete_assignment_action, bg="lightcoral", width=10).pack(side=tk.LEFT, padx=5)

            tk.Button(input_frame, text="Refresh Lists", command=self.refresh_data).grid(row=5, column=0, columnspan=2, pady=5)
        else:
            tk.Label(self.frame, text="You have read-only access to the curriculum.", fg="blue", font=("Arial", 10, "italic")).pack(pady=10)

        tk.Label(self.frame, text="Current Curriculum (Click to Select)", font=("Arial", 12, "bold")).pack(pady=5)
        self.curriculum_listbox = tk.Listbox(self.frame, width=80, height=13)
        self.curriculum_listbox.pack(pady=5)
        
        self.curriculum_listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event):
        if self.role != "Admin": return 
        try:
            selected_index = self.curriculum_listbox.curselection()[0]
            row = self.curriculum_data[selected_index]
            
            self.selected_old_term = row[0]
            self.selected_old_course = row[1]
            
            self.term_combo.set(row[0])
            self.course_combo.set(f"{row[1]} - {row[2]}")
            self.dept_combo.set(row[5]) 
            self.on_dept_select(None) 
        except IndexError:
            pass

    def on_dept_select(self, event):
        selected_dept = self.dept_combo.get()
        # YENİ: Eğitmen veritabanına özel bağlantı kullanılıyor
        instructors = self.instructor_db.get_instructors_by_dept(selected_dept)
        self.instructor_combo['values'] = [f"{i[2]} - {i[0]} {i[1]}" for i in instructors]
        self.instructor_combo.set('')

    def assign_action(self):
        term = self.term_combo.get()
        selected_course = self.course_combo.get()
        selected_instructor = self.instructor_combo.get()

        if not term or not selected_course or not selected_instructor:
            messagebox.showwarning("Missing Information", "Please select a Term, Course, Department, and Instructor!")
            return

        course_code = selected_course.split(" - ")[0]
        instructor_id = selected_instructor.split(" - ")[0]

        success, message = self.db.assign_course(course_code, instructor_id, term)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_data()
        else:
            messagebox.showerror("Error", message)

    def update_assignment_action(self):
        term = self.term_combo.get()
        selected_course = self.course_combo.get()
        selected_instructor = self.instructor_combo.get()

        if not term or not selected_course or not selected_instructor or not self.selected_old_course:
            messagebox.showwarning("Missing Info", "Please select an assignment from the list, then select new values!")
            return

        course_code = selected_course.split(" - ")[0]
        instructor_id = selected_instructor.split(" - ")[0]

        success, message = self.db.update_assignment(self.selected_old_term, self.selected_old_course, term, course_code, instructor_id)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_data()
        else:
            messagebox.showerror("Error", message)

    def delete_assignment_action(self):
        try:
            selected_index = self.curriculum_listbox.curselection()[0]
            row = self.curriculum_data[selected_index]
            term_info = row[0]
            course_code = row[1]
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select an assignment from the list to remove!")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove {course_code} from {term_info}?")
        if confirm:
            success, message = self.db.delete_assignment(term_info, course_code)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_data()

    def refresh_data(self):
        if self.role == "Admin":
            courses = self.course_db.get_all_courses()
            self.course_combo['values'] = [f"{c[0]} - {c[1]}" for c in courses]
            
            # YENİ: Veritabanından çekmek yerine sabit ana listemizi atıyoruz
            self.dept_combo['values'] = ["Computer Engineering", "Electrical Engineering", "Software Engineering", "Mechanical Engineering", "Industrial Engineering", "Civil Engineering"]

        self.curriculum_listbox.delete(0, tk.END)
        self.curriculum_data = self.db.get_curriculum(filter_dept=self.dept)
        
        for row in self.curriculum_data:
            display_text = f"[{row[0]}] {row[1]}: {row[2]} | Instructor: {row[3]} {row[4]} (Dept: {row[5]})"
            self.curriculum_listbox.insert(tk.END, display_text)
        
        self.selected_old_term = ""
        self.selected_old_course = ""

# ====================================================================
# Class 16: Handles the Admin creation, update, and deletion logic
# ====================================================================
class AdminManagerTab:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.db = AdminDB()
        self.admin_data = []
        self.selected_old_username = "" # Güncelleme sırasında eski ismi hafızada tutmak için
        self.setup_ui()
        self.load_admins()

    def setup_ui(self):
        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Admin Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(input_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        # YENİ: Şifre sansürü (show="*") kaldırıldı.
        self.password_entry = tk.Entry(input_frame, width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # BUTONLAR ÇERÇEVESİ
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Add", command=self.add_admin_action, bg="lightblue", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_admin_action, bg="lightgoldenrod", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_admin_action, bg="lightcoral", width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame, text="Registered Admins (Click to Select)", font=("Arial", 12, "bold")).pack(pady=5)
        self.admin_listbox = tk.Listbox(self.frame, width=60, height=12)
        self.admin_listbox.pack(pady=5)
        
        self.admin_listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event):
        try:
            selected_index = self.admin_listbox.curselection()[0]
            admin = self.admin_data[selected_index]
            
            self.clear_entries()
            self.selected_old_username = admin[0] # DÜZELTME: Clear işleminden SONRA hafızaya al!
            
            self.username_entry.insert(0, admin[0])
            self.password_entry.insert(0, admin[1])
        except IndexError:
            pass

    def add_admin_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please provide a username and password.")
            return

        success, message = self.db.add_admin(username, password)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_admins()
        else:
            messagebox.showerror("Error", message)

    def update_admin_action(self):
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()

        if not new_username or not new_password or not self.selected_old_username:
            messagebox.showwarning("Missing Info", "Please select an admin from the list to update!")
            return

        success, message = self.db.update_admin(self.selected_old_username, new_username, new_password)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_entries()
            self.load_admins()
        else:
            messagebox.showerror("Error", message)

    def delete_admin_action(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Missing Info", "Please select an admin to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete admin '{username}'?")
        if confirm:
            success, message = self.db.delete_admin(username)
            if success:
                messagebox.showinfo("Success", message)
                self.clear_entries()
                self.load_admins()
            else:
                messagebox.showerror("Error", message)

    def load_admins(self):
        self.admin_listbox.delete(0, tk.END)
        self.admin_data = self.db.get_all_admins()
        for admin in self.admin_data:
            # YENİ: Listede hem kullanıcı adı hem de şifre görünüyor
            self.admin_listbox.insert(tk.END, f"Username: {admin[0]}   |   Password: {admin[1]}")

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.selected_old_username = ""