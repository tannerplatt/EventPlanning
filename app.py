#flask application for event planning system
from flask import Flask, render_template, request, redirect, url_for, session
from db_config import get_db_connection

#initialize flask application
app = Flask(__name__)
app.secret_key = 'EVENT1!'  #secret key for session management

#route for home page redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

#route for login/logout functionality
@app.route('/login', methods=['GET', 'POST'])
def login():
    #handle logout clears session and redirects to login page
    if request.method == 'GET' and 'user_id' in session:
        session.pop('user_id', None)
        return redirect(url_for('login'))
        
    #handle login validates email and creates session
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        #query database for user with matching email
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            #create session for authenticated user
            session['user_id'] = user['UserID']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email"
    return render_template('login.html')

#route for user dashboard displays user's events and invites
@app.route('/dashboard')
def dashboard():
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    print(f"Loading dashboard for user_id: {user_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        #get user's basic information
        cursor.execute("SELECT Name FROM Users WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        print(f"Found user: {user}")
        
        #get events created by user
        cursor.execute("""
            SELECT Events.*, Venues.Name AS VenueName
            FROM Events
            LEFT JOIN Venues ON Events.VenueID = Venues.VenueID
            WHERE Events.UserID = %s
        """, (user_id,))
        created_events = cursor.fetchall()
        print(f"Found {len(created_events)} created events")
        
        #get events where user is invited
        cursor.execute("""
            SELECT Events.*, Venues.Name AS VenueName
            FROM Events
            LEFT JOIN Venues ON Events.VenueID = Venues.VenueID
            JOIN Invites ON Events.EventID = Invites.EventID
            WHERE Invites.UserID = %s
        """, (user_id,))
        invited_events = cursor.fetchall()
        print(f"Found {len(invited_events)} invited events")
        
        #combine and deduplicate events
        all_events = created_events + invited_events
        unique_events = {event['EventID']: event for event in all_events}.values()
        events = list(unique_events)
        print(f"Total unique events: {len(events)}")
        
        #get user's pending invites
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

#route for viewing and managing invites
@app.route('/invites')
def invites():
    #check if user is logged in
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #get all invites for the user with event details
    cursor.execute("""
        SELECT Invites.InviteID, Events.Name AS EventName, Invites.DateSent, Invites.Text, Invites.RecipientStatus
        FROM Invites
        JOIN Events ON Invites.EventID = Events.EventID
        WHERE Invites.UserID = %s
    """, (user_id,))
    invites = cursor.fetchall()
    conn.close()
    return render_template('invites.html', invites=invites)

#route for responding to event invites
@app.route('/respond_invite/<int:invite_id>/<status>')
def respond_invite(invite_id, status):
    #update invite status in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Invites SET RecipientStatus = %s WHERE InviteID = %s", (status, invite_id))
    conn.commit()
    conn.close()
    return redirect(url_for('invites'))

#route for creating new events
@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            #get form data for new event
            event_name = request.form['name']
            date = request.form['date']
            description = request.form['description']
            theme = request.form['theme']
            venue_id = request.form['venue_id']
            user_id = session['user_id']

            #debug print
            print(f"Creating event with data: name={event_name}, date={date}, user_id={user_id}")

            #create new event in database
            cursor.execute('''
                INSERT INTO Events (UserID, VenueID, Name, Date, Description, Theme)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, venue_id, event_name, date, description, theme))
            conn.commit()

            #get id of newly created event
            event_id = cursor.lastrowid
            print(f"Created event with ID: {event_id}")

            #create invites for selected users
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

    #get: show event creation form
    #get list of available venues
    cursor.execute('SELECT * FROM Venues')
    venues = cursor.fetchall()

    #get list of users for invites
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('create_event.html', venues=venues, users=users)

#route for user registration
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        #get registration form data
        new_name = request.form['new_name']
        new_age = request.form['new_age']
        new_email = request.form['new_email']
        new_number = request.form['new_number']

        #check for existing user with same email
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (new_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "This email is already in use. Please log in."

        #create new user in database
        cursor.execute('''
            INSERT INTO Users (Name, Age, Email, Number)
            VALUES (%s, %s, %s, %s)
        ''', (new_name, new_age, new_email, new_number))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('login'))

#route for viewing available vendors
@app.route('/vendors')
def vendors():
    #get all vendors from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Vendors")
    vendors = cursor.fetchall()
    conn.close()
    return render_template('vendors.html', vendors=vendors)

#route for viewing all events
@app.route('/events')
def events():
    #get all events with venue information
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

#route for viewing event details
@app.route('/event/<int:event_id>')
def event_details(event_id):
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        #get detailed event information including creator and venue
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
        
        #get list of attendees and their status
        cursor.execute("""
            SELECT u.Name, i.RecipientStatus as Status
            FROM Invites i
            JOIN Users u ON i.UserID = u.UserID
            WHERE i.EventID = %s
        """, (event_id,))
        attendees = cursor.fetchall()
        
        #check if current user is event creator
        is_creator = event['UserID'] == session['user_id']
        
        conn.close()
        return render_template('event_details.html', 
                             event=event,
                             attendees=attendees,
                             is_creator=is_creator)
    except Exception as e:
        print(f"Error loading event details: {str(e)}")
        return f"Error loading event details: {str(e)}"

#route for editing existing events
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        #get event details
        cursor.execute("""
            SELECT * FROM Events WHERE EventID = %s
        """, (event_id,))
        event = cursor.fetchone()
        
        if not event:
            return "Event not found", 404
            
        #verify user has permission to edit
        if event['UserID'] != session['user_id']:
            return "You don't have permission to edit this event", 403
            
        if request.method == 'POST':
            #update event information
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
            
            #handle new invites
            new_invites = request.form.getlist('new_invites')
            for user_id in new_invites:
                cursor.execute("""
                    INSERT INTO Invites (UserID, EventID, DateSent, Text, RecipientStatus)
                    VALUES (%s, %s, NOW(), %s, 'Pending')
                """, (user_id, event_id, f"You're invited to {request.form['name']}"))
            
            conn.commit()
            return redirect(url_for('event_details', event_id=event_id))
            
        #get available venues
        cursor.execute("SELECT * FROM Venues")
        venues = cursor.fetchall()
        
        #get current invites
        cursor.execute("""
            SELECT u.UserID, u.Name, i.RecipientStatus as Status
            FROM Invites i
            JOIN Users u ON i.UserID = u.UserID
            WHERE i.EventID = %s
        """, (event_id,))
        current_invites = cursor.fetchall()
        
        #get users available for new invites
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

#route for removing invites
@app.route('/remove_invite/<int:user_id>/<int:event_id>')
def remove_invite(user_id, event_id):
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        #verify user has permission to remove invites
        cursor.execute("SELECT UserID FROM Events WHERE EventID = %s", (event_id,))
        event = cursor.fetchone()
        
        if not event or event['UserID'] != session['user_id']:
            return "You don't have permission to remove invites", 403
            
        #remove the invite from database
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

#route for business registration page
@app.route('/register-business', methods=['GET'])
def register_business_page():
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('register_business.html')

#route for processing business registration
@app.route('/register_business', methods=['POST'])
def register_business():
    #check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    business_type = request.form['business_type']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if business_type == 'vendor':
            #insert new vendor into database
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
            #insert new venue into database
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

#run the application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
