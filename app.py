"""
PawConnect - Pet Adoption Management System
Backend Web Application powered by Python Flask & MySQL
"""
import os
import functools
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, g, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'pawconnect_default_secret_key_2026')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

# ------------------------------------------------------------
# Authentication & Role Decorators
# ------------------------------------------------------------
def login_required(view):
    """Ensures user is logged into the session."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def role_required(*allowed_roles):
    """Restricts access based on user role (adopter, shelter, admin)."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if 'user_id' not in session:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for('login', next=request.url))
            if session.get('role') not in allowed_roles:
                flash("You do not have permission to view that page.", "error")
                return redirect(url_for('index'))
            return view(**kwargs)
        return wrapped_view
    return decorator

# ------------------------------------------------------------
# Context Processors & Helper Utilities
# ------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Provides common data to templates."""
    return {
        'current_user_id': session.get('user_id'),
        'current_user_name': session.get('user_name'),
        'current_user_role': session.get('role')
    }

def get_unique_cities():
    """Fetches list of distinct cities from shelters table."""
    try:
        rows = db.query_db("SELECT DISTINCT city FROM shelters WHERE city IS NOT NULL AND city != '' ORDER BY city ASC")
        return [r['city'] for r in rows] if rows else []
    except Exception as e:
        print(f"Error fetching cities: {e}")
        return ["Bangalore", "Mumbai", "Pune", "Delhi", "Hyderabad"]

# ------------------------------------------------------------
# Public Routes: Home, Available Pets, Pet Details
# ------------------------------------------------------------
@app.route('/')
def index():
    """Home page with hero section, statistics, and featured pets."""
    featured_pets = []
    stats = {'total_pets': 0, 'total_shelters': 0, 'adoptions_count': 0}
    cities = []

    try:
        # Fetch featured pets (Approved listings from verified shelters)
        featured_query = """
            SELECT p.*, s.shelter_name, s.city, s.state
            FROM pets p
            JOIN shelters s ON p.shelter_id = s.id
            WHERE p.is_approved = 1 AND s.is_verified = 1
            ORDER BY (p.status = 'Available') DESC, p.created_at DESC
            LIMIT 6
        """
        featured_pets = db.query_db(featured_query)

        # Platform metrics
        pets_count = db.query_db("SELECT COUNT(*) as c FROM pets WHERE is_approved = 1", one=True)
        shelters_count = db.query_db("SELECT COUNT(*) as c FROM shelters WHERE is_verified = 1", one=True)
        adoptions_count = db.query_db("SELECT COUNT(*) as c FROM adoption_requests WHERE status = 'Approved'", one=True)

        stats = {
            'total_pets': pets_count['c'] if pets_count else 0,
            'total_shelters': shelters_count['c'] if shelters_count else 0,
            'adoptions_count': adoptions_count['c'] if adoptions_count else 0
        }
        cities = get_unique_cities()

    except Exception as e:
        print(f"Index route error: {e}")
        flash("Welcome to PawConnect! Note: Local MySQL server connection status can be verified in .env.", "info")

    return render_template('index.html', featured_pets=featured_pets, stats=stats, cities=cities)


@app.route('/pets')
def pets():
    """Available Pets page with dynamic search, filter by city, species, and status."""
    keyword = request.args.get('q', '').strip()
    species = request.args.get('species', '').strip()
    city = request.args.get('city', '').strip()
    status = request.args.get('status', 'Available').strip()
    gender = request.args.get('gender', '').strip()

    pets_list = []
    cities = get_unique_cities()

    try:
        # Base query: approved listings from verified shelters
        query = """
            SELECT p.*, s.shelter_name, s.city, s.state
            FROM pets p
            JOIN shelters s ON p.shelter_id = s.id
            WHERE p.is_approved = 1 AND s.is_verified = 1
        """
        params = []

        if keyword:
            query += " AND (p.name LIKE %s OR p.breed LIKE %s OR p.description LIKE %s OR s.shelter_name LIKE %s)"
            kw_param = f"%{keyword}%"
            params.extend([kw_param, kw_param, kw_param, kw_param])

        if species:
            query += " AND p.species = %s"
            params.append(species)

        if city:
            query += " AND s.city = %s"
            params.append(city)

        if status:
            query += " AND p.status = %s"
            params.append(status)

        if gender:
            query += " AND p.gender = %s"
            params.append(gender)

        query += " ORDER BY (p.status = 'Available') DESC, p.created_at DESC"
        pets_list = db.query_db(query, tuple(params))

    except Exception as e:
        print(f"Pets search error: {e}")
        flash("Could not retrieve pet listings from the database. Please ensure MySQL is running.", "error")

    return render_template('pets.html', pets=pets_list, cities=cities)


