import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import pyodbc
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# ODBC connection string for Oracle Database
ODBC_CONNECTION_STRING = "DSN=oracledb;Uid=rajasri;Pwd=Rajasri;"

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

ODBC_CONNECTION_STRING = "DSN=oracledb;Uid=rajasri;Pwd=Rajasri;"

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
    user_data = None
    disable_buttons = False

    if request.method == "POST":
        connection = get_db_connection()
        cursor = None

        try:
            if connection:
                cursor = connection.cursor()

                if "fetch" in request.form:
                    did = request.form.get("did")

                    # Fetch user details from `dbtab`
                    cursor.execute("SELECT * FROM dbtab WHERE did = ?", (did,))
                    user_data = cursor.fetchone()

                    if user_data:
                        # Check if the user also exists in `maindb`
                        cursor.execute("SELECT * FROM maindb WHERE did = ?", (did,))
                        in_main_table = cursor.fetchone()

                        if in_main_table:
                            disable_buttons = True  # Disable buttons if record exists in both tables
                        
                        flash(f"user ID {did} fetched successfully.", "info")
                    else:
                        flash("user not found.", "error")
                        user_data = None



                elif "save" in request.form:
                    return save_user()

                elif "update" in request.form:
                    return update_user()

                elif "delete" in request.form:
                    return delete_user()

                elif "commit" in request.form:
                    return commit_user()

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
    "user_form.html",
    user_data=user_data,
    disable_buttons=disable_buttons,
)
    
