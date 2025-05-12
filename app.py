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
    
    user_id = session['user_id']
    print(f"Loading dashboard for user_id: {user_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user's name
        cursor.execute("SELECT Name FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        print(f"Found user: {user}")
        
        # Get user's created events
        cursor.execute("""
            SELECT Events.*, Venues.Name AS VenueName
            FROM Events
            LEFT JOIN Venues ON Events.VenueID = Venues.VenueID
            WHERE Events.UserID = %s
        """, (user_id,))
        created_events = cursor.fetchall()
        print(f"Found {len(created_events)} created events")
        
        # Get user's invited events
        cursor.execute("""
            SELECT Events.*, Venues.Name AS VenueName
            FROM Events
            LEFT JOIN Venues ON Events.VenueID = Venues.VenueID
            JOIN Invites ON Events.EventID = Invites.EventID
            WHERE Invites.UserID = %s
        """, (user_id,))
        invited_events = cursor.fetchall()
        print(f"Found {len(invited_events)} invited events")
        
        # Combine events, removing duplicates
        all_events = created_events + invited_events
        unique_events = {event['EventID']: event for event in all_events}.values()
        events = list(unique_events)
        print(f"Total unique events: {len(events)}")
        
        # Get user's invites
        cursor.execute("""
            SELECT Invites.InviteID AS invite_id, Events.Name AS event_name, Invites.RecipientStatus AS status
            FROM Invites
            JOIN Events ON Invites.EventID = Events.EventID
            WHERE Invites.UserID = %s
        """, (user_id,))
        invites = cursor.fetchall()
        print(f"Found {len(invites)} invites")
        
        conn.close()
        return render_template('dashboard.html', 
                             user_name=user['Name'],
                             user_events=events,
                             invites=invites)
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        return f"Error loading dashboard: {str(e)}"

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
        try:
            event_name = request.form['name']
            date = request.form['date']
            description = request.form['description']
            theme = request.form['theme']
            venue_id = request.form['venue_id']
            user_id = session['user_id']

            # Debug print
            print(f"Creating event with data: name={event_name}, date={date}, user_id={user_id}")

            # Step 1: Insert the event into the Events table
            cursor.execute('''
                INSERT INTO Events (UserID, VenueID, Name, Date, Description, Theme)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, venue_id, event_name, date, description, theme))
            conn.commit()

            # Step 2: Get the EventID of the newly created event
            event_id = cursor.lastrowid
            print(f"Created event with ID: {event_id}")

            # Step 3: Handle invites for users selected in the form
            invite_users = request.form.getlist('invite_users')
            print(f"Inviting users: {invite_users}")
            
            for invite_user_id in invite_users:
                cursor.execute('''
                    INSERT INTO Invites (UserID, EventID, DateSent, Text, RecipientStatus)
                    VALUES (%s, %s, NOW(), %s, 'Pending')
                ''', (invite_user_id, event_id, f"You're invited to {event_name}"))
                conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return f"Error creating event: {str(e)}"

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

@app.route('/event/<int:event_id>')
def event_details(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get event details with creator name and venue name
        cursor.execute("""
            SELECT e.*, u.Name as CreatorName, v.Name as VenueName
            FROM Events e
            JOIN Users u ON e.UserID = u.UserID
            LEFT JOIN Venues v ON e.VenueID = v.VenueID
            WHERE e.EventID = %s
        """, (event_id,))
        event = cursor.fetchone()
        
        if not event:
            return "Event not found", 404
        
        # Get attendees and their status
        cursor.execute("""
            SELECT u.Name, i.RecipientStatus as Status
            FROM Invites i
            JOIN Users u ON i.UserID = u.UserID
            WHERE i.EventID = %s
        """, (event_id,))
        attendees = cursor.fetchall()
        
        # Check if current user is the creator
        is_creator = event['UserID'] == session['user_id']
        
        conn.close()
        return render_template('event_details.html', 
                             event=event,
                             attendees=attendees,
                             is_creator=is_creator)
    except Exception as e:
        print(f"Error loading event details: {str(e)}")
        return f"Error loading event details: {str(e)}"

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get event details
        cursor.execute("""
            SELECT * FROM Events WHERE EventID = %s
        """, (event_id,))
        event = cursor.fetchone()
        
        if not event:
            return "Event not found", 404
            
        # Check if user is the creator
        if event['UserID'] != session['user_id']:
            return "You don't have permission to edit this event", 403
            
        if request.method == 'POST':
            # Update event
            cursor.execute("""
                UPDATE Events 
                SET Name = %s, Date = %s, Description = %s, Theme = %s, VenueID = %s
                WHERE EventID = %s
            """, (
                request.form['name'],
                request.form['date'],
                request.form['description'],
                request.form['theme'],
                request.form['venue_id'],
                event_id
            ))
            
            # Handle new invites
            new_invites = request.form.getlist('new_invites')
            for user_id in new_invites:
                cursor.execute("""
                    INSERT INTO Invites (UserID, EventID, DateSent, Text, RecipientStatus)
                    VALUES (%s, %s, NOW(), %s, 'Pending')
                """, (user_id, event_id, f"You're invited to {request.form['name']}"))
            
            conn.commit()
            return redirect(url_for('event_details', event_id=event_id))
            
        # GET: Show edit form
        cursor.execute("SELECT * FROM Venues")
        venues = cursor.fetchall()
        
        # Get current invites
        cursor.execute("""
            SELECT u.UserID, u.Name, i.RecipientStatus as Status
            FROM Invites i
            JOIN Users u ON i.UserID = u.UserID
            WHERE i.EventID = %s
        """, (event_id,))
        current_invites = cursor.fetchall()
        
        # Get available users (excluding current invites)
        cursor.execute("""
            SELECT UserID, Name FROM Users 
            WHERE UserID NOT IN (
                SELECT UserID FROM Invites WHERE EventID = %s
            ) AND UserID != %s
        """, (event_id, session['user_id']))
        available_users = cursor.fetchall()
        
        conn.close()
        return render_template('edit_event.html', 
                             event=event, 
                             venues=venues,
                             current_invites=current_invites,
                             available_users=available_users)
        
    except Exception as e:
        print(f"Error editing event: {str(e)}")
        return f"Error editing event: {str(e)}"

@app.route('/remove_invite/<int:user_id>/<int:event_id>')
def remove_invite(user_id, event_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify user is the event creator
        cursor.execute("SELECT UserID FROM Events WHERE EventID = %s", (event_id,))
        event = cursor.fetchone()
        
        if not event or event['UserID'] != session['user_id']:
            return "You don't have permission to remove invites", 403
            
        # Remove the invite
        cursor.execute("""
            DELETE FROM Invites 
            WHERE UserID = %s AND EventID = %s
        """, (user_id, event_id))
        
        conn.commit()
        conn.close()
        return redirect(url_for('edit_event', event_id=event_id))
        
    except Exception as e:
        print(f"Error removing invite: {str(e)}")
        return f"Error removing invite: {str(e)}"

@app.route('/register-business', methods=['GET'])
def register_business_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('register_business.html')

@app.route('/register_business', methods=['POST'])
def register_business():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    business_type = request.form['business_type']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if business_type == 'vendor':
            # Insert new vendor
            cursor.execute('''
                INSERT INTO Vendors (Name, ServiceType, Owner, StaffCount, PhoneNumber)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                request.form['name'],
                request.form['service_type'],
                request.form['owner'],
                request.form['staff_count'],
                request.form['phone_number']
            ))
        elif business_type == 'venue':
            # Insert new venue
            cursor.execute('''
                INSERT INTO Venues (Name, Location, Capacity, Type)
                VALUES (%s, %s, %s, %s)
            ''', (
                request.form['name'],
                request.form['location'],
                request.form['capacity'],
                request.form['venue_type']
            ))
            
        conn.commit()
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error registering business: {str(e)}")
        return f"Error registering business: {str(e)}"
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