@app.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    """Detailed profile of a selected pet including shelter details and application action."""
    try:
        query = """
            SELECT p.*, 
                   s.id AS shelter_table_id, s.shelter_name, s.city, s.state, 
                   s.address AS shelter_address, s.phone AS shelter_phone, 
                   s.email AS shelter_email, s.website AS shelter_website, 
                   s.is_verified
            FROM pets p
            JOIN shelters s ON p.shelter_id = s.id
            WHERE p.id = %s
        """
        pet = db.query_db(query, (pet_id,), one=True)
        if not pet:
            flash("Pet listing not found.", "error")
            return redirect(url_for('pets'))

        return render_template('pet_detail.html', pet=pet)
    except Exception as e:
        print(f"Pet detail error: {e}")
        flash("Failed to load pet details.", "error")
        return redirect(url_for('pets'))

# ------------------------------------------------------------
# Authentication: Login, Register, Logout
# ------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and Shelter authentication with role redirection."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        next_url = request.form.get('next', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template('login.html')

        try:
            user = db.query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)

            if user and check_password_hash(user['password_hash'], password):
                # Set session state
                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['email'] = user['email']
                session['role'] = user['role']

                flash(f"Welcome back, {user['full_name']}!", "success")

                if next_url and next_url.startswith('/'):
                    return redirect(next_url)

                # Route based on role
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user['role'] == 'shelter':
                    return redirect(url_for('shelter_dashboard'))
                else:
                    return redirect(url_for('adopter_dashboard'))
            else:
                flash("Invalid email or password. Please try again.", "error")

        except Exception as e:
            print(f"Login database error: {e}")
            flash("Database connection error. Please verify MySQL service status.", "error")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User and Shelter account registration."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        role = request.form.get('role', 'adopter').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('register.html')

        try:
            # Check if email is already taken
            existing = db.query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
            if existing:
                flash("An account with that email already exists. Please log in.", "warning")
                return redirect(url_for('login'))

            hashed_password = generate_password_hash(password)

            if role == 'shelter':
                shelter_name = request.form.get('shelter_name', '').strip() or full_name
                license_number = request.form.get('license_number', '').strip()
                state = request.form.get('state', '').strip() or 'State'
                website = request.form.get('website', '').strip()
                description = request.form.get('description', '').strip()

                # Execute transactional creation: insert user + insert shelter
                user_id, _ = db.modify_db(
                    "INSERT INTO users (full_name, email, password_hash, phone, address, role) VALUES (%s, %s, %s, %s, %s, %s)",
                    (full_name, email, hashed_password, phone, address, 'shelter')
                )

                db.modify_db(
                    """INSERT INTO shelters 
                       (user_id, shelter_name, license_number, city, state, address, phone, email, website, description, is_verified) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_id, shelter_name, license_number, city, state, address, phone, email, website, description, False)
                )

                flash("Shelter account registered successfully! Your account is pending admin verification.", "success")
            else:
                # Standard adopter
                user_id, _ = db.modify_db(
                    "INSERT INTO users (full_name, email, password_hash, phone, address, role) VALUES (%s, %s, %s, %s, %s, %s)",
                    (full_name, email, hashed_password, phone, address, 'adopter')
                )
                flash("Adopter account created successfully! Please log in to continue.", "success")

            return redirect(url_for('login'))

        except Exception as e:
            print(f"Registration error: {e}")
            flash(f"Failed to register account: {e}", "error")

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('index'))

# ------------------------------------------------------------
# Adopter Workflow: Submit & Track Applications
# ------------------------------------------------------------
@app.route('/apply/<int:pet_id>', methods=['GET', 'POST'])
@login_required
@role_required('adopter')
def apply(pet_id):
    """Submit an adoption application for a specific available pet."""
    try:
        query = """
            SELECT p.*, s.shelter_name, s.city, s.state
            FROM pets p
            JOIN shelters s ON p.shelter_id = s.id
            WHERE p.id = %s
        """
        pet = db.query_db(query, (pet_id,), one=True)
        if not pet:
            flash("Pet listing not found.", "error")
            return redirect(url_for('pets'))

        if pet['status'] != 'Available':
            flash(f"Sorry, {pet['name']} is currently {pet['status'].lower()} and not accepting new applications.", "warning")
            return redirect(url_for('pet_detail', pet_id=pet_id))

        user = db.query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)

        # Check if already applied
        existing_app = db.query_db(
            "SELECT id, status FROM adoption_requests WHERE pet_id = %s AND user_id = %s AND status = 'Pending'",
            (pet_id, session['user_id']),
            one=True
        )
        if existing_app:
            flash(f"You already have an active pending application for {pet['name']}.", "info")
            return redirect(url_for('adopter_dashboard'))

        if request.method == 'POST':
            housing_type = request.form.get('housing_type', 'Apartment').strip()
            has_yard = 1 if request.form.get('has_yard') else 0
            previous_experience = request.form.get('previous_experience', '').strip()
            reason_for_adoption = request.form.get('reason_for_adoption', '').strip()
            contact_phone = request.form.get('contact_phone', user['phone'] or '').strip()

            if not previous_experience or not reason_for_adoption or not contact_phone:
                flash("Please fill in all required questions in the application.", "error")
                return render_template('apply.html', pet=pet, user=user)

            # Insert application into MySQL
            db.modify_db(
                """INSERT INTO adoption_requests 
                   (pet_id, user_id, housing_type, has_yard, previous_experience, reason_for_adoption, contact_phone, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')""",
                (pet_id, session['user_id'], housing_type, has_yard, previous_experience, reason_for_adoption, contact_phone)
            )

            flash(f"Your adoption application for {pet['name']} has been submitted to {pet['shelter_name']}!", "success")
            return redirect(url_for('adopter_dashboard'))

        return render_template('apply.html', pet=pet, user=user)

    except Exception as e:
        print(f"Apply error: {e}")
        flash("Failed to process adoption application.", "error")
        return redirect(url_for('pets'))


@app.route('/adopter/dashboard')
@login_required
@role_required('adopter')
def adopter_dashboard():
    """Adopter portal showing all submitted applications and their statuses."""
    try:
        query = """
            SELECT ar.*, p.name AS pet_name, p.species, p.breed, p.image_url, 
                   s.shelter_name, s.city AS shelter_city, s.phone AS shelter_phone
            FROM adoption_requests ar
            JOIN pets p ON ar.pet_id = p.id
            JOIN shelters s ON p.shelter_id = s.id
            WHERE ar.user_id = %s
            ORDER BY ar.created_at DESC
        """
        applications = db.query_db(query, (session['user_id'],))
        return render_template('adopter_dashboard.html', applications=applications)
    except Exception as e:
        print(f"Adopter dashboard error: {e}")
        flash("Failed to load your applications.", "error")
        return render_template('adopter_dashboard.html', applications=[])

# ------------------------------------------------------------
# Shelter / Rescuer Dashboard & Pet Management
# ------------------------------------------------------------
@app.route('/shelter/dashboard')
@login_required
@role_required('shelter')
def shelter_dashboard():
    """Shelter management portal with listed pets and incoming applications."""
    try:
        shelter = db.query_db("SELECT * FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)
        if not shelter:
            flash("Shelter profile not found.", "error")
            return redirect(url_for('index'))

        # Fetch pets managed by this shelter
        pets = db.query_db(
            "SELECT * FROM pets WHERE shelter_id = %s ORDER BY created_at DESC",
            (shelter['id'],)
        )

        # Fetch applications for this shelter's pets
        app_query = """
            SELECT ar.*, 
                   p.name AS pet_name, p.breed AS pet_breed, p.image_url AS pet_image,
                   u.full_name AS applicant_name, u.email AS applicant_email
            FROM adoption_requests ar
            JOIN pets p ON ar.pet_id = p.id
            JOIN users u ON ar.user_id = u.id
            WHERE p.shelter_id = %s
            ORDER BY (ar.status = 'Pending') DESC, ar.created_at DESC
        """
        applications = db.query_db(app_query, (shelter['id'],))

        return render_template('shelter_dashboard.html', shelter=shelter, pets=pets, applications=applications)
    except Exception as e:
        print(f"Shelter dashboard error: {e}")
        flash("Error loading shelter portal.", "error")
        return redirect(url_for('index'))


@app.route('/shelter/pet/add', methods=['GET', 'POST'])
@login_required
@role_required('shelter')
def add_pet():
    """Register and publish a new pet."""
    shelter = db.query_db("SELECT * FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)
    if not shelter:
        flash("Shelter profile not found.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        species = request.form.get('species', 'Dog').strip()
        breed = request.form.get('breed', '').strip()
        age_years = int(request.form.get('age_years', 1))
        age_months = int(request.form.get('age_months', 0))
        gender = request.form.get('gender', 'Male').strip()
        size = request.form.get('size', 'Medium').strip()
        color = request.form.get('color', '').strip()
        image_url = request.form.get('image_url', '').strip()
        description = request.form.get('description', '').strip()
        medical_notes = request.form.get('medical_notes', '').strip()

        vaccinated = 1 if request.form.get('vaccinated') else 0
        spayed_neutered = 1 if request.form.get('spayed_neutered') else 0
        good_with_kids = 1 if request.form.get('good_with_kids') else 0
        good_with_pets = 1 if request.form.get('good_with_pets') else 0

        # Auto-approve listing if shelter is verified, else require admin moderation
        is_approved = 1 if shelter['is_verified'] else 0

        if not name or not breed or not image_url or not description:
            flash("Please provide all required fields including photo URL and description.", "error")
            return render_template('add_pet.html')

        try:
            db.modify_db(
                """INSERT INTO pets 
                   (shelter_id, name, species, breed, age_years, age_months, gender, size, color, 
                    description, medical_notes, vaccinated, spayed_neutered, good_with_kids, good_with_pets, 
                    image_url, status, is_approved) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Available', %s)""",
                (shelter['id'], name, species, breed, age_years, age_months, gender, size, color,
                 description, medical_notes, vaccinated, spayed_neutered, good_with_kids, good_with_pets,
                 image_url, is_approved)
            )

            msg = f"{name} has been listed successfully!"
            if not is_approved:
                msg += " Note: Listing will become publicly visible once verified by platform admin."
            flash(msg, "success")
            return redirect(url_for('shelter_dashboard'))

        except Exception as e:
            print(f"Add pet error: {e}")
            flash(f"Failed to add pet: {e}", "error")

    return render_template('add_pet.html')


@app.route('/shelter/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('shelter')
def edit_pet(pet_id):
    """Edit existing pet profile."""
    shelter = db.query_db("SELECT * FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)
    pet = db.query_db("SELECT * FROM pets WHERE id = %s AND shelter_id = %s", (pet_id, shelter['id']), one=True)
    if not pet:
        flash("Pet not found or unauthorized.", "error")
        return redirect(url_for('shelter_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        species = request.form.get('species', 'Dog').strip()
        breed = request.form.get('breed', '').strip()
        age_years = int(request.form.get('age_years', 1))
        age_months = int(request.form.get('age_months', 0))
        gender = request.form.get('gender', 'Male').strip()
        size = request.form.get('size', 'Medium').strip()
        color = request.form.get('color', '').strip()
        status = request.form.get('status', 'Available').strip()
        image_url = request.form.get('image_url', '').strip()
        description = request.form.get('description', '').strip()
        medical_notes = request.form.get('medical_notes', '').strip()

        vaccinated = 1 if request.form.get('vaccinated') else 0
        spayed_neutered = 1 if request.form.get('spayed_neutered') else 0
        good_with_kids = 1 if request.form.get('good_with_kids') else 0
        good_with_pets = 1 if request.form.get('good_with_pets') else 0

        try:
            db.modify_db(
                """UPDATE pets 
                   SET name = %s, species = %s, breed = %s, age_years = %s, age_months = %s, 
                       gender = %s, size = %s, color = %s, status = %s, image_url = %s, 
                       description = %s, medical_notes = %s, vaccinated = %s, 
                       spayed_neutered = %s, good_with_kids = %s, good_with_pets = %s 
                   WHERE id = %s AND shelter_id = %s""",
                (name, species, breed, age_years, age_months, gender, size, color, status,
                 image_url, description, medical_notes, vaccinated, spayed_neutered,
                 good_with_kids, good_with_pets, pet_id, shelter['id'])
            )
            flash(f"Details for {name} updated successfully!", "success")
            return redirect(url_for('shelter_dashboard'))

        except Exception as e:
            print(f"Edit pet error: {e}")
            flash(f"Failed to update pet details: {e}", "error")

    return render_template('edit_pet.html', pet=pet)


@app.route('/shelter/pet/<int:pet_id>/status', methods=['POST'])
@login_required
@role_required('shelter')
def update_pet_status(pet_id):
    """Quick toggle of pet status from dashboard."""
    shelter = db.query_db("SELECT id FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)
    status = request.form.get('status', 'Available').strip()
    try:
        db.modify_db(
            "UPDATE pets SET status = %s WHERE id = %s AND shelter_id = %s",
            (status, pet_id, shelter['id'])
        )
        flash("Pet availability status updated.", "success")
    except Exception as e:
        print(f"Status update error: {e}")
        flash("Could not update status.", "error")
    return redirect(url_for('shelter_dashboard'))


@app.route('/shelter/pet/<int:pet_id>/delete', methods=['POST'])
@login_required
@role_required('shelter')
def delete_pet(pet_id):
    """Delete a pet listing."""
    shelter = db.query_db("SELECT id FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)
    try:
        db.modify_db("DELETE FROM pets WHERE id = %s AND shelter_id = %s", (pet_id, shelter['id']))
        flash("Pet listing removed.", "info")
    except Exception as e:
        print(f"Delete pet error: {e}")
        flash("Failed to delete pet listing.", "error")
    return redirect(url_for('shelter_dashboard'))


@app.route('/shelter/application/<int:app_id>/status', methods=['POST'])
@login_required
@role_required('shelter')
def update_application_status(app_id):
    """
    Approve or Reject an adoption application.
    Enforces DBMS Business Logic:
    - If status is 'Approved':
      1. Marks application as 'Approved'
      2. Automatically marks the pet as 'Adopted'
      3. Automatically rejects any competing pending applications for the same pet with a notification
      This prevents duplicate successful adoptions of the same pet!
    """
    new_status = request.form.get('status', '').strip()
    remarks = request.form.get('remarks', '').strip()

    if new_status not in ('Approved', 'Rejected'):
        flash("Invalid status choice.", "error")
        return redirect(url_for('shelter_dashboard'))

    try:
        shelter = db.query_db("SELECT id FROM shelters WHERE user_id = %s", (session['user_id'],), one=True)

        # Verify application belongs to this shelter
        query = """
            SELECT ar.*, p.name AS pet_name, p.status AS pet_current_status
            FROM adoption_requests ar
            JOIN pets p ON ar.pet_id = p.id
            WHERE ar.id = %s AND p.shelter_id = %s
        """
        app_record = db.query_db(query, (app_id, shelter['id']), one=True)

        if not app_record:
            flash("Application record not found or unauthorized.", "error")
            return redirect(url_for('shelter_dashboard'))

        pet_id = app_record['pet_id']

        if new_status == 'Approved':
            # Check if pet has ALREADY been adopted
            if app_record['pet_current_status'] == 'Adopted':
                flash("Cannot approve application: This pet has already been adopted!", "error")
                return redirect(url_for('shelter_dashboard'))

            # Transaction: Approve this request, set pet to Adopted, decline competing requests
            db.modify_db(
                "UPDATE adoption_requests SET status = 'Approved', shelter_remarks = %s WHERE id = %s",
                (remarks or "Adoption application approved! Congratulations.", app_id)
            )

            db.modify_db(
                "UPDATE pets SET status = 'Adopted' WHERE id = %s",
                (pet_id,)
            )

            # Auto-reject competing pending requests for the same pet
            db.modify_db(
                """UPDATE adoption_requests 
                   SET status = 'Rejected', 
                       shelter_remarks = 'Pet adopted by another approved applicant.' 
                   WHERE pet_id = %s AND id != %s AND status = 'Pending'""",
                (pet_id, app_id)
            )

            flash(f"Application approved! {app_record['pet_name']} has been marked as Adopted and duplicate requests resolved.", "success")

        else:
            # Rejection
            db.modify_db(
                "UPDATE adoption_requests SET status = 'Rejected', shelter_remarks = %s WHERE id = %s",
                (remarks or "Application declined by shelter coordinator.", app_id)
            )
            flash("Adoption application was marked as declined.", "info")

    except Exception as e:
        print(f"Update application error: {e}")
        flash(f"Database error: {e}", "error")

    return redirect(url_for('shelter_dashboard'))

# ------------------------------------------------------------
# Admin Dashboard & Moderation
# ------------------------------------------------------------
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin console for reviewing shelters, verifying pet listings, and user management."""
    try:
        admin_info = db.query_db("SELECT * FROM admins WHERE user_id = %s", (session['user_id'],), one=True)
        if not admin_info:
            admin_info = {'admin_code': 'ADM-SUPER', 'department': 'System Administration'}

        users = db.query_db("SELECT id, full_name, email, phone, role, created_at FROM users ORDER BY created_at DESC")

        shelters_query = """
            SELECT s.*, u.full_name AS rep_name, u.email AS rep_email
            FROM shelters s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.is_verified ASC, s.created_at DESC
        """
        shelters = db.query_db(shelters_query)

        pets_query = """
            SELECT p.*, s.shelter_name, s.city
            FROM pets p
            JOIN shelters s ON p.shelter_id = s.id
            ORDER BY p.is_approved ASC, p.created_at DESC
        """
        all_pets = db.query_db(pets_query)

        all_applications = db.query_db("SELECT * FROM adoption_requests ORDER BY created_at DESC")

        return render_template(
            'admin_dashboard.html',
            admin_info=admin_info,
            users=users,
            shelters=shelters,
            all_pets=all_pets,
            all_applications=all_applications
        )
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        flash("Failed to load admin moderation console.", "error")
        return redirect(url_for('index'))


@app.route('/admin/shelter/<int:shelter_id>/verify', methods=['POST'])
@login_required
@role_required('admin')
def verify_shelter(shelter_id):
    """Admin endpoint to verify or revoke shelter accounts."""
    action = request.form.get('action', 'approve')
    new_verified_val = 1 if action == 'approve' else 0

    try:
        db.modify_db("UPDATE shelters SET is_verified = %s WHERE id = %s", (new_verified_val, shelter_id))
        status_word = "verified and approved" if new_verified_val else "revoked"
        flash(f"Shelter status has been {status_word}.", "success")
    except Exception as e:
        print(f"Verify shelter error: {e}")
        flash("Failed to update shelter status.", "error")

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/pet/<int:pet_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_pet_listing(pet_id):
    """Admin endpoint to approve or unpublish pet listings."""
    action = request.form.get('action', 'approve')
    new_val = 1 if action == 'approve' else 0

    try:
        db.modify_db("UPDATE pets SET is_approved = %s WHERE id = %s", (new_val, pet_id))
        status_word = "approved for public display" if new_val else "delisted"
        flash(f"Pet listing has been {status_word}.", "success")
    except Exception as e:
        print(f"Approve pet error: {e}")
        flash("Failed to update pet approval.", "error")

    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------
# Application Entry Point
# ------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("=" * 60)
    print(" PawConnect - Pet Adoption Management System")
    print(f" Running locally on: http://127.0.0.1:{port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
