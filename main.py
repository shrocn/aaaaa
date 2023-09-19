from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

def load_users():
    users = {}  # Use a dictionary to store usernames, passwords, and roles
    with open('users.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_data = {
                "password": row['password'],
                "role": row['role']  # Store the user's role
            }
            users[row['username']] = user_data  # Store username, password, and role in the dictionary
    return users
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and users[username]["password"] == password:
            session["username"] = username

            # Check if the user is an admin
            if users[username]["role"] == "admin":
                return redirect(url_for("admin"))  # Redirect to admin page
            else:
                return redirect(url_for("index"))  # Redirect to regular user page

        else:
            return render_template('login.html', error_message='Incorrect username or password, please try again')

    return render_template("login.html")


# Create a route for the admin dashboard
@app.route("/admin")
def admin():
    # Check if the user is an admin (you can also use session data to determine this)
    if "username" in session:
        username = session["username"]
        users = load_users()
        if username in users and users[username]["role"] == "admin":

            # Read the content of newusers.csv
            newusers_data = []
            with open('newusers.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    newusers_data.append(row)

            return render_template("admin.html", newusers_data=newusers_data)

    # If the user is not an admin or not logged in, redirect them to the regular login page
    return redirect(url_for("login"))

@app.route('/staff-tasks', methods=['POST'])
def staff_tasks():
    if 'csvFile' not in request.files:
        return render_template('admin.html', error_message='No file part')

    csv_file = request.files['csvFile']

    if csv_file.filename == '':
        return render_template('admin.html', error_message='No selected file')

    if csv_file:
        # Read the CSV data and convert it to a list of dictionaries
        csv_data = []
        csv_text = csv_file.read().decode('utf-8')  # Read the file as text

        csv_reader = csv.DictReader(csv_text.splitlines())
        for row in csv_reader:
            csv_data.append(row)

        return render_template('admin.html', staff_tasks=csv_data)

    return render_template('admin.html')


# Create a separate admin dashboard template (admin_dashboard.html)
# You can customize this page for your admin users.
@app.route('/create')
def create_account_page():
    return render_template('create.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Section 1: Title and Subtitle
    title = 'Handheld Cube Satellite Experiment'
    subtitle = 'Changes in Altitude'

    return render_template('index.html', title=title, subtitle=subtitle)

@app.route('/create', methods=['POST'])
def create():
    username = request.form.get('username')
    password = request.form.get('password')

    # Basic validation, you can add more robust validation here
    users = load_users()
    if username in users:
        # Return an error message or perform appropriate action
        return render_template('create.html', error_message='Username already exists')

    # Save to CSV if validation passes
    # First CSV file
    with open('users.csv', 'a', newline='') as csvfile1:
        csv_writer1 = csv.writer(csvfile1)
        csv_writer1.writerow([username, password])

    # Second CSV file
    with open('newusers.csv', 'a', newline='') as csvfile2:
        csv_writer2 = csv.writer(csvfile2)
        csv_writer2.writerow([username, password])

        # Redirect to the survey page after successful account creation
        return redirect(url_for("survey"))


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == "POST":
        # Process the survey form data here
        question1_response = request.form["question1"]
        question2_response = request.form["question2"]

        # Write the responses to a file
        with open("survey_responses.txt", "a") as file:
            file.write(f"Question 1 Response: {question1_response}\n")
            file.write(f"Question 2 Response: {question2_response}\n")

        # You can store the survey data in a database or perform other actions

        # After processing the survey, redirect the user to the index page or any other desired page
        return redirect(url_for("index"))

    # Render the survey form HTML template if it's a GET request
    return render_template("survey.html")


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
