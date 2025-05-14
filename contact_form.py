import streamlit as st
import smtplib
import datetime
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import os
import time

server = st.secrets["SERVER"]
port = st.secrets["PORT"]
u = st.secrets["U"]
secret = st.secrets["SECRET"]
recipient = st.secrets["RECIPIENT"]
log_file = "logs.csv"

def contact_form():
    if os.path.exists(log_file):
        log_df = pd.read_csv(log_file)
    else:
        log_df = pd.DataFrame(columns=["Name", "Email", "Message", "Date", "Time"])

    with st.form(key="contact_form"):
        st.subheader("✉️ Contact Form")
        name = st.text_input("**Your name***", key="name")
        email = st.text_input("**Your email***", key="email")
        message = st.text_area("**💬 Message***", key="message")
        st.markdown('<p style="font-size: 13px;">*Required fields</p>', unsafe_allow_html=True)
        submit = st.form_submit_button(label="Send")

        if submit:
            if not name or not email or not message:
                st.error("Please fill out all required fields.")
            else:
                try:
                    validate_email(email, check_deliverability=True)
                    server = smtplib.SMTP(st.secrets["SERVER"], st.secrets["PORT"])
                    server.starttls()
                    server.login(st.secrets["U"], st.secrets["SECRET"])
                    subject = "Contact Form Submission"
                    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
                    msg = MIMEMultipart()
                    msg["From"] = st.secrets["U"]
                    msg["To"] = st.secrets["RECIPIENT"]
                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, "plain"))
                    server.sendmail(st.secrets["U"], st.secrets["RECIPIENT"], msg.as_string())

                    # Send confirmation email to user
                    current_datetime = datetime.datetime.now()
                    confirmation_subject = f"Confirmation of Contact Form Submission ({current_datetime.date()})"
                    confirmation_body = f"Thank you, {name}, for contacting us! Your message has been received.\n\nYour message: {message}"
                    confirmation_msg = MIMEMultipart()
                    confirmation_msg["From"] = st.secrets["U"]
                    confirmation_msg["To"] = email
                    confirmation_msg["Subject"] = confirmation_subject
                    confirmation_msg.attach(MIMEText(confirmation_body, "plain"))
                    server.sendmail(st.secrets["U"], email, confirmation_msg.as_string())
                    server.quit()

                    # Log the submission
                    formatted_date = current_datetime.strftime("%Y-%m-%d")
                    formatted_time = current_datetime.strftime("%H:%M:%S")
                    new_log = pd.DataFrame([{
                        "Name": name,
                        "Email": email,
                        "Message": message,
                        "Date": formatted_date,
                        "Time": formatted_time,
                    }])
                    log_df = pd.concat([log_df, new_log], ignore_index=True)
                    log_df.to_csv(log_file, index=False)

                    st.toast(f"👋 :green[Hello] :orange[{name}]!")
                    st.success("Your message was sent successfully!")
                    
                    time.sleep(1)
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

                except EmailNotValidError as e:
                    st.error(f"Invalid email address: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

def display_message_log():
    st.subheader("Message Logs")
    if os.path.exists(log_file):
        log_df = pd.read_csv(log_file)
    else:
        log_df = pd.DataFrame(columns=["Name", "Email", "Message", "Date", "Time"])

    if not log_df.empty:
        log_df.index = log_df.index + 1 
        st.dataframe(log_df)
    else:
        st.info("No messages sent yet.")

def main():
    st.title("Contact Form App")
    if st.checkbox("✉️ Contact Me"):
        contact_form()


    if st.button("Message Logs"):
        display_message_log()

    st.markdown("""
    <div style="position: fixed; bottom: 0; width: 100%;">
        <p style="text-align: left; color: #a3a0a3; margin-bottom: 28px; font-size: 11px;">
            <a href="https://github.com/jlnetosci/streamlit-contact-form" target="_blank" style="color: inherit;">Base template</a> by: 
            <a href="https://github.com/jlnetosci" target="_blank" style="color: inherit;">João L. Neto</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
