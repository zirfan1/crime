from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
import sqlite3
import plotly.express as px

app = Flask(__name__)

# Load and Clean Data
def load_and_clean_data():
    file_path = "data/RCD06.20250317132007.csv"  
    df = pd.read_csv(file_path)

    # Rename columns to lowercase with underscores
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Select relevant columns and rename for clarity
    df = df.rename(columns={
        "year": "year",
        "type_of_offence": "type_of_offence",
        "garda_region": "garda_region",
        "value": "value"
    })

    # Remove missing values
    df = df.dropna(subset=["year", "type_of_offence", "garda_region", "value"])

    # Ensure numeric values for crime statistics
    df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0).astype(int)

    return df

df = load_and_clean_data()

# Initialize SQLite Database for Feedback
def init_db():
    conn = sqlite3.connect("data/feedback.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            concern INTEGER NOT NULL CHECK(concern BETWEEN 1 AND 10)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home Page - Display Crime Summary & Charts
@app.route("/")
def home():
    crime_summary = df.groupby("garda_region")["value"].sum().reset_index()
    table = crime_summary.to_html(classes="table table-striped", index=False)

    # Pass data to charts
    crime_types = df["type_of_offence"].unique().tolist()
    crime_data = df.to_dict(orient="records")

    return render_template("index.html", table=table, crime_types=crime_types, crime_data=crime_data)

# Interactive Bar Chart Data
@app.route("/bar_chart_data")
def bar_chart_data():
    crime_summary = df.groupby("garda_region")["value"].sum().reset_index()
    return jsonify(crime_summary.to_dict(orient="records"))

# 📌 Updated Pie Chart with Smooth Transitions
@app.route("/crime_pie_chart")
def crime_pie_chart():
    # Aggregate crime data by type
    crime_by_type = df.groupby("type_of_offence")["value"].sum().reset_index()

    # Create an interactive pie chart with animations
    fig = px.pie(crime_by_type, 
                 values="value", 
                 names="type_of_offence", 
                 title="Crime Distribution by Type",
                 hole=0.4,  # Creates a donut effect
                 labels={"type_of_offence": "Crime Type"},
                 template="plotly_dark")

    # Enable smooth transitions and animations
    fig.update_traces(
        textinfo="percent+label",
        pull=[0.05] * len(crime_by_type),
        hoverinfo="label+percent",
        marker=dict(line=dict(color="#000000", width=2)),  # Add smooth boundaries
    )

    fig.update_layout(
        transition={"duration": 800, "easing": "cubic-in-out"},
        legend_title="Crime Categories"
    )

    return jsonify(fig.to_json())

# Feedback Page
@app.route("/feedback", methods=["GET"])
def feedback():
    return render_template("feedback.html", regions=df["garda_region"].unique())

# Submit Feedback
@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    name = request.form["name"]
    region = request.form["region"]
    concern = int(request.form["concern"])

    conn = sqlite3.connect("data/feedback.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (name, region, concern) VALUES (?, ?, ?)", (name, region, concern))
    conn.commit()
    conn.close()

    return redirect("/feedback_summary")

# Display Feedback Summary
@app.route("/feedback_summary")
def feedback_summary():
    conn = sqlite3.connect("data/feedback.db")
    df_feedback = pd.read_sql_query("SELECT region, AVG(concern) as avg_concern FROM feedback GROUP BY region", conn)
    conn.close()

    return render_template("feedback_summary.html", table=df_feedback.to_html(classes="table table-striped"))

# Crime Safety Recommendations
@app.route("/recommendations")
def recommendations():
    conn = sqlite3.connect("data/feedback.db")
    df_feedback = pd.read_sql_query("SELECT region, AVG(concern) as avg_concern FROM feedback GROUP BY region", conn)
    conn.close()

    high_concern_areas = df_feedback[df_feedback["avg_concern"] >= 7]["region"].tolist()

    recommendations_text = "<p>Areas with high concern: " + ", ".join(high_concern_areas) + "</p>" if high_concern_areas else "<p>No high concern areas identified yet.</p>"

    return render_template("recommendations.html", recommendations=recommendations_text)

# Charts Page - Displays Graphs
@app.route("/charts")
def charts():
    years = df["year"].unique().tolist()
    crime_types = df["type_of_offence"].unique().tolist()
    return render_template("charts.html", years=years, crime_types=crime_types)

if __name__ == "__main__":
    app.run(debug=True)
