import mysql.connector

class Database:
    def get_connection(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="aman@1246",
            database="course_system"
        )

class User:
    def __init__(self, name, email, role):
        self.__name = name
        self.__email = email
        self.__role = role

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_role(self):
        return self.__role


class UserService(Database):

    # CREATE
    def add_user(self, user):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """INSERT INTO users (name, email, role, password)
                       VALUES (%s, %s, %s, %s)"""

            cursor.execute(query, (user.get_name(),user.get_email(),user.get_role(), "123"))
            conn.commit()
  
            print("User added successfully")

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    
    def view_users(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
        SELECT user_id, name, email, password, role,
        DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s')
        FROM users
        """)              
            for row in cursor.fetchall():
                print(row)

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    # UPDATE
    def update_marks(self, student_id, course_id, marks):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """UPDATE performance 
                       SET total_marks=%s 
                       WHERE student_id=%s AND course_id=%s"""

            cursor.execute(query, (marks, student_id, course_id))
            conn.commit()

            print("Marks updated successfully")

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    def delete_user(self, user_id):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
            conn.commit()

            print("User deleted successfully")

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    def enroll_student(self,student_id, course_id):
        conn = None
        try:
             conn = self.get_connection()
             cursor = conn.cursor()

             query = "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)"
             cursor.execute(query, (student_id, course_id))

             conn.commit()
             print("Student enrolled successfully")

        except Exception as e:
             print("Error:", e)

        finally:
            if conn:
             conn.close()

    def view_enrollments(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT u.name, c.course_name
            FROM enrollments e
            JOIN users u ON e.student_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            """

            cursor.execute(query)

            for row in cursor.fetchall():
                print(row)

        except Exception as e:
             print("Error:", e)

        finally:
            if conn:
             conn.close()

    def add_assignment(self,course_id, title, max_marks, due_date):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO assignments (course_id, title, max_marks, due_date)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(query, (course_id, title, max_marks, due_date))
            conn.commit()

            print("Assignment added")

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    def add_submission(self,assignment_id, student_id, marks):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO submissions (assignment_id, student_id, submission_date, marks_obtained)
            VALUES (%s, %s, CURDATE(), %s)
            """

            cursor.execute(query, (assignment_id, student_id, marks))
            conn.commit()

            print("Submission added")

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()

    def view_performance(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT u.name, c.course_name, p.percentage, p.grade
            FROM performance p
            JOIN users u ON p.student_id = u.user_id
            JOIN courses c ON p.course_id = c.course_id
            """

            cursor.execute(query)

            for row in cursor.fetchall():
                print(row)

        except Exception as e:
            print("Error:", e)

        finally:
            if conn:
                conn.close()




