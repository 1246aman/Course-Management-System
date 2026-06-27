from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'course_system_secret'


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "aman@1246",
    "database": "course_system"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_db(sql, params=(), fetchone=False):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    result = cur.fetchone() if fetchone else cur.fetchall()
    conn.close()
    return result

def mutate_db(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

@app.route('/')
def dashboard():
    try:
        users     = query_db("SELECT COUNT(*) AS c FROM users")[0]['c']
        courses   = query_db("SELECT COUNT(*) AS c FROM courses")[0]['c']
        enrolls   = query_db("SELECT COUNT(*) AS c FROM enrollments")[0]['c']
        assigns   = query_db("SELECT COUNT(*) AS c FROM assignments")[0]['c']
        avg_perf  = query_db("SELECT ROUND(AVG(percentage),1) AS a FROM performance")[0]['a'] or 0
        top_student = query_db("""
            SELECT u.name, MAX(p.percentage) AS pct
            FROM performance p JOIN users u ON p.student_id=u.user_id
            GROUP BY u.name ORDER BY pct DESC LIMIT 1
        """)
        recent_enrollments = query_db("""
            SELECT u.name, c.course_name, e.enrollment_date
            FROM enrollments e
            JOIN users u ON e.student_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id;
            ORDER BY e.enrolled_date DESC LIMIT 5
        """)
    except Exception as e:
        users = courses = enrolls = assigns = avg_perf = 0
        top_student = []
        recent_enrollments = []

    return render_template('dashboard.html',
        users=users, courses=courses, enrolls=enrolls,
        assigns=assigns, avg_perf=avg_perf,
        top_student=top_student[0] if top_student else None,
        recent_enrollments=recent_enrollments
    )

@app.route('/users')
def users():
    rows = query_db("SELECT user_id, name, email, role, DATE_FORMAT(created_at,'%Y-%m-%d %H:%i') AS created_at FROM users ORDER BY user_id DESC")
    return render_template('users.html', users=rows)

@app.route('/users/add', methods=['POST'])
def add_user():
    name  = request.form['name']
    email = request.form['email']
    role  = request.form['role']
    password = request.form.get('password', '123')
    try:
        mutate_db("INSERT INTO users (name,email,role,password) VALUES (%s,%s,%s,%s)",
                  (name, email, role, password))
        return jsonify(success=True, message="User added successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/users/delete/<int:uid>', methods=['POST'])
def delete_user(uid):
    try:
        mutate_db("DELETE FROM users WHERE user_id=%s", (uid,))
        return jsonify(success=True, message="User deleted successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/users/get/<int:uid>')
def get_user(uid):
    row = query_db("SELECT user_id,name,email,role FROM users WHERE user_id=%s", (uid,), fetchone=True)
    return jsonify(row)

@app.route('/users/update', methods=['POST'])
def update_user():
    uid   = request.form['user_id']
    name  = request.form['name']
    email = request.form['email']
    role  = request.form['role']
    try:
        mutate_db("UPDATE users SET name=%s,email=%s,role=%s WHERE user_id=%s", (name,email,role,uid))
        return jsonify(success=True, message="User updated successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/courses')
def courses():
    rows = query_db("SELECT * FROM courses ORDER BY course_id DESC")
    return render_template('courses.html', courses=rows)

@app.route('/courses/add', methods=['POST'])
def add_course():
    name = request.form['course_name']
    desc = request.form.get('description','')
    try:
        mutate_db("INSERT INTO courses (course_name, description) VALUES (%s,%s)", (name, desc))
        return jsonify(success=True, message="Course added successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/courses/delete/<int:cid>', methods=['POST'])
def delete_course(cid):
    try:
        mutate_db("DELETE FROM courses WHERE course_id=%s", (cid,))
        return jsonify(success=True, message="Course deleted!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/enrollments')
def enrollments():
    rows = query_db("""
        SELECT e.enrollment_id, u.name AS student, c.course_name,
               DATE_FORMAT(e.enrollment_date,'%Y-%m-%d') AS enrollment_date
        FROM enrollments e
        JOIN users u ON e.student_id=u.user_id
        JOIN courses c ON e.course_id=c.course_id
        ORDER BY e.enrollment_date DESC
    """)
    students = query_db("SELECT user_id,name FROM users WHERE role='student'")
    course_list = query_db("SELECT course_id,course_name FROM courses")
    return render_template('enrollments.html', enrollments=rows, students=students, courses=course_list)

@app.route('/enrollments/add', methods=['POST'])
def enroll_student():
    sid = request.form['student_id']
    cid = request.form['course_id']
    try:
        mutate_db("INSERT INTO enrollments (student_id,course_id) VALUES (%s,%s)", (sid, cid))
        return jsonify(success=True, message="Student enrolled successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/enrollments/delete/<int:eid>', methods=['POST'])
def delete_enrollment(eid):
    try:
        mutate_db("DELETE FROM enrollments WHERE enrollment_id=%s", (eid,))
        return jsonify(success=True, message="Enrollment removed!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/assignments')
def assignments():
    rows = query_db("""
        SELECT a.assignment_id, c.course_name, a.title, a.max_marks,
               DATE_FORMAT(a.due_date,'%Y-%m-%d') AS due_date
        FROM assignments a JOIN courses c ON a.course_id=c.course_id
        ORDER BY a.due_date DESC
    """)
    course_list = query_db("SELECT course_id,course_name FROM courses")
    return render_template('assignments.html', assignments=rows, courses=course_list)

@app.route('/assignments/add', methods=['POST'])
def add_assignment():
    cid   = request.form['course_id']
    title = request.form['title']
    marks = request.form['max_marks']
    due   = request.form['due_date']
    try:
        mutate_db("INSERT INTO assignments (course_id,title,max_marks,due_date) VALUES (%s,%s,%s,%s)",
                  (cid, title, marks, due))
        return jsonify(success=True, message="Assignment added successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/assignments/delete/<int:aid>', methods=['POST'])
def delete_assignment(aid):
    try:
        mutate_db("DELETE FROM assignments WHERE assignment_id=%s", (aid,))
        return jsonify(success=True, message="Assignment deleted!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/submissions')
def submissions():
    rows = query_db("""
        SELECT s.submission_id, u.name AS student, a.title AS assignment,
               s.marks_obtained, a.max_marks,
               DATE_FORMAT(s.submission_date,'%Y-%m-%d') AS submission_date
        FROM submissions s
        JOIN users u ON s.student_id=u.user_id
        JOIN assignments a ON s.assignment_id=a.assignment_id
        ORDER BY s.submission_date DESC
    """)
    students = query_db("SELECT user_id,name FROM users WHERE role='student'")
    assign_list = query_db("SELECT assignment_id,title FROM assignments")
    return render_template('submissions.html', submissions=rows, students=students, assignments=assign_list)

@app.route('/submissions/add', methods=['POST'])
def add_submission():
    aid   = request.form['assignment_id']
    sid   = request.form['student_id']
    marks = request.form['marks_obtained']
    try:
        mutate_db("INSERT INTO submissions (assignment_id,student_id,submission_date,marks_obtained) VALUES (%s,%s,CURDATE(),%s)",
                  (aid, sid, marks))
        return jsonify(success=True, message="Submission recorded!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/performance')
def performance():
    rows = query_db("""
        SELECT p.performance_id, u.name AS student, c.course_name,
               p.total_marks, p.percentage, p.grade
        FROM performance p
        JOIN users u ON p.student_id=u.user_id
        JOIN courses c ON p.course_id=c.course_id
        ORDER BY p.percentage DESC
    """)
    students = query_db("SELECT user_id,name FROM users WHERE role='student'")
    course_list = query_db("SELECT course_id,course_name FROM courses")
    return render_template('performance.html', performance=rows, students=students, courses=course_list)

@app.route('/performance/update', methods=['POST'])
def update_marks():
    sid   = request.form['student_id']
    cid   = request.form['course_id']
    marks = request.form['total_marks']
    try:
        mutate_db("UPDATE performance SET total_marks=%s WHERE student_id=%s AND course_id=%s",
                  (marks, sid, cid))
        return jsonify(success=True, message="Marks updated successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/performance/add', methods=['POST'])

def add_performance():
    sid   = request.form['student_id']
    cid   = request.form['course_id']
    marks = int(request.form['total_marks'])

    percentage = marks

    if percentage >= 90:
        grade = 'A+'
    elif percentage >= 75:
        grade = 'A'
    elif percentage >= 60:
        grade = 'B'
    elif percentage >= 40:
        grade = 'C'
    else:
        grade = 'F'

    try:
        mutate_db("""
            INSERT INTO performance (student_id, course_id, total_marks, percentage, grade)
            VALUES (%s, %s, %s, %s, %s)
        """, (sid, cid, marks, percentage, grade))

        return jsonify(success=True, message="Performance record added!")

    except Exception as e:
        return jsonify(success=False, message="⚠️ Record already exists or error occurred")

@app.route('/analytics')
def analytics():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT u.name, c.course_name, p.percentage
            FROM performance p
            JOIN users u ON p.student_id=u.user_id
            JOIN courses c ON p.course_id=c.course_id
        """, conn)
        conn.close()

        if df.empty:
            return render_template('analytics.html', charts={}, stats={}, table=[])

        df['status'] = df['percentage'].apply(lambda x: 'Pass' if x >= 40 else 'Fail')

        stats = {
            'avg': round(float(np.mean(df['percentage'])), 2),
            'max': round(float(df['percentage'].max()), 2),
            'min': round(float(df['percentage'].min()), 2),
            'pass_count': int((df['status'] == 'Pass').sum()),
            'fail_count': int((df['status'] == 'Fail').sum()),
            'top_student': df.loc[df['percentage'].idxmax(), 'name'],
        }

        charts = {}

        # Bar chart – avg by course
        fig, ax = plt.subplots(figsize=(8, 4))
        course_avg = df.groupby('course_name')['percentage'].mean()
        bars = ax.bar(course_avg.index, course_avg.values, color='#6C63FF', edgecolor='none')
        ax.set_facecolor('#0d0d1a')
        fig.patch.set_facecolor('#0d0d1a')
        ax.tick_params(colors='#aaa')
        ax.spines[:].set_color('#333')
        ax.set_title('Avg Performance by Course', color='#fff', pad=12)
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                    f'{bar.get_height():.1f}%', ha='center', va='bottom', color='#ccc', fontsize=9)
        buf = io.BytesIO(); plt.tight_layout(); plt.savefig(buf, format='png'); buf.seek(0)
        charts['bar'] = base64.b64encode(buf.read()).decode(); plt.close()

        # Pie chart – pass/fail
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie([stats['pass_count'], stats['fail_count']],
               labels=['Pass', 'Fail'], colors=['#4ade80','#f87171'],
               autopct='%1.1f%%', startangle=140,
               textprops={'color':'#ddd'})
        ax.set_facecolor('#0d0d1a'); fig.patch.set_facecolor('#0d0d1a')
        ax.set_title('Pass / Fail Ratio', color='#fff', pad=12)
        buf = io.BytesIO(); plt.tight_layout(); plt.savefig(buf, format='png'); buf.seek(0)
        charts['pie'] = base64.b64encode(buf.read()).decode(); plt.close()

        # Histogram – percentage distribution
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(df['percentage'], bins=10, color='#f59e0b', edgecolor='#0d0d1a')
        ax.set_facecolor('#0d0d1a'); fig.patch.set_facecolor('#0d0d1a')
        ax.tick_params(colors='#aaa'); ax.spines[:].set_color('#333')
        ax.set_title('Score Distribution', color='#fff', pad=12)
        ax.set_xlabel('Percentage', color='#aaa'); ax.set_ylabel('Count', color='#aaa')
        buf = io.BytesIO(); plt.tight_layout(); plt.savefig(buf, format='png'); buf.seek(0)
        charts['hist'] = base64.b64encode(buf.read()).decode(); plt.close()

        table = df.to_dict(orient='records')
        return render_template('analytics.html', charts=charts, stats=stats, table=table)
    except Exception as e:
        return render_template('analytics.html', charts={}, stats={}, table=[], error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
