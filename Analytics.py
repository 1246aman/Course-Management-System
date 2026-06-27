import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Database_Connect import Database

db = Database()


def get_data():
    conn = db.get_connection()

    query = """
    SELECT u.name, c.course_name, p.percentage
    FROM performance p
    JOIN users u ON p.student_id = u.user_id
    JOIN courses c ON p.course_id = c.course_id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def basic_analysis():
    df = get_data()

    print(df)

    print("\nAverage:", np.mean(df['percentage']))

    print("\nTop Student:")
    print(df[df['percentage'] == df['percentage'].max()])



def add_status():
    df = get_data()

    df['status'] = df['percentage'].apply(
        lambda x: 'Pass' if x >= 40 else 'Fail'
    )

    print(df)



def plot_graph():
    df = get_data()

    data = df.groupby('course_name')['percentage'].mean()

    data.plot(kind='bar')
    plt.title("Course Performance")
    plt.show()