-- GreenEdu Database - Green Technology Awareness Platform
-- Import this in phpMyAdmin after creating the database

CREATE DATABASE IF NOT EXISTS greenedu;
USE greenedu;

-- Users (admin and researchers)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'researcher') DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Institutions (schools and colleges)
CREATE TABLE IF NOT EXISTS institutions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    type ENUM('School', 'College', 'University') NOT NULL,
    location VARCHAR(150),
    students_count INT DEFAULT 0,
    green_score INT DEFAULT 0,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    institution_id INT,
    grade VARCHAR(50),
    awareness_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL
);

-- Survey responses
CREATE TABLE IF NOT EXISTS surveys (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(100) NOT NULL,
    institution_name VARCHAR(150),
    solar_energy INT CHECK (solar_energy BETWEEN 1 AND 5),
    energy_saving INT CHECK (energy_saving BETWEEN 1 AND 5),
    water_conservation INT CHECK (water_conservation BETWEEN 1 AND 5),
    waste_management INT CHECK (waste_management BETWEEN 1 AND 5),
    awareness_level ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    comments TEXT,
    status ENUM('Pending', 'Completed') DEFAULT 'Pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Green technology categories
CREATE TABLE IF NOT EXISTS green_tech (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    adoption_percent INT DEFAULT 0,
    description TEXT,
    icon VARCHAR(50)
);

-- Recent activities
CREATE TABLE IF NOT EXISTS activities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50),
    title VARCHAR(200),
    description TEXT,
    icon VARCHAR(50),
    icon_color VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upcoming activities
CREATE TABLE IF NOT EXISTS upcoming (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200),
    description TEXT,
    event_date DATE,
    event_time VARCHAR(50),
    status ENUM('Scheduled', 'Upcoming', 'Pending') DEFAULT 'Upcoming'
);

-- Quotes
CREATE TABLE IF NOT EXISTS quotes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_text TEXT,
    author VARCHAR(100)
);

-- Energy resources data (colleges save their energy data here)
CREATE TABLE IF NOT EXISTS energy_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    college_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    contact_email VARCHAR(100),
    location VARCHAR(150),
    student_count INT DEFAULT 0,
    solar_kwh DECIMAL(10,2) DEFAULT 0,
    wind_kwh DECIMAL(10,2) DEFAULT 0,
    grid_kwh DECIMAL(10,2) DEFAULT 0,
    diesel_liters DECIMAL(10,2) DEFAULT 0,
    water_liters_per_day DECIMAL(10,2) DEFAULT 0,
    waste_recycled_kg DECIMAL(10,2) DEFAULT 0,
    green_score INT DEFAULT 0,
    notes TEXT,
    submitted_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin (password: admin123)
-- bcrypt hash for 'admin123': $2b$12$...
-- We'll register through the app and update role, or use this placeholder
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@greenedu.com', 'placeholder', 'admin');

-- Sample institutions
INSERT INTO institutions (name, type, location, students_count, green_score, status) VALUES
('Green Valley Public School', 'School', 'Mumbai, MH', 850, 78, 'Active'),
('Sunrise International School', 'School', 'Delhi, DL', 1200, 65, 'Active'),
('Central High School', 'School', 'Bangalore, KA', 950, 82, 'Active'),
('EcoTech College', 'College', 'Pune, MH', 2500, 88, 'Active'),
('Greenfield University', 'University', 'Chennai, TN', 5800, 75, 'Active'),
('Riverdale Academy', 'School', 'Hyderabad, TS', 720, 60, 'Active'),
('Mountain View Institute', 'College', 'Shimla, HP', 1800, 90, 'Active'),
('Coastal Engineering College', 'College', 'Goa, GA', 3200, 72, 'Active'),
('Northern Hills School', 'School', 'Dehradun, UK', 600, 68, 'Active'),
('Eastern Public School', 'School', 'Kolkata, WB', 1100, 55, 'Active'),
('Western Tech University', 'University', 'Ahmedabad, GJ', 6200, 80, 'Active'),
('Southern Arts College', 'College', 'Kochi, KL', 2100, 70, 'Active');

-- Sample green tech categories
INSERT INTO green_tech (name, adoption_percent, description, icon) VALUES
('Solar Energy', 78, 'Use of solar panels for clean and renewable energy.', 'solar'),
('Energy Saving', 75, 'Smart lighting and energy-efficient devices.', 'bulb'),
('Water Conservation', 62, 'Rainwater harvesting and water-saving fixtures.', 'water'),
('Waste Management', 56, 'Reduce, Reuse, Recycle practices.', 'recycle'),
('Sustainable Campus', 48, 'Green buildings and eco-friendly infrastructure.', 'leaf'),
('Wind Energy', 35, 'Use of wind turbines for renewable power.', 'wind'),
('E-Waste Management', 42, 'Proper disposal and recycling of electronic waste.', 'ewaste');

-- Sample recent activities
INSERT INTO activities (type, title, description, icon, icon_color, created_at) VALUES
('survey', 'New survey responses received', 'From 2 institutions', 'survey', 'green', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('report', 'Green technology report generated', 'For Central High School', 'report', 'blue', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('solar', 'Solar panel usage updated', 'At Sunrise College', 'solar', 'orange', DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('institution', 'New institution registered', 'Green Valley Public School', 'building', 'purple', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('student', 'New student registered', '50 students from EcoTech College', 'student', 'green', DATE_SUB(NOW(), INTERVAL 2 DAY));

-- Sample upcoming events
INSERT INTO upcoming (title, description, event_date, event_time, status) VALUES
('Survey Reminder', 'Reminder email for Green Technology', '2026-04-25', '10:00 AM - 11:00 AM', 'Scheduled'),
('Green Campus Workshop', 'Sustainable Practices in Education', '2026-04-28', '02:00 PM - 04:00 PM', 'Upcoming'),
('Report Submission', 'Final analysis and report', '2026-05-05', '09:00 AM - 10:00 AM', 'Pending');

-- Sample quotes
INSERT INTO quotes (quote_text, author) VALUES
('Greener campuses today, a sustainable future tomorrow.', 'A Greener Future Advocate'),
('Together we can make education more sustainable with green technology.', 'GreenEdu Team'),
('The Earth does not belong to us; we belong to the Earth.', 'Chief Seattle');

-- Sample energy data records
INSERT INTO energy_data (college_name, contact_person, contact_email, location, student_count,
                         solar_kwh, wind_kwh, grid_kwh, diesel_liters,
                         water_liters_per_day, waste_recycled_kg, green_score, notes, submitted_by)
VALUES
('Green Valley Public School', 'Dr. Anil Sharma', 'anil@greenvalley.edu', 'Mumbai, MH', 850,
 1200.50, 0, 3500.00, 50.00, 8000.00, 120.50, 78, 'Installed 50 solar panels on rooftop', 'admin'),
('EcoTech College', 'Prof. Priya Mehta', 'priya@ecotech.edu', 'Pune, MH', 2500,
 3500.75, 800.00, 7200.00, 30.00, 18000.00, 350.00, 88, 'Uses solar + wind hybrid system', 'admin'),
('Sunrise International School', 'Mr. Rakesh Kumar', 'rakesh@sunrise.edu', 'Delhi, DL', 1200,
 900.00, 0, 4200.00, 80.00, 9500.00, 95.00, 65, 'Partial solar coverage on main building', 'admin'),
('Central High School', 'Ms. Sneha Roy', 'sneha@centralhigh.edu', 'Bangalore, KA', 950,
 1500.00, 200.00, 2800.00, 20.00, 7000.00, 150.00, 82, 'Rainwater harvesting installed', 'admin');