@app.route("/get_user/<did>", methods=["GET"])
def get_user(did):
    """Fetch a user's details by ID."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM dbtab WHERE did = ?", (did,))
            result = cursor.fetchone()
            if result:
                user_data = {
                    "did": result[0],
                    "dname": result[1],
                    "ddob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                    "dgender": result[3],
                    "dno": result[4],
                    "dbname": result[5],
                    "dphone": result[6],
                    "dtype": result[7],
                }
                return {"success": True, "user": user_data}
            else:
                return {"success": False, "message": "Accessory not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection:
            connection.close()


@app.route('/get_next_did', methods=['GET'])
def get_next_did():
    """Fetch the next available b_id in the format B001, B002, etc."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Query to fetch the maximum numeric part of a_id (excluding 'P')
            cursor.execute("""
                SELECT MAX(CAST(SUBSTR(did, 2) AS INTEGER))
                FROM dbtab
            """)
            result = cursor.fetchone()

            # Ensure the result is processed correctly
            max_id = result[0] if result[0] else 0  # Default to 0 if no records
            next_did = f"B{int(max_id) + 1:03}"  # Increment and format as PXXX

            cursor.close()
            return jsonify({"success": True, "next_did": next_did})
        else:
            return jsonify({"success": False, "message": "Database connection failed."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()



@app.route("/navigate_user/<action>/<did>", methods=["GET"])
def navigate_user(action, did):
    """Handle previous/next navigation."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            if action == "previous":
                # Query to fetch the previous user record
                cursor.execute(
                    """
                    SELECT * FROM dbtab
                    WHERE did = (
                        SELECT MAX(did)
                        FROM dbtab
                        WHERE did < ?
                    )
                    """,
                    (did,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the user exists in maindb
                    cursor.execute("SELECT * FROM maindb WHERE did = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "user": {
                            "did": result[0],
                            "dname": result[1],
                            "ddob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "dgender": result[3],
                            "dno": result[4],
                            "dbname": result[5],
                            "dphone": result[6],
                            "dtype": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in maindb
                    }
                else:
                    return {"success": False, "message": "This is the first record."}

            elif action == "next":
                # Query to fetch the next user record
                cursor.execute(
                    """
                    SELECT * FROM dbtab
                    WHERE did = (
                        SELECT MIN(did)
                        FROM dbtab
                        WHERE did > ?
                    )
                    """,
                    (did,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the user exists in maindb
                    cursor.execute("SELECT * FROM maindb WHERE did = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "user": {
                            "did": result[0],
                            "dname": result[1],
                            "ddob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "dgender": result[3],
                            "dno": result[4],
                            "dbname": result[5],
                            "dphone": result[6],
                            "dtype": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in maindb
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
                    SELECT * FROM dbtab
                    WHERE did = (
                        SELECT MAX(did)
                        FROM dbtab
                        WHERE did < ?
                    )
                    """,
                    (did,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the user exists in maindb
                    cursor.execute("SELECT * FROM maindb WHERE did = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "user": {
                            "did": result[0],
                            "dname": result[1],
                            "ddob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "dtype": result[3],
                            "dno": result[4],
                            "dbname": result[5],
                            "dphone": result[6],
                            "dgender": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in maindb
                    }
                else:
                    return {"success": False, "message": "This is the first record."}

            elif action == "next":
                cursor.execute(
                    """
                    SELECT * FROM dbtab
                    WHERE did = (
                        SELECT MIN(did)
                        FROM dbtab
                        WHERE did > ?
                    )
                    """,
                    (did,),
                )
                result = cursor.fetchone()
                if result:
                    # Check if the user exists in maindb
                    cursor.execute("SELECT * FROM maindb WHERE did = ?", (result[0],))
                    in_main_table = cursor.fetchone()

                    return {
                        "success": True,
                        "user": {
                            "did": result[0],
                            "dname": result[1],
                            "ddob": result[2].strftime("%d-%b-%Y") if result[2] else None,
                            "dgender": result[3],
                            "dno": result[4],
                            "dbname": result[5],
                            "dphone": result[6],
                            "dtype": result[7],
                        },
                        "disable_buttons": bool(in_main_table),  # Disable buttons if in maindb
                    }
                else:
                    return {"success": False, "message": "This is the last record."}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection:
            connection.close()


@app.route("/fetch_details/<did>", methods=["GET"])
def fetch_details(did):
    """Fetch user details and determine button status."""
    response = {"success": False, "data": None, "disable_buttons": False}

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Fetch details from `dbtab` table
            cursor.execute("SELECT * FROM dbtab WHERE did = ?", (did,))
            user_data = cursor.fetchone()

            if user_data:
                # Check if the record exists in `maindb`
                cursor.execute("SELECT * FROM maindb WHERE did = ?", (did,))
                in_main_table = cursor.fetchone()

                # Disable buttons if the record is in both tables
                response["disable_buttons"] = bool(in_main_table)
                response["data"] = {
                    "did": user_data[0],
                    "dname": user_data[1],
                    "ddob": user_data[2].strftime("%d-%b-%Y") if user_data[2] else "",
                    "dgender": user_data[3],
                    "dno": user_data[4],
                    "dbname": user_data[5],
                    "dphone": user_data[6],
                    "dtype": user_data[7],
                }
                response["success"] = True
    except Exception as e:
        response["error"] = str(e)
    finally:
        if connection:
            connection.close()

    return response


def save_user():
    """Save a new user record."""
    did = request.form.get("did")
    dname = request.form.get("dname")
    ddob = request.form.get("ddob")
    
    dgender = request.form.get("dgender")
    dno = request.form.get("dno")
    dbname = request.form.get("dbname")
    dphone = request.form.get("dphone")
    dtype = request.form.get("dtype")

    # Validate input
    if not all([did, dname, ddob, dgender, dno, dbname, dphone, dtype]):
        flash("All fields are required!", "error")
        return redirect(url_for("index"))

    try:
        ddob = datetime.datetime.strptime(ddob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO dbtab (did, dname, ddob, dgender, dno, dbname, dphone, dtype)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                did, dname,ddob, dgender, dno, dbname, dphone, dtype,
            )
            connection.commit()
            flash("Record saved successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def update_user():
    """Update an existing user record."""
    did = request.form.get("did")
    dname = request.form.get("dname")
    ddob = request.form.get("ddob")
    dgender = request.form.get("dgender")
    dno = request.form.get("dno")
    dbname = request.form.get("dbname")
    dphone = request.form.get("dphone")
    dtype = request.form.get("dtype")

    try:
        ddob = datetime.datetime.strptime(ddob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE dbtab
                SET dname = ?, ddob = ?, dgender = ?, dno = ?, dbname = ?, dphone = ?, dtype = ?
                WHERE did = ?
                """,
                dname, ddob, dgender, dno, dbname, dphone, dtype, did,
            )
            connection.commit()
            flash("Record updated successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def delete_user():
    """Delete a user record."""
    did = request.form.get("did")
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM dbtab WHERE did = ?", (did,))
            connection.commit()
            flash("Record deleted successfully.", "success")
        else:
            flash("Database connection failed.", "error")
    except pyodbc.DatabaseError as e:
        flash(f"Database error: {e}", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("index"))


def commit_user():
    """Commit user record to maindb with conditional logic."""
    did = request.form.get("did")
    dname = request.form.get("dname")
    ddob = request.form.get("ddob")
    dgender = request.form.get("dgender")
    dno = request.form.get("dno")
    dbname = request.form.get("dbname")
    dphone = request.form.get("dphone")
    dtype = request.form.get("dtype")

    try:
        # Validate date format
        ddob = datetime.datetime.strptime(ddob, "%d-%b-%Y").strftime("%d-%b-%Y")
    except ValueError:
        flash("Invalid date format. Use dd-Mon-yyyy (e.g., 02-Dec-2024).", "error")
        return redirect(url_for("index"))

    try:
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))

        cursor = connection.cursor()

        # Check if a_id exists in the dbtab table
        cursor.execute("SELECT * FROM dbtab WHERE did = ?", (did,))
        user = cursor.fetchone()

        if user:
            # Copy the user to maindb if found in dbtab
            cursor.execute(
                """
                INSERT INTO maindb (did, dname, ddob, dgender, dno, dbname, dphone, dtype)
                SELECT did, dname, ddob, dgender, dno, dbname, dphone, dtype
                FROM dbtab WHERE did = ?
                """,
                (did,)
            )
            flash("Record committed to maindb.", "success")
        else:
            # Check if the user exists in maindb
            cursor.execute("SELECT * FROM maindb WHERE did = ?", (did,))
            in_main_table = cursor.fetchone()

            if not in_main_table:
                # Save in both tables if not found in either
               
                flash("Record not found at buffer.Save the record at buffer", "success")
            else:
                flash("Record already exists in maindb.", "info")

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
            cursor.execute("SELECT * FROM dbtab")
            buffer_records = cursor.fetchall()

        records_list = [
            {
                'did': row[0],
                'dname': row[1],
                'ddob': row[2],
                'dgender': row[3],
                'dno': row[4],
                'dbname': row[5],
                'dphone': row[6],
		        'dtype': row[7],
            }

            for row in buffer_records
        ]
        return render_template('userbuffer.html', records=records_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
