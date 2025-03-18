from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
import sqlite3
import plotly.express as px
import json

app = Flask(__name__)

# Load and Clean Data
def load_and_clean_data():
    file_path = "data/RCD06.20250317132007.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.rename(columns={"year": "year", "type_of_offence": "type_of_offence", "garda_region": "garda_region", "value": "value"})
    df = df.dropna(subset=["year", "type_of_offence", "garda_region", "value"])
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

@app.route("/")
def home():
    crime_types = df["type_of_offence"].unique().tolist()
    crime_data = df.to_dict(orient="records")
    return render_template("index.html", crime_types=crime_types, crime_data=crime_data)

@app.route("/bar_chart_data")
def bar_chart_data():
    year = request.args.get('year', type=int)
    crime_type = request.args.get('type')
    query_data = df
    if year:
        query_data = query_data[query_data['year'] == year]
    if crime_type and crime_type != 'All Types':
        query_data = query_data[query_data['type_of_offence'] == crime_type]
    crime_summary = query_data.groupby("garda_region")["value"].sum().reset_index()
    return jsonify(crime_summary.to_dict(orient="records"))

@app.route("/crime_pie_chart")
def crime_pie_chart():
    year = request.args.get('year', type=int)
    crime_type = request.args.get('type')
    query_data = df
    if year:
        query_data = query_data[query_data['year'] == year]
    if crime_type and crime_type != 'All Types':
        query_data = query_data[query_data['type_of_offence'] == crime_type]

    crime_by_type = query_data.groupby("type_of_offence")["value"].sum().reset_index()
    fig = px.pie(crime_by_type, values="value", names="type_of_offence", title="Crime Distribution by Type")
    return jsonify(json.loads(fig.to_json()))


@app.route("/line_chart_data")
def line_chart_data():
    year = request.args.get('year', type=int)  # Gets year from query string, if present
    crime_type = request.args.get('type')  # Gets crime type from query string, if present

    # Start with all data
    query_data = df

    # Filter data based on year if provided
    if year:
        query_data = query_data[query_data['year'] == year]

    # Filter data based on crime type if provided
    if crime_type and crime_type != 'All Types':
        query_data = query_data[query_data['type_of_offence'] == crime_type]

    crime_trend = query_data.groupby(["year", "garda_region"])["value"].sum().reset_index()
    return jsonify(crime_trend.to_dict(orient="records"))





@app.route("/feedback", methods=["GET"])
def feedback():
    return render_template("feedback.html", regions=df["garda_region"].unique())

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

@app.route("/feedback_summary")
def feedback_summary():
    conn = sqlite3.connect("data/feedback.db")
    df_feedback = pd.read_sql_query("SELECT region, AVG(concern) as avg_concern FROM feedback GROUP BY region", conn)
    conn.close()
    return render_template("feedback_summary.html", table=df_feedback.to_html(classes="table table-striped"))

@app.route("/recommendations")
def recommendations():
    conn = sqlite3.connect("data/feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT region, AVG(concern) as avg_concern FROM feedback GROUP BY region HAVING AVG(concern) >= 7")
    high_concern_areas = cursor.fetchall()
    conn.close()
    regions = [area[0] for area in high_concern_areas]
    concerns = [area[1] for area in high_concern_areas]
    return render_template("recommendations.html", regions=regions, concerns=concerns)

@app.route("/charts")
def charts():
    years = df["year"].unique().tolist()
    crime_types = df["type_of_offence"].unique().tolist()
    return render_template("charts.html", years=years, crime_types=crime_types)

if __name__ == "__main__":
    app.run(debug=True)
