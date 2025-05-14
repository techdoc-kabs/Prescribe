import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='mhpss_db',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None




def get_user_sessions_dataframe(date_filter='all', start_date=None, end_date=None):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT session_id, student_id, user_name, name, login_time, logout_time, duration, status
                FROM user_sessions
            """)
            rows = cursor.fetchall()
            columns = ['session_id', 'student_id', 'user_name', 'name', 'login_time', 'logout_time', 'duration', 'status']
            df = pd.DataFrame(rows, columns=columns)
            df['duration'] = df['duration'].apply(lambda x: format_duration(x) if x is not None else 'N/A')
            

            df['login_time'] = pd.to_datetime(df['login_time'])
            if date_filter == 'Today':
                today = datetime.today().date()
                df = df[df['login_time'].dt.date == today]
            elif date_filter == 'This Week':
                start_of_week = datetime.today() - timedelta(days=datetime.today().weekday())
                df = df[df['login_time'] >= start_of_week]
            elif date_filter == 'This Month':
                start_of_month = datetime.today().replace(day=1)
                df = df[df['login_time'] >= start_of_month]
            elif date_filter == 'This Year':
                start_of_year = datetime.today().replace(month=1, day=1)
                df = df[df['login_time'] >= start_of_year]
            elif date_filter == 'Custom Range' and start_date and end_date:
                df = df[(df['login_time'].dt.date >= start_date) & (df['login_time'].dt.date <= end_date)]
            
            all_columns = df.columns.tolist()
            selected_columns = st.sidebar.multiselect("Select columns to display", all_columns, default=all_columns)
            df = df[selected_columns]
            return df
        except Exception as e:
            st.error(f"Error fetching user sessions: {e}")
            return None
        finally:
            cursor.close()
            connection.close()


def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    duration_parts = []
    if hours > 0:
        duration_parts.append(f"{hours} hr{'s' if hours > 1 else ''}")
    if minutes > 0:
        duration_parts.append(f"{minutes} min{'s' if minutes > 1 else ''}")
    if secs > 0 or not duration_parts:
        duration_parts.append(f"{secs} sec{'s' if secs > 1 else ''}")
    return ", ".join(duration_parts)



def main():
    date_filter = st.sidebar.selectbox(
        "Select Date Range", 
        ('Today', 'This Week', 'This Month', 'This Year', 'Custom Range', 'All Time'),
        index=5)
    start_date, end_date = None, None
    if date_filter == 'Custom Range':
        start_date = st.sidebar.date_input("Start Date", value=datetime.today().date() - timedelta(days=7))
        end_date = st.sidebar.date_input("End Date", value=datetime.today().date())

    col1, col2, col3 = st.columns([1, 1, 4])
    df = get_user_sessions_dataframe(date_filter=date_filter, start_date=start_date, end_date=end_date)
    
  
    df.index = df.index + 1
    active_users_count = df[df['status'] == 'active'].shape[0]
    inactive_users_count = df[df['status'] == 'inactive'].shape[0]
    background_color1 = "#4CAF50"
    # background_color2 = "#FF0000"
    with col1:
        with st.container():
            st.metric(label="Active Users", value=active_users_count)
            style_metric_cards(background_color=background_color1, box_shadow=True, border_radius_px=100)

    with col2:
        with st.container():
            st.metric(label="Inactive Users", value=inactive_users_count)
            style_metric_cards(background_color="#4CAF50", box_shadow=True, border_radius_px=10)

    if col3.checkbox('Show User Sessions'):
        st.write(f"Showing user sessions for {date_filter}")
        st.write(df)

if __name__ == "__main__":
    main()
