
import streamlit as st
import base64
import os










def main():
    set_custom_background(bg_color="#2c3e50", sidebar_img=None)


    if 'student_name' not in st.session_state:
        st.session_state.student_name = ''

    page_menu = get_menu()
    if st.session_state["username"]:
        st.sidebar.success(f'👋 Hi :orange[{st.session_state["username"]}]')
        student_info = fetch_student_record(st.session_state["username"])
        st.sidebar.write(student_info)
        if st.sidebar.button(":red[Sign Out]"):
            username = st.session_state["username"]
            st.toast(f"👋 :green[Bye] :green[{username}]")    
            st.session_state.clear()  
            st.rerun()    
        if st.session_state["selected_page"]:
            if st.button("🔙 Return to Menu"):
                st.session_state["selected_page"] = None  
                st.rerun()
            if st.session_state.username:
                student_details = fetch_student_details_by_username(st.session_state.username)
                if student_details:
                    st.session_state.student_id = student_details.get("student_id")
                    st.session_state.name = student_details.get("name")
                    st.session_state.gender = student_details.get("gender")
                    st.session_state.age = student_details.get("age")
                    st.session_state.student_class = student_details.get("student_class")
                    st.session_state.stream = student_details.get("stream")
                    st.session_state.contact = student_details.get("contact")
                    st.session_state.email = student_details.get("email")
                    st.session_state.role = student_details.get("role")
                    
                if st.session_state["selected_page"] == "APPOINTMENTS":
                    appointment_details = fetch_appointment_details_by_username(st.session_state.username)
                    if appointment_details:
                        latest_appointment = max(appointment_details, key=lambda x: x["appointment_id"])  # Get the latest appointment
                        appointment_id = latest_appointment.get("appointment_id")
                        appointment_date = latest_appointment.get("appointment_date")
                        st.session_state.appointment_id = latest_appointment.get("appointment_id")
                        st.session_state.appointment_type = latest_appointment.get("appointment_type")
                        st.session_state.appointment_time = latest_appointment.get("appointment_time")
                        st.session_state.clinician_name = latest_appointment.get("clinician_name")
                        st.session_state.appointment_date = latest_appointment.get("appointment_date")
                        st.session_state.reason = latest_appointment.get("reason")
                        student_forms_page.main()
                    else:
                        st.info('No pending assessments, plese wait for Updates')

                elif st.session_state["selected_page"] == "SUPPORT":
                    st.subheader("Support Page")

                elif st.session_state["selected_page"] == "CHAT ROOM":
                    st.subheader("Chats Page")
                
                elif st.session_state["selected_page"] == "CONTENT":
                    video_display.main()
                   
                elif st.session_state["selected_page"] == "PROFILE":
                    st.subheader("Profile Page")
                    student_info = fetch_student_record(st.session_state["username"])
                    if student_info:
                        st.write(student_info)
        
        else:
            col1, col2 = st.columns(2)
            for index, page in enumerate(pages):
                with col1 if index % 2 == 0 else col2:
                    if card(
                        title=page["title"],
                        text=page['text'],
                        image=page["icon"],
                        key=page["title"],
                        styles={
                            "card": {
                                "width": "300px",
                                "height": "250px",
                                "border-radius": "30px",
                                "background": f"linear-gradient(135deg, {page['color']}, #ffffff)",
                                "color": "white",
                                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",
                                "border": f"2px solid {page['color']}",
                                "text-align": "center",
                            },
                            "text": {"font-family": "serif", "font-size": "16px"},
                        },
                    ):
                        st.session_state["selected_page"] = page["title"]
                        st.rerun()





if __name__ == "__main__":
    main()

