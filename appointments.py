import streamlit as st
# import mysql.connector
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
from datetime import datetime

def create_connection():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'port': 3306,
        'database': 'kabs_db'
    }
    db = mysql.connector.connect(**config)
    return db


def generate_appointment_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM appointments")
    result = cursor.fetchone()
    count = result[0] if result[0] is not None else 0
    current_year = datetime.now().year
    new_id = f"APP-{current_year}-{count + 1:04}"
    return new_id


def create_appointments_table(db):
    cursor = db.cursor()
    create_appointments_table_query = """
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id VARCHAR(20) PRIMARY KEY,
        student_id VARCHAR(20),
        student_name VARCHAR(255),
        appointment_type VARCHAR(255) DEFAULT 'NEW',
        appointment_date DATE,
        appointment_time TIME,
        clinician_name VARCHAR(255),
        reason TEXT,
        FOREIGN KEY (student_id) REFERENCES students(STUDENT_ID)
    )
    """
    cursor.execute(create_appointments_table_query)
    db.commit()


def determine_appointment_type(db, student_id):
    cursor = db.cursor()
    query = """
    SELECT COUNT(*) FROM appointments WHERE student_id = %s
    """
    cursor.execute(query, (student_id,))
    count = cursor.fetchone()[0]
    return "NEW" if count == 0 else "REVISIT"


def insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason):
    if check_for_duplicate_appointment(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason):
        st.warning("Duplicate appointment detected for the same student ID.")
        return  
    cursor = db.cursor()
    cursor.execute("SELECT STUDENT_NAME FROM students WHERE STUDENT_ID = %s", (student_id,))
    student_name = cursor.fetchone()
    if student_name:
        student_name = student_name[0]
    
    appointment_id = generate_appointment_id(db)
    appointment_time_str = appointment_time.strftime("%H:%M:%S")  # Ensure time is in the correct format
    appointment_date_str = appointment_date.strftime("%Y-%m-%d")
    reason_str = ', '.join(reason) if reason else ""  # Join reasons as a comma-separated string
    insert_appointment_query = """
    INSERT INTO appointments (appointment_id, student_id, student_name, appointment_type, appointment_date, appointment_time, clinician_name, reason)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    appointment_data = (appointment_id, student_id, student_name, appointment_type, appointment_date_str, appointment_time_str, clinician_name, reason_str)

    try:
        cursor.execute(insert_appointment_query, appointment_data)
        db.commit()
        st.success("Appointment created successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")



def update_appointment_record(db, appointment_id, new_appointment_type, new_appointment_date, new_appointment_time, new_clinician_name, new_reason):
    cursor = db.cursor()
    update_appointment_query = """
    UPDATE appointments
    SET appointment_type = %s, appointment_date = %s, appointment_time = CAST(%s AS TIME), clinician_name = %s, reason = %s
    WHERE appointment_id = %s
    """
    appointment_data = (new_appointment_type, new_appointment_date, new_appointment_time, new_clinician_name, new_reason, appointment_id)
    cursor.execute(update_appointment_query, appointment_data)
    db.commit()


def delete_appointment(db, appointment_id):
    cursor = db.cursor()
    delete_appointment_query = """
    DELETE FROM appointments
    WHERE appointment_id = %s
    """
    cursor.execute(delete_appointment_query, (appointment_id,))
    db.commit()
    st.warning("Appointment deleted.")

clinicians = ['','Dr.Paul','Dr.Cissy','Dr.James']
appointment_reasons = ['','Assessemnt','Group session','Indiviual therapy','Family therapy']
st.session_state["appointment_reasons"] = appointment_reasons


def edit_appointment(db):
    with st.form('edit appointment'):
        appointment = st.session_state.edit_appointment
        new_appointment_type = st.text_input('APPOINTMENT_TYPE', appointment[3])
        new_appointment_date = st.date_input("APPOINTMENT DATE", value=pd.to_datetime(appointment[4]).date())
        new_appointment_time = st.time_input("APPOINTMENT TIME", value=pd.to_datetime(appointment[5]).time())
        new_clinician_name = st.selectbox("CLINICIAN", clinicians, index=clinicians.index(appointment[6]))
        new_reason = st.multiselect("REASON", appointment_reasons, default=appointment[7].split(", "))
        update = st.form_submit_button("Update Appointment")
        if update:
            reason_str = ', '.join(new_reason) 
            update_appointment_record(db, appointment[0], new_appointment_type, new_appointment_date, new_appointment_time, new_clinician_name, reason_str)
            st.success('Appointment updated')


def fetch_appointment_by_id(db, appointment_id):
    cursor = db.cursor()
    select_appointment_query = """
       SELECT a.appointment_id, a.student_id, a.student_name, a.appointment_type, a.appointment_date, CAST(a.appointment_time AS CHAR), a.clinician_name, a.reason
       FROM appointments a
       WHERE a.appointment_id = %s
       """
    cursor.execute(select_appointment_query, (appointment_id,))
    appointment = cursor.fetchone()
    return appointment



def fetch_appointments(db, search_input):
    cursor = db.cursor(dictionary=True)
    if search_input.strip().upper().startswith("APP-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type, clinician_name, reason
        FROM appointments
        WHERE appointment_id = %s
        """
        cursor.execute(query, (search_input.strip(),))
    else: 
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("student_name LIKE %s")
            query_conditions.append("student_name LIKE %s")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("student_name LIKE %s")
            params.append(f"%{search_input}%")
        query = f"""
        SELECT student_id, student_name, appointment_id, appointment_date, appointment_type, clinician_name, reason
        FROM appointments
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))

    return cursor.fetchall()



def search_edit_and_update_appointment(db, appointment_id):
    appointment = fetch_appointment_by_id(db, appointment_id)
    if appointment:
        st.session_state.edit_appointment= appointment
    if 'edit_appointment' in st.session_state:
        edit_appointment(db)
    else:
        st.error("Student record not found in the database.")


#### APPOINTMENTS ######
def show_all_appointments(db):
    cursor = db.cursor()
    select_query = """
    SELECT appointment_id, student_id, student_name, appointment_type, appointment_date, CAST(appointment_time AS CHAR), clinician_name, reason
    FROM appointments
    """
    cursor.execute(select_query)
    records = cursor.fetchall()
    if records:
        df = pd.DataFrame(records, columns=['Appointment ID', 'Student ID', 'Student Name', 'Appointment Type', 'Appointment Date', 'Appointment Time', 'Clinician Name', 'Reason'])
        st.write(f'No. of appointments: {len(df)}')
        st.dataframe(df)
    else:
        st.warning("No appointments found")


def fetch_student_by_id(db, student_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE STUDENT_ID = %s", (student_id,))
    return cursor.fetchone()

clinians = ['','Dr.Paul','Dr.Cissy','Dr.James']
appointment_reasons = ['','Assessemnt','Group session','Indiviual therapy','Family therapy']

   
def check_for_duplicate_appointment(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason):
    query = """
        SELECT COUNT(*) 
        FROM appointments 
        WHERE student_id = %s 
        AND appointment_type = %s
        AND appointment_date = %s 
        AND appointment_time = %s
        AND clinician_name = %s
        AND reason IN (%s)
    """
    cursor = db.cursor()
    cursor.execute(query, (student_id, appointment_type, appointment_date, appointment_time, clinician_name, ','.join(reason)))
    result = cursor.fetchone()[0]
    cursor.close()
    return result > 0


def fetch_students(db, search_input):
    cursor = db.cursor(dictionary=True)
    if search_input.strip().upper().startswith("STUD-") or search_input.isdigit():
        query = """
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE student_id = %s
        """
        cursor.execute(query, (search_input.strip(),))
    else: 
        name_parts = search_input.strip().split()
        query_conditions = []
        params = []

        if len(name_parts) == 2:
            first_name, last_name = name_parts
            query_conditions.append("student_name LIKE %s")
            query_conditions.append("student_name LIKE %s")
            params.extend([f"%{first_name} {last_name}%", f"%{last_name} {first_name}%"])
        else:
            query_conditions.append("student_name LIKE %s")
            params.append(f"%{search_input}%")
        query = f"""
        SELECT student_id, student_name, age, gender, class, stream
        FROM students
        WHERE {" OR ".join(query_conditions)}
        """
        cursor.execute(query, tuple(params))
    return cursor.fetchall()


def get_student_select_list(db):
    cursor = db.cursor()
    cursor.execute("SELECT STUDENT_ID, STUDENT_NAME FROM students")
    students = cursor.fetchall()
    select_list = [""] 
    select_list += [f"{student[0]} - {student[1]}" for student in students]
    return select_list

#### DRIVER CODE #######

def main():
    db = create_connection()
    create_appointment_students_table()

    appoint_menu = option_menu(
        menu_title='',
        orientation='horizontal',
        menu_icon='',
        options=['Schedule Appointment', 'Edit Appointment', 'Booked', 'Status'],
        icons=['calendar-plus', 'book', 'database', 'person-circle'],
        styles={
            "container": {"padding": "10!important", "background-color": 'black', 'border': '0.01px dotted red'},
            "icon": {"color": "red", "font-size": "12px"},
            "nav-link": {"color": "#d7c4c1", "font-size": "12px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
            "nav-link-selected": {"background-color": "green"},
        },
        key="register_menu"
    )

    if appoint_menu == 'Schedule Appointment':
        schedule_option = st.sidebar.selectbox("Choose appointment type:", ['One Student', 'All Students'])
        if schedule_option == 'One Student':
            st.sidebar.subheader("STUDENT DETAILS")
            with st.sidebar.expander("🔍SEARCH", expanded=True):
                search_input = st.text_input("Enter Name or Student ID", "")
            results = []
            if search_input.strip():
                results = fetch_students(db, search_input)
            selected_record = None
            if results:
                st.sidebar.write(f"**{len(results)} result(s) found**")
                options = {f"{r['student_name']} - {r['student_id']}": r for r in results}
                selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
                selected_record = options[selected_option]
            if selected_record:
                with st.sidebar.expander("📄 STUDENT DETAILS", expanded=True):
                    st.write(f"Student ID: {selected_record['student_id']}")
                    st.write(f"Student Name: {selected_record['student_name']}")
                    st.write(f"Age(Yrs): {selected_record['age']}")
                    st.write(f"Sex: {selected_record['gender']}")
                    st.write(f"Class: {selected_record['class']}")
                    st.write(f"Stream: {selected_record['stream']}")
                
                st.session_state["student_id"] = selected_record["student_id"]
                st.session_state["student_name"] = selected_record["student_name"]
                student_id = st.session_state.student_id
                student_name= st.session_state.student_name
                with st.form("Vender"):
                    appointment_type = determine_appointment_type(db, student_id)
                    st.write(f"APPOINTMENT TYPE: {appointment_type}")
                    appointment_date = st.date_input("APPOINTMENT DATE:", key="appointment_date")
                    appointment_time = st.time_input("APPOINTMENT TIME:", key="appointment_time")
                    clinician_name = st.selectbox("CLINICIAN:", clinians)  # Ensure 'clinians' is defined
                    reason = st.multiselect("REASON FOR APPOINTMENT:", appointment_reasons)  # Ensure 'appointment_reasons' is defined
                    submit = st.form_submit_button("Schedule Appointment")
                    if submit:
                        if not appointment_date or not appointment_time or not clinician_name or not reason:
                            st.warning("Please fill in all the fields before submitting.")
                        else:
                            if check_for_duplicate_appointment(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason):
                                st.warning("Duplicate appointment detected: An appointment with the same parameters already exists.")
                            else:
                                insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason)
                                st.success(f"{student_name} for {reason} by {clinician_name}.")
            else:
                st.info("Search for student and create appointment.")
        
        

        elif schedule_option == 'All Students':
            all_students = get_student_select_list(db)
            with st.expander('SCHEDULE', expanded = True):
                if all_students:
                    student_id = st.session_state.student_id
                    appointment_type = determine_appointment_type(db, student_id)
                    appointment_date = st.date_input("APPOINTMENT DATE:", key="appointment_date_all")
                    appointment_time = st.time_input("APPOINTMENT TIME:", key="appointment_time_all")
                    clinician_name = st.selectbox("CLINICIAN:", clinians)
                    reason = st.multiselect("REASON FOR APPOINTMENT:", appointment_reasons)  # Ensure 'appointment_reasons' is defined
                    submit = st.button(":red[Schedule Appointments for All Students]")
                    if submit:
                        if not appointment_type or not appointment_date or not appointment_time or not clinician_name or not reason:
                            st.error("Please fill in all the fields before submitting.")
                        else:
                            for student_entry in all_students:
                                student_id = student_entry.split(" - ")[0]
                                student = fetch_student_by_id(db, student_id)
                                if not student:
                                    continue
                                if check_for_duplicate_appointment(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason):
                                    st.warning(f"Duplicate appointment detected for student {student_entry}. Skipping.")
                                else:
                                    insert_appointment_record(db, student_id, appointment_type, appointment_date, appointment_time, clinician_name, reason)
                            st.success(f"{len(all_students)} scheduled for {reason}.")
                else:
                    st.error("No students found to schedule appointments for.")


    elif appoint_menu == "Edit Appointment":
        st.sidebar.subheader("APPOINTMENT DETAILS")
        with st.sidebar.expander("🔍SEARCH", expanded=True):
            search_input = st.text_input("Enter Name or Appointment ID", "")
        results = []
        if search_input.strip():
            results = fetch_appointments(db, search_input)
        selected_record = None
        if results:
            st.sidebar.write(f"**{len(results)} result(s) found**")
            options = {f"{r['student_name']} - {r['appointment_id']}": r for r in results}
            selected_option = st.sidebar.selectbox("Select a record:", list(options.keys()))
            selected_record = options[selected_option]
        if selected_record:
            with st.sidebar.expander("📄 APPOINTMENT DETIALS", expanded=True):
                st.write(f"Student ID: {selected_record['student_id']}")
                st.write(f"Student Name: {selected_record['student_name']}")
                st.write(f"Appointment ID: {selected_record['appointment_id']}")
                st.write(f"Appointment Date: {selected_record['appointment_date']}")
                st.write(f"Appointment Type: {selected_record['appointment_type']}")
                st.write(f"Clinician: {selected_record['clinician_name']}")
                st.write(f"Appointment Reason: {selected_record['reason']}")
            student_id = st.session_state.student_id
            student_name= st.session_state.student_name
            appointment_id= st.session_state.appointment_id
            search_edit_and_update_appointment(db, appointment_id)
    
    elif appoint_menu == "Booked":
        show_all_appointments(db)

    elif appoint_menu == 'Status':
        st.write("Status section is under development.")



if __name__ == "__main__":
    main()
