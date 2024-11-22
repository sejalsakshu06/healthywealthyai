import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import random
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# === API Configuration ===
OPENWEATHER_API_KEY = "your_openweather_api_key"  # Replace with your API key
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

DB_FILE = "health_tracker.db"


# === Database Setup ===
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            water_intake REAL,
            sleep_hours REAL,
            exercise_minutes REAL
        )
    """)
    conn.commit()
    conn.close()


# === Data Management ===
def fetch_data_by_date_range(start_date, end_date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT date, water_intake, sleep_hours, exercise_minutes 
        FROM health_data 
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """
    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()
    conn.close()
    return data


def fetch_weekly_averages():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT AVG(water_intake) AS avg_water,
               AVG(sleep_hours) AS avg_sleep,
               AVG(exercise_minutes) AS avg_exercise
        FROM health_data
        WHERE date >= date('now', '-7 days')
    """
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return {
        "avg_water": result[0] if result[0] else 0,
        "avg_sleep": result[1] if result[1] else 0,
        "avg_exercise": result[2] if result[2] else 0
    }


# === Feedback and Utilities ===
def exercise_feedback(exercise_minutes):
    if exercise_minutes < 30:
        return "Try to get at least 30 minutes of exercise today to stay active and healthy."
    elif 30 <= exercise_minutes < 60:
        return "Great job! You're staying active. Try to push yourself for 60 minutes next time!"
    else:
        return "Excellent! You're hitting your exercise goals. Keep it up!"


def sleep_feedback(sleep_hours):
    if sleep_hours < 7:
        return "Sleep is crucial for recovery. Try to aim for 7-9 hours of sleep each night for better health."
    elif 7 <= sleep_hours <= 9:
        return "Great job! You're getting a healthy amount of sleep. Keep it up!"
    else:
        return "You’re sleeping well! Just make sure not to oversleep as it may affect your productivity."


def generate_health_tip():
    tips = [
        "Stay consistent with your exercise routine!",
        "Drink water regularly to keep yourself hydrated.",
        "Incorporate more fruits and vegetables into your meals.",
        "Take short breaks during work to stretch and relax.",
        "Prioritize a good night's sleep for better health."
    ]
    return random.choice(tips)


def get_weather(city):
    try:
        response = requests.get(WEATHER_API_URL.format(city=city, api_key=OPENWEATHER_API_KEY))
        data = response.json()
        if response.status_code == 200:
            return data['main']['temp'], data['weather'][0]['description']
        else:
            return None, "Unable to fetch weather data"
    except:
        return None, "Weather API Error"


def visualize_data():
    start_date = "2024-01-01"  # Example range
    end_date = datetime.now().strftime("%Y-%m-%d")
    data = fetch_data_by_date_range(start_date, end_date)

    if not data:
        messagebox.showerror("Error", "No data available for the selected date range.")
        return

    dates = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d-%b") for row in data]
    water = [row[1] for row in data]
    sleep = [row[2] for row in data]
    exercise = [row[3] for row in data]

    fig, ax = plt.subplots(3, 1, figsize=(8, 12))

    # Line graph for Water Intake
    ax[0].plot(dates, water, marker='o', color='blue', linestyle='-', label="Water Intake")
    ax[0].set_title("Water Intake (Liters)")
    ax[0].set_ylabel("Liters")
    ax[0].legend()
    ax[0].grid(True)

    # Line graph for Sleep Hours
    ax[1].plot(dates, sleep, marker='o', color='green', linestyle='-', label="Sleep Hours")
    ax[1].set_title("Sleep Hours")
    ax[1].set_ylabel("Hours")
    ax[1].legend()
    ax[1].grid(True)

    # Line graph for Exercise Minutes
    ax[2].plot(dates, exercise, marker='o', color='orange', linestyle='-', label="Exercise Minutes")
    ax[2].set_title("Exercise Minutes")
    ax[2].set_ylabel("Minutes")
    ax[2].legend()
    ax[2].grid(True)

    plt.tight_layout()

    # Display the chart in Tkinter
    window = tk.Toplevel()
    window.title("Health Metrics Visualization")
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()


# === Tkinter GUI ===
def main_window():
    root = tk.Tk()
    root.title("Personal Health Tracker")
    root.geometry("600x500")

    # Dynamic Greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning! Start your day with positivity!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon! Keep going, you're doing great!"
    else:
        greeting = "Good Evening! Relax and recharge for tomorrow."

    tk.Label(root, text=greeting, font=("Arial", 14, "bold")).pack(pady=10)

    # Date Picker
    tk.Label(root, text="Select Date:").pack()
    date_entry = DateEntry(root, width=12, background="darkblue", foreground="white", borderwidth=2)
    date_entry.pack(pady=5)

    # Input Fields
    tk.Label(root, text="Water Intake (Liters):").pack()
    water_entry = tk.Entry(root)
    water_entry.pack()

    tk.Label(root, text="Sleep Hours:").pack()
    sleep_entry = tk.Entry(root)
    sleep_entry.pack()

    tk.Label(root, text="Exercise Minutes:").pack()
    exercise_entry = tk.Entry(root)
    exercise_entry.pack()

    # Submit Button
    def submit_data():
        try:
            water = float(water_entry.get())
            sleep = float(sleep_entry.get())
            exercise = float(exercise_entry.get())

            feedback = exercise_feedback(exercise)
            sleep_feedback_message = sleep_feedback(sleep)

            messagebox.showinfo("Exercise Feedback", feedback)
            messagebox.showinfo("Sleep Feedback", sleep_feedback_message)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    tk.Button(root, text="Submit", command=submit_data).pack(pady=10)

    # Weekly Averages
    def show_weekly_averages():
        averages = fetch_weekly_averages()
        avg_message = (
            f"Weekly Averages:\n\n"
            f"Water Intake: {averages['avg_water']:.2f} L/day\n"
            f"Sleep Hours: {averages['avg_sleep']:.2f} hours/day\n"
            f"Exercise Minutes: {averages['avg_exercise']:.2f} mins/day"
        )
        messagebox.showinfo("Weekly Averages", avg_message)

    tk.Button(root, text="View Weekly Averages", command=show_weekly_averages).pack(pady=10)
    tk.Button(root, text="Visualize Data", command=visualize_data).pack(pady=10)

    # Health Tip
    tk.Label(root, text="Daily Health Tip:", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(root, text=generate_health_tip(), font=("Arial", 10)).pack(pady=5)

    # Weather Section
    tk.Label(root, text="Enter Your City for Weather Info:").pack(pady=5)
    city_entry = tk.Entry(root)
    city_entry.pack()

    def show_weather():
        city = city_entry.get()
        temp, description = get_weather(city)
        if temp:
            weather_message = f"Current temperature in {city}: {temp}°C\nWeather: {description.capitalize()}"
        else:
            weather_message = description
        messagebox.showinfo("Weather Info", weather_message)

    tk.Button(root, text="Get Weather Info", command=show_weather).pack(pady=10)

    root.mainloop()


# === Program Entry Point ===
if __name__ == "__main__":
    initialize_database()
    main_window()
