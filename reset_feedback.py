import sqlite3

def reset_feedback_db():
    conn = sqlite3.connect("data/feedback.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_feedback_db()
    print("Feedback database has been reset.")
