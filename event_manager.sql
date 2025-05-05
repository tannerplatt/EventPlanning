-- Create database for final project
CREATE DATABASE IF NOT EXISTS event_manager;
USE event_manager;

-- Users table
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Age INT,
    Email VARCHAR(100),
    Number VARCHAR(20)
);

INSERT INTO Users (Name, Age, Email, Number) VALUES
('Alice Smith', 25, 'alice@example.com', '123-456-7890'),
('Bob Johnson', 30, 'bob@example.com', '987-654-3210'),
('Charlie Davis', 22, 'charlie@example.com', '555-111-2222');

-- Venues table
CREATE TABLE Venues (
    VenueID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Location VARCHAR(100),
    Capacity INT,
    Type VARCHAR(50)
);

INSERT INTO Venues (Name, Location, Capacity, Type) VALUES
('Grand Hall', 'Newport Beach', 300, 'Indoor'),
('Oceanview Terrace', 'Laguna Beach', 150, 'Outdoor'),
('Rooftop Lounge', 'Irvine', 200, 'Rooftop');

-- Events table
CREATE TABLE Events (
    EventID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    VenueID INT,
    Name VARCHAR(100),
    Date DATE,
    Description TEXT,
    Theme VARCHAR(100),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (VenueID) REFERENCES Venues(VenueID)
);

INSERT INTO Events (UserID, VenueID, Name, Date, Description, Theme) VALUES
(1, 1, 'Charity Gala', '2025-05-10', 'Annual fundraising event.', 'Formal'),
(2, 2, 'Beach Bonfire Night', '2025-06-15', 'Relaxing night on the beach.', 'Casual'),
(3, 3, 'Startup Pitch Fest', '2025-07-20', 'Entrepreneurs pitch ideas.', 'Tech');

-- Invites table
CREATE TABLE Invites (
    InviteID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    EventID INT,
    DateSent DATE,
    Text TEXT,
    RecipientStatus VARCHAR(50),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);

INSERT INTO Invites (UserID, EventID, DateSent, Text, RecipientStatus) VALUES
(2, 1, '2025-04-01', 'Join us for the gala!', 'Attending'),
(3, 1, '2025-04-01', 'Hope you can make it!', 'Maybe'),
(1, 2, '2025-05-01', 'Bonfire party!', 'Declined');

-- Vendors table
CREATE TABLE Vendors (
    VendorID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    ServiceType VARCHAR(100),
    Owner VARCHAR(100),
    StaffCount INT
);

INSERT INTO Vendors (Name, ServiceType, Owner, StaffCount) VALUES
('Elite Catering', 'Catering', 'John Chef', 15),
('AV Pros', 'Audio/Visual', 'Mike Sound', 10),
('PhotoTime', 'Photography', 'Sarah Click', 5);

-- Vendor_Event junction table
CREATE TABLE Vendor_Event (
    VendorID INT,
    EventID INT,
    VendorCost FLOAT,
    PRIMARY KEY (VendorID, EventID),
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);

INSERT INTO Vendor_Event (VendorID, EventID, VendorCost) VALUES
(1, 1, 300.00),
(2, 1, 500.00),
(3, 3, 1000.00);