from Analytics import basic_analysis, add_status, plot_graph
from Database_Connect import User, UserService
service = UserService()


while True:
    print("\n1. Add User")
    print("2. View Users")
    print("3. Update Marks")
    print("4. Delete User")
    print("5. Enroll Student")
    print("6. View Enrollments")
    print("7. Add Assignment")
    print("8. Add Submission")
    print("9. View Performance")
    print("10. Analytics")
    print("11. Show Graph")
    print("12. Exit")

    choice = input("Enter choice: ")

    if choice == '1':
        name = input("Name: ")
        email = input("Email: ")
        role = input("Role: ")

        user = User(name, email, role)   
        service.add_user(user)

    elif choice == '2':
        service.view_users()

    elif choice == '3':
        sid = int(input("Student ID: "))
        cid = int(input("Course ID: "))
        marks = int(input("Marks: "))
        service.update_marks(sid, cid, marks)

    elif choice == '4':
        uid = int(input("User ID: "))
        service.delete_user(uid)

    elif choice == '5':
        sid = int(input("Student ID: "))
        cid = int(input("Course ID: "))
        service.enroll_student(sid, cid)
        break

    elif choice == '6':
        service.view_enrollments()

    elif choice == '7':
        cid = int(input("Course ID: "))
        title = input("Title: ")
        marks = int(input("Max Marks: "))
        due = input("Due Date (YYYY-MM-DD): ")
        service.add_assignment(cid, title, marks, due)

    elif choice == '8':
        aid = int(input("Assignment ID: "))
        sid = int(input("Student ID: "))
        marks = int(input("Marks: "))
        service.add_submission(aid, sid, marks)

    elif choice == '9':
        service.view_performance()

    elif choice == '10':
        basic_analysis()
        add_status()

    elif choice == '11':
        plot_graph()

    elif choice == '12':
        break

    else:
        print("Invalid choice")