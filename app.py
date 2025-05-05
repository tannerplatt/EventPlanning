from flask import Flask, render_template, request, redirect, url_for, session
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'EVENT1!'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['UserID']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Events WHERE UserID = %s", (session['user_id'],))
    events = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', events=events)

@app.route('/invites')
def invites():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Invites.InviteID, Events.Name AS EventName, Invites.DateSent, Invites.Text, Invites.RecipientStatus
        FROM Invites
        JOIN Events ON Invites.EventID = Events.EventID
        WHERE Invites.UserID = %s
    """, (user_id,))
    invites = cursor.fetchall()
    conn.close()
    return render_template('invites.html', invites=invites)


@app.route('/respond_invite/<int:invite_id>/<status>')
def respond_invite(invite_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Invites SET RecipientStatus = %s WHERE InviteID = %s", (status, invite_id))
    conn.commit()
    conn.close()
    return redirect(url_for('invites'))

@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        event_name = request.form['name']
        date = request.form['date']
        description = request.form['description']
        theme = request.form['theme']
        venue_id = request.form['venue_id']
        user_id = session['user_id']

        # Step 1: Insert the event into the Events table
        cursor.execute('''
            INSERT INTO Events (UserID, VenueID, Name, Date, Description, Theme)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, venue_id, event_name, date, description, theme))
        conn.commit()

        # Step 2: Get the EventID of the newly created event
        event_id = cursor.lastrowid

        # Step 3: Handle invites for users selected in the form
        invite_users = request.form.getlist('invite_users')
        for invite_user_id in invite_users:
            cursor.execute('''
                INSERT INTO Invites (UserID, EventID, DateSent, Text, RecipientStatus)
                VALUES (%s, %s, NOW(), %s, 'Pending')
            ''', (invite_user_id, event_id, f"You're invited to {event_name}"))
            conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))

    # GET: Show form
    cursor.execute('SELECT * FROM Venues')
    venues = cursor.fetchall()

    # Get the list of all users to invite
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('create_event.html', venues=venues, users=users)

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # Get user inputs
        new_name = request.form['new_name']
        new_age = request.form['new_age']
        new_email = request.form['new_email']
        new_number = request.form['new_number']

        # Check if user already exists with this email
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (new_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "This email is already in use. Please log in."

        # Insert new user into the Users table
        cursor.execute('''
            INSERT INTO Users (Name, Age, Email, Number)
            VALUES (%s, %s, %s, %s)
        ''', (new_name, new_age, new_email, new_number))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('login'))




@app.route('/vendors')
def vendors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Vendors")
    vendors = cursor.fetchall()
    conn.close()
    return render_template('vendors.html', vendors=vendors)


@app.route('/events')
def events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Events.*, Venues.Name AS VenueName
        FROM Events
        JOIN Venues ON Events.VenueID = Venues.VenueID
    """)
    events = cursor.fetchall()
    conn.close()
    return render_template('events.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)
