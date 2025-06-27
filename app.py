import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import pyodbc
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# ODBC connection string for Oracle Database
ODBC_CONNECTION_STRING = "DSN=oracledb;Uid=rajasri;Pwd=2004;"

# Route for the authentication page
@app.route('/', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form.get('action')  # Check which button was clicked

        if action == 'Login':
            try:
                conn = pyodbc.connect(ODBC_CONNECTION_STRING)
                cursor = conn.cursor()

                # Query to validate the user
                query = "SELECT password FROM users WHERE username = ?"
                cursor.execute(query, (username,))
                result1 = cursor.fetchone()
                
                query = "SELECT alternate_password FROM users WHERE username = ?"
                cursor.execute(query, (username,))
                result2 = cursor.fetchone()

                if result1 and result1[0] == password:
                    session['username'] = username  # Set session for logged-in user
                    return redirect(url_for('index'))
                elif result2 and result2[0] == password:
                    session['username'] = username  # Set session for logged-in user
                    return redirect(url_for('index'))
                else:
                    flash("Authentication Failed! Invalid username or password.")
            except Exception as e:
                logging.error(f"Login error: {e}")
                flash("An error occurred during login. Please try again.")
            finally:
                conn.close()

        elif action == 'Create User':
            return redirect(url_for('create_user', action='create'))

        elif action == 'Change Password':
            return redirect(url_for('create_user', action='change'))

    return render_template('auth_page.html')


# Route for the user creation/change password page
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    action = request.args.get('action', 'create')  # Default action is 'create'

    if request.method == 'POST':
        username = request.form['username']
        
       
        if action == 'create':
            password = request.form['password']
    #    confirm_password = request.form['confirm_password']
            alternate_password = request.form.get('alternate_password', None)  # Handle missing key
            try:
                conn = pyodbc.connect(ODBC_CONNECTION_STRING)
                cursor = conn.cursor()

                # Check if the username already exists
                query_check = "SELECT username FROM users WHERE username = ?"
                cursor.execute(query_check, (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Username already exists!")
                    return redirect(url_for('create_user', action='create'))

                # Insert new user into the database
                query_insert = "INSERT INTO users (username, password, alternate_password) VALUES (?, ?, ?)"
                cursor.execute(query_insert, (username, password, alternate_password))
                conn.commit()

                flash("User created successfully! You can now log in.")
                return redirect(url_for('auth_page'))
            except Exception as e:
                logging.error(f"User creation error: {e}")
                flash("An error occurred during user creation. Please try again.")
            finally:
                conn.close()

        elif action == 'change':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_new_password = request.form['confirm_new_password']

            if new_password != confirm_new_password:
                flash("New passwords do not match!")
                return redirect(url_for('create_user', action='change'))

            try:
                conn = pyodbc.connect(ODBC_CONNECTION_STRING)
                cursor = conn.cursor()

                # Fetch current password from the database
                query = "SELECT password FROM users WHERE username = ?"
                cursor.execute(query, (username,))
                result1 = cursor.fetchone()
                query = "SELECT alternate_password FROM users WHERE username = ?"
                cursor.execute(query, (username,))
                result2 = cursor.fetchone()
                

                if result1 and result1[0] == current_password:
                    # Update the password
                    update_query = "UPDATE users SET password = ? WHERE username = ?"
                    cursor.execute(update_query, (new_password, username))
                    conn.commit()

                    flash("Password changed successfully!")
                    return redirect(url_for('auth_page'))
                elif result2 and result2[0] == current_password:
                    # Update the password
                    update_query = "UPDATE users SET alternate_password = ? WHERE username = ?"
                    cursor.execute(update_query, (new_password, username))
                    conn.commit()

                    flash("Password changed successfully!")
                    return redirect(url_for('auth_page'))
                else:
                    flash("Current password is incorrect.")
            except Exception as e:
                logging.error(f"Password change error: {e}")
                flash("An error occurred during password change. Please try again.")
            finally:
                conn.close()

    return render_template('create_user.html', action=action)






def get_db_connection():
    """Establish database connection."""
    try:
        connection = pyodbc.connect(ODBC_CONNECTION_STRING)
        return connection
    except pyodbc.DatabaseError as e:
        print(f"Error connecting to the database: {e}")
        return None



@app.route("/index", methods=["GET", "POST"])
def index():
    patient_data = None
    disable_buttons = False

    if request.method == "POST":
        connection = get_db_connection()
        cursor = None

        try:
            if connection:
                cursor = connection.cursor()

                if "fetch" in request.form:
                    patient_id = request.form.get("patient_id")

                    # Fetch patient details from `patients`
                    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
                    patient_data = cursor.fetchone()

                    if patient_data:
                        # Check if the patient also exists in `main_table`
                        cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (patient_id,))
                        in_main_table = cursor.fetchone()

                        if in_main_table:
                            disable_buttons = True  # Disable buttons if record exists in both tables
                        
                        flash(f"Patient ID {patient_id} fetched successfully.", "info")
                    else:
                        flash("Patient not found.", "error")
                        patient_data = None



                elif "save" in request.form:
                    return save_patient()

                elif "update" in request.form:
                    return update_patient()

                elif "delete" in request.form:
                    return delete_patient()

                elif "commit" in request.form:
                    return commit_patient()

                elif "clear" in request.form:
                    return redirect(url_for("index"))

            else:
                flash("Database connection failed.", "error")

        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template(
    "patient_form.html",
    patient_data=patient_data,
    disable_buttons=disable_buttons,
)
    
@app.route("/get_patient/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    """Fetch a patient's details by ID."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
            result = cursor.fetchone()
            if result:
                patient_data = {
                    "patient_id": result[0],
                    "name": result[1],
                    "dob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                    "gender": result[3],
                    "age": result[4],
                    "address": result[5],
                    "phone": result[6],
                    "patient_type": result[7],
                }
                return {"success": True, "patient": patient_data}
            else:
                return {"success": False, "message": "Patient not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection:
            connection.close()


@app.route('/get_next_patient_id', methods=['GET'])
def get_next_patient_id():
    """Fetch the next available patient_id in the format P001, P002, etc."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Query to fetch the maximum numeric part of patient_id (excluding 'P')
            cursor.execute("""
                SELECT MAX(CAST(SUBSTR(patient_id, 2) AS INTEGER))
                FROM patients
            """)
            result = cursor.fetchone()

            # Ensure the result is processed correctly
            max_id = result[0] if result[0] else 0  # Default to 0 if no records
            next_id = f"P{int(max_id) + 1:03}"  # Increment and format as PXXX

            cursor.close()
            return jsonify({"success": True, "next_patient_id": next_id})
        else:
            return jsonify({"success": False, "message": "Database connection failed."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()



@app.route("/navigate_patient/<action>/<patient_id>", methods=["GET"])
def navigate_patient(action, patient_id):
    """Handle previous/next navigation."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            if action == "previous":
                # Query to fetch the previous patient record
                cursor.execute(
                    """
                    SELECT * FROM patients
                    WHERE patient_id = (
                        SELECT MAX(patient_id)
                        FROM patients
                        WHERE patient_id < ?
                    )
                    """,
                    (patient_id,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the patient exists in main_table
                    cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "patient": {
                            "patient_id": result[0],
                            "name": result[1],
                            "dob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "gender": result[3],
                            "age": result[4],
                            "address": result[5],
                            "phone": result[6],
                            "patient_type": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in main_table
                    }
                else:
                    return {"success": False, "message": "This is the first record."}

            elif action == "next":
                # Query to fetch the next patient record
                cursor.execute(
                    """
                    SELECT * FROM patients
                    WHERE patient_id = (
                        SELECT MIN(patient_id)
                        FROM patients
                        WHERE patient_id > ?
                    )
                    """,
                    (patient_id,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the patient exists in main_table
                    cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "patient": {
                            "patient_id": result[0],
                            "name": result[1],
                            "dob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "gender": result[3],
                            "age": result[4],
                            "address": result[5],
                            "phone": result[6],
                            "patient_type": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in main_table
                    }
                else:
                    return {"success": False, "message": "This is the last record."}

    except pyodbc.Error as e:
        # Handle specific database error
        print(f"Database error occurred: {str(e)}")
        return {"success": False, "error": str(e)}

    except Exception as e:
        # General exception handling
        print(f"Error occurred: {str(e)}")
        return {"success": False, "error": str(e)}

    finally:
        # Ensure the connection is always closed
        if connection:
            connection.close()

    """Handle previous/next navigation."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            if action == "previous":
                cursor.execute(
                    """
                    SELECT * FROM patients
                    WHERE patient_id = (
                        SELECT MAX(patient_id)
                        FROM patients
                        WHERE patient_id < ?
                    )
                    """,
                    (patient_id,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the patient exists in main_table
                    cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "patient": {
                            "patient_id": result[0],
                            "name": result[1],
                            "dob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "gender": result[3],
                            "age": result[4],
                            "address": result[5],
                            "phone": result[6],
                            "patient_type": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in main_table
                    }
                else:
                    return {"success": False, "message": "This is the first record."}

            elif action == "next":
                cursor.execute(
                    """
                    SELECT * FROM patients
                    WHERE patient_id = (
                        SELECT MIN(patient_id)
                        FROM patients
                        WHERE patient_id > ?
                    )
                    """,
                    (patient_id,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the patient exists in main_table
                    cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "patient": {
                            "patient_id": result[0],
                            "name": result[1],
                            "dob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "gender": result[3],
                            "age": result[4],
                            "address": result[5],
                            "phone": result[6],
                            "patient_type": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in main_table
                    }
                else:
                    return {"success": False, "message": "This is the last record."}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection:
            connection.close()


@app.route("/fetch_details/<patient_id>", methods=["GET"])
def fetch_details(patient_id):
    """Fetch patient details and determine button status."""
    response = {"success": False, "data": None, "disable_buttons": False}

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Fetch details from `patients` table
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
            patient_data = cursor.fetchone()

            if patient_data:
                # Check if the record exists in `main_table`
                cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (patient_id,))
                in_main_table = cursor.fetchone()

                # Disable buttons if the record is in both tables
                response["disable_buttons"] = bool(in_main_table)
                response["data"] = {
                    "patient_id": patient_data[0],
                    "name": patient_data[1],
                    "dob": patient_data[2].strftime("%d-%b-%Y") if patient_data[2] else "",
                    "gender": patient_data[3],
                    "age": patient_data[4],
                    "address": patient_data[5],
                    "phone": patient_data[6],
                    "patient_type": patient_data[7],
                }
                response["success"] = True
    except Exception as e:
        response["error"] = str(e)
    finally:
        if connection:
            connection.close()

    return response


def save_patient():
    """Save a new patient record."""
    patient_id = request.form.get("patient_id")
    name = request.form.get("name")
    dob = request.form.get("dob")
   

    
    gender = request.form.get("gender")
    age = request.form.get("age")
    address = request.form.get("address")
    phone = request.form.get("phone")
    patient_type = request.form.get("patient_type")

    # Validate input
    if not all([patient_id, name, dob, gender, age, address, phone, patient_type]):
        flash("All fields are required!", "error")
        return redirect(url_for("index"))

    try:
        dob = datetime.datetime.strptime(dob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO patients (patient_id, name, dob, gender, age, address, phone, patient_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                patient_id, name, dob, gender, age, address, phone, patient_type,
            )
            connection.commit()
            flash("Patient record saved successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def update_patient():
    """Update an existing patient record."""
    patient_id = request.form.get("patient_id")
    name = request.form.get("name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    age = request.form.get("age")
    address = request.form.get("address")
    phone = request.form.get("phone")
    patient_type = request.form.get("patient_type")

    try:
        dob = datetime.datetime.strptime(dob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE patients
                SET name = ?, dob = ?, gender = ?, age = ?, address = ?, phone = ?, patient_type = ?
                WHERE patient_id = ?
                """,
                name, dob, gender, age, address, phone, patient_type, patient_id,
            )
            connection.commit()
            flash("Patient record updated successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def delete_patient():
    """Delete a patient record."""
    patient_id = request.form.get("patient_id")
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
            connection.commit()
            flash("Patient record deleted successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def commit_patient():
    """Commit patient record to main_table with conditional logic."""
    patient_id = request.form.get("patient_id")
    name = request.form.get("name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    age = request.form.get("age")
    address = request.form.get("address")
    phone = request.form.get("phone")
    patient_type = request.form.get("patient_type")

    try:
        # Validate date format
        dob = datetime.datetime.strptime(dob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))

        cursor = connection.cursor()

        # Check if patient_id exists in the patients table
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        patient = cursor.fetchone()

        if patient:
            # Copy the patient to main_table if found in patients
            cursor.execute(
                """
                INSERT INTO main_table (patient_id, name, dob, gender, age, address, phone, patient_type)
                SELECT patient_id, name, dob, gender, age, address, phone, patient_type
                FROM patients WHERE patient_id = ?
                """,
                (patient_id,)
            )
            flash("Patient record committed to main_table.", "success")
        else:
            # Check if the patient exists in main_table
            cursor.execute("SELECT * FROM main_table WHERE patient_id = ?", (patient_id,))
            in_main_table = cursor.fetchone()

            if not in_main_table:
                # Save in both tables if not found in either
                cursor.execute(
                    """
                    INSERT INTO patients (patient_id, name, dob, gender, age, address, phone, patient_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (patient_id, name, dob, gender, age, address, phone, patient_type)
                )
                cursor.execute(
                    """
                    INSERT INTO main_table (patient_id, name, dob, gender, age, address, phone, patient_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (patient_id, name, dob, gender, age, address, phone, patient_type)
                )
                flash("Patient record saved in both patients and main_table.", "success")
            else:
                flash("Patient already exists in main_table.", "info")

        connection.commit()
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    except Exception as e:
        flash(f"Unexpected error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))



@app.route('/view_buffer', methods=['GET'])
def view_buffer():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM patients")
            buffer_records = cursor.fetchall()

        records_list = [
            {
                'patient_id': row[0],
                'name': row[1],
                'dob': row[2],
                'gender': row[3],
                'age': row[4],
                'address': row[5],
                'phone': row[6],
		'patient_type': row[7],
            }

            for row in buffer_records
        ]
        return render_template('buffer_table.html', records=records_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
