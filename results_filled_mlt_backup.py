
import streamlit as st
import json
import pandas as pd
import os
import appointments
import requested_tools
from datetime import datetime
import captured_responses 
import seaborn as sns
import sqlite3
import plotly.express as px


def create_connection():
    try:
        db = sqlite3.connect("mhpss_db.sqlite", check_same_thread=False)
        db.row_factory = sqlite3.Row
        return db
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def fetch_requested_tools_students(db, appointment_id):
    cursor = db.cursor()
    query = """
    SELECT tool_name, tool_status 
    FROM requested_tools_students
    WHERE appointment_id = ?
    """
    cursor.execute(query, (appointment_id,))
    result = cursor.fetchall()
    tools_status = {row[0]: row[1] for row in result}
    cursor.close()
    return tools_status

def update_tool_status(db, appointment_id, tool_name, new_status):
    cursor = db.cursor()
    update_query = """
    UPDATE requested_tools_students
    SET tool_status = ?
    WHERE appointment_id = ? AND tool_name = ?
    """
    cursor.execute(update_query, (new_status, appointment_id, tool_name))
    db.commit()


def check_existing_entry(db, appointment_id):
    try:
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM PHQ_9forms WHERE appointment_id = ?"
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()[0]
        return result > 0
    except Exception as e:
        st.error(f"An error occurred while checking for duplicates: {e}")
        return False
    finally:
        cursor.close()


def capture_PHQ_9_responses():
    responses = []
    answered_questions = set()

    with st.form('PHQ-9'):
        st.write('PATIENT HEALTH QUESTIONNAIRE-9 (PHQ-9 Form)')
        for i, question in enumerate(questions, start=1):
            st.markdown(f"<span style='color:steelblue; font-weight:bold'>{i}. {question}</span>", unsafe_allow_html=True)
            selected_radio = st.radio(f'', ['Select from options below', 'Not at all', 'Several Days', 'More Than Half the Days', 'Nearly Every Day'], key=f"q{i}")
            if selected_radio != 'Select from options below':
                responses.append({'question': f'Q{i}', 'response': selected_radio})
                answered_questions.add(i)
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            if len(answered_questions) != len(questions):
                st.warning('Please complete the entire form')
    return responses

tool_status = ['Pending','Completed']
tools_template_dict = {
    'PHQ-9': capture_PHQ_9_responses,
    'GAD-7' :'capture_GAD-7_responses',
    'BDI' :'capture_BDI_responses'}
tool_respnse_dict = {
    'PHQ-9': 'PHQ-9_responses',
    'GAD-7': 'GAD-7_responses',
    'BDI':'BDI_responses'}


def fetch_latest_phq9(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT 
            phq_score, 
            depression_status,
            suicide_response,
            suicide_risk
        FROM PHQ_9forms 
        WHERE appointment_id = ?
        ORDER BY assessment_date DESC
        LIMIT 1
        """
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        
        if result:
            columns = ["PHQ Score", "Depression Status", "Suicide Response", "Suicide Risk"]
            return pd.DataFrame([result], columns=columns)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching PHQ-9: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def fetch_latest_gad7(db, appointment_id):
    try:
        cursor = db.cursor()
        query = """
        SELECT 
            gad_score,
            anxiety_status 
        FROM gad_7forms 
        WHERE appointment_id = ?
        ORDER BY assessment_date DESC
        LIMIT 1
        """
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        
        if result:
            columns = ["GAD-7 Score", "Anxiety Status"]
            return pd.DataFrame([result], columns=columns)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching GAD-7: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def style_gad7_dataframe(df):
    anxiety_colors = {
        "Severe anxiety": "red",
        "Moderate anxiety": "orange",
        "Mild anxiety": "yellow",
        "Minimal anxiety": "green"
    }

    def highlight_anxiety(val):
        return f"background-color: {anxiety_colors.get(val, '')}; color: black" if val in anxiety_colors else ""

    styled_df = df.style.applymap(highlight_anxiety, subset=["Anxiety Status"]) \
                         .set_table_styles([{
                             'selector': 'thead th',
                             'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
                         }]) \
                         .hide(axis="index")  
    return styled_df


def colorize(val):
    color = status_colors.get(val, "") or suicide_risk_colors.get(val, "")
    
    if color:
        return f"background-color: {color}; color: white; font-weight: bold;"
    anxiety_colors = {
        "Severe anxiety": "red",
        "Moderate anxiety": "orange",
        "Mild anxiety": "yellow",
        "Minimal anxiety": "green"
    }
    anxiety_color = anxiety_colors.get(val, "")
    if anxiety_color:
        return f"background-color: {anxiety_color}; color: white; font-weight: bold;"

    return ""


def style_phq9_dataframe(df):
    status_colors = {
        "Severe depression": "red",
        "Moderately severe depression": "orange",
        "Moderate depression": "yellow",
        "Mild depression": "blue",
        "Minimal depression": "green",
    }
    
    suicide_risk_colors = {
        "High": "red",
        "Moderate": "yellow",
        "Low": "green"
    }

    def highlight_status(val):
        return f"background-color: {status_colors.get(val, '')}; color: white" if val in status_colors else ""
    def highlight_suicide_risk(val):
        return f"background-color: {suicide_risk_colors.get(val, '')}; color: white" if val in suicide_risk_colors else ""
    styled_df = df.style.applymap(highlight_status, subset=["Depression Status"]) \
                         .applymap(highlight_suicide_risk, subset=["Suicide Risk"]) \
                         .set_table_styles([{
                             'selector': 'thead th',
                             'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
                         }]) \
                         .hide(axis="index")
    return styled_df


def highlight_headers(df):
    return df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}
    ])


def style_summary_dataframe(df):
    status_colors = {
        "Severe depression": "red",
        "Moderately severe depression": "orange",
        "Moderate depression": "yellow",
        "Mild depression": "blue",
        "Minimal depression": "green",
    }
    suicide_risk_colors = {
        "High": "red",
        "Moderate": "yellow",
        "Low": "green"
    }
    anxiety_colors = {
        "Severe anxiety": "red",
        "Moderate anxiety": "orange",
        "Mild anxiety": "yellow",
        "Minimal anxiety": "green"
    }
    def highlight_status(val):
        return f"background-color: {status_colors.get(val, '')}; color: white" if val in status_colors else ""
    def highlight_suicide_risk(val):
        return f"background-color: {suicide_risk_colors.get(val, '')}; color: white" if val in suicide_risk_colors else ""
    def highlight_anxiety(val):
        return f"background-color: {anxiety_colors.get(val, '')}; color: white" if val in anxiety_colors else ""
    styled_df = df.style.applymap(highlight_status, subset=["Depression Status"]) \
                         .applymap(highlight_suicide_risk, subset=["Suicide Risk"]) \
                         .applymap(highlight_anxiety, subset=["Anxiety Status"]) \
                         .applymap(
                             lambda x:'font-size: 8; border-radius: 10px; padding: 1px; border: 1px  white;'  # Encircle text
                         ) \
                         .set_table_styles([{
                             'selector': 'thead th',
                             'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]
                         }]) \
                         .hide(axis="index")
    return styled_df
def generate_summary_dataframe(db, appointment_id):
    try:
        phq9_df = fetch_latest_phq9(db, appointment_id)
        gad7_df = fetch_latest_gad7(db, appointment_id)
        
        if not phq9_df.empty and not gad7_df.empty:
            summary_data = {
                "PHQ Score": phq9_df["PHQ Score"].values[0],
                "Depression Status": phq9_df["Depression Status"].values[0],
                'Suicide Score': phq9_df['Suicide Response'].values[0],
                "Suicide Risk": phq9_df["Suicide Risk"].values[0],
                "GAD-7 Score": gad7_df["GAD-7 Score"].values[0],
                "Anxiety Status": gad7_df["Anxiety Status"].values[0]
            }
            summary_df = pd.DataFrame([summary_data])
            return style_summary_dataframe(summary_df)

        elif not phq9_df.empty:
            summary_data = {
                "PHQ Score": phq9_df["PHQ Score"].values[0],
                "Depression Status": phq9_df["Depression Status"].values[0],
                'Suicide Score': phq9_df['Suicide Response'].values[0],
                "Suicide Risk": phq9_df["Suicide Risk"].values[0],
                "GAD-7 Score": "N/A",
                "Anxiety Status": "N/A"
            }
            summary_df = pd.DataFrame([summary_data])
            return style_summary_dataframe(summary_df)

        elif not gad7_df.empty:
            summary_data = {
                "PHQ Score": "N/A",
                "Depression Status": "N/A",
                'Suicide Score':'N/A',
                "Suicide Risk": "N/A",
                "GAD-7 Score": gad7_df["GAD-7 Score"].values[0],
                "Anxiety Status": gad7_df["Anxiety Status"].values[0]
            }
            summary_df = pd.DataFrame([summary_data])
            summary_df = summary_df.reset_index(drop=True)
            summary_df.index = summary_df.index + 1
            return style_summary_dataframe(summary_df)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return pd.DataFrame()


##### MLTIPLE RESLTS 
status_colors = {
    "Severe depression": "red",
    "Moderately severe depression": "orange",
    "Moderate depression": "yellow",
    "Mild depression": "blue",
    "Minimal depression": "green",}

suicide_risk_colors = {
    "High": "red",
    "Moderate": "yellow",
    "Low": "green"
}

anxiety_colors = {
    "Severe anxiety": "red",
    "Moderate anxiety": "orange",
    "Mild anxiety": "yellow",
    "Minimal anxiety": "green"
}

functioning_colors = {
    "Extremely difficult": "red",
    "Very difficult": "orange",
    "Somewhat difficult": "yellow",
    "Not difficult at all": "green"
}

def highlight_cells(val):
    color = (
        status_colors.get(val, "") or
        suicide_risk_colors.get(val, "") or
        anxiety_colors.get(val, "") or 
        functioning_colors.get(val, ""))
    if color:
        return f"background-color: {color}; color: black; font-weight: bold;"
    return ""

def style_fetched_dataframe(df):
    styled_df = df.style.applymap(highlight_cells) \
        .set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}
        ]) \
        .hide(axis="index") 
    return styled_df

def fetch_multiple_students_appointments(db):
    cursor = db.cursor()
    fetch_query = """
    SELECT s.student_id, s.name, s.student_class, s.stream, r.appointment_id, r.term, r.screen_type, f.difficulty_level
    FROM student_users s
    JOIN requested_tools_students r ON s.student_id = r.student_id
    JOIN functioning_responses f ON r.appointment_id = f.appointment_id  -- Fixed alias
    GROUP BY s.student_id, r.appointment_id, f.appointment_id
    """
    cursor.execute(fetch_query)
    results = cursor.fetchall()
    cursor.close()
    return results


def filter_data(df):
    student_id_filter = st.sidebar.multiselect('Select Student IDs', df['Student ID'].unique())
    student_name_filter = st.sidebar.multiselect('Select Student Names', df['Student Name'].unique())
    student_class_filter = st.sidebar.multiselect('Select Student Class', df['Class'].unique())
    stream_filter = st.sidebar.multiselect('Select Stream', df['Stream'].unique())
    term_filter = st.sidebar.multiselect('Select Term', df['Term'].unique())
    screen_type_filter = st.sidebar.multiselect('Select Screen Type', df['Screen_Type'].unique())
    difficulty_level_filter = st.sidebar.multiselect('Select Difficulty Level', df['Functioning'].unique())
    depression_status_filter = st.sidebar.multiselect('Depression Status', df.get('Depression Status', pd.Series()).unique())
    suicide_risk_filter = st.sidebar.multiselect('Suicide Risk', df.get('Suicide Risk', pd.Series()).unique())
    anxiety_status_filter = st.sidebar.multiselect('Anxiety Status', df.get('Anxiety Status', pd.Series()).unique())
    if student_id_filter:
        df = df[df['Student ID'].isin(student_id_filter)]
    if student_name_filter:
        df = df[df['Student Name'].isin(student_name_filter)]
    if student_class_filter:
        df = df[df['Class'].isin(student_class_filter)]
    if stream_filter:
        df = df[df['Stream'].isin(stream_filter)]
    if term_filter:
        df = df[df['Term'].isin(term_filter)]
    if screen_type_filter:
        df = df[df['Screen_Type'].isin(screen_type_filter)]
    if difficulty_level_filter:
        df = df[df['Functioning'].isin(difficulty_level_filter)]
    if depression_status_filter:
        df = df[df['Depression Status'].isin(depression_status_filter)]
    if suicide_risk_filter:
        df = df[df['Suicide Risk'].isin(suicide_risk_filter)]
    if anxiety_status_filter:
        df = df[df['Anxiety Status'].isin(anxiety_status_filter)]
    available_columns = df.columns.tolist()
    selected_columns = st.sidebar.multiselect("Select Columns to Display", available_columns, default=available_columns)
    return df[selected_columns] 

def display_graphical_view(df):
    st.sidebar.header("Graphical Analysis")
    if df.empty:
        st.warning("No data available to visualize.")
        return
    graph_type = st.sidebar.selectbox("Select Graph Type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
    x_axis = st.sidebar.selectbox("Select X-axis", df.columns)
    y_axis = st.sidebar.selectbox("Select Y-axis", df.select_dtypes(include=['number']).columns)
    if graph_type == "Bar Chart":
        fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
    elif graph_type == "Line Chart":
        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
    elif graph_type == "Pie Chart":
        fig = px.pie(df, names=x_axis, values=y_axis, title=f"Distribution of {y_axis} by {x_axis}")
    elif graph_type == "Scatter Plot":
        fig = px.scatter(df, x=x_axis, y=y_axis, title=f"Scatter Plot of {y_axis} vs {x_axis}")
    st.plotly_chart(fig)

   
### DRIVER CODE ######
def main():
    db = create_connection()
    student_appointments = fetch_multiple_students_appointments(db)
    if not student_appointments:
        st.warning("No student appointments found.")
    else:
        all_results = []  
        for record in student_appointments:
            appointment_id = record["appointment_id"]
            student_id = record["student_id"]
            student_name = record["name"]
            student_class = record['student_class']
            stream = record['stream']
            term = record['term']
            screen_type = record['screen_type']
            difficulty_level = record['difficulty_level']
            requested_tools_students = fetch_requested_tools_students(db, appointment_id)
            tools_list = list(requested_tools_students.keys())
            student_summary = {
                "Student ID": student_id,
                "Student Name": student_name,
                'Class': student_class,
                'Stream' : stream,
                "Appointment ID": appointment_id,  
                'Term': term,
                'Screen_Type': screen_type,
                'Functioning':difficulty_level}
            for tool in tools_list:
                tool_status = requested_tools_students[tool]
                if tool_status == "Completed":
                    if tool == "PHQ-9":
                        phq9_df = fetch_latest_phq9(db, appointment_id)
                        if not phq9_df.empty:
                            phq9_data = phq9_df.iloc[0].to_dict()
                            for key in phq9_data:
                                if isinstance(phq9_data[key], (int, float)): 
                                    phq9_data[key] = int(phq9_data[key])  
                            student_summary.update(phq9_data)
                    elif tool == "GAD-7":
                        gad7_df = fetch_latest_gad7(db, appointment_id)
                        if not gad7_df.empty:
                            gad7_data = gad7_df.iloc[0].to_dict()
                            for key in gad7_data:
                                if isinstance(gad7_data[key], (int, float)):
                                    gad7_data[key] = int(gad7_data[key])  
                            student_summary.update(gad7_data)

            all_results.append(student_summary)
        if all_results:
            results_df = pd.DataFrame(all_results)
            results_df.index = results_df.index + 1
            results_df = filter_data(results_df)
            styled_results_df = style_fetched_dataframe(results_df) 
            st.table(styled_results_df)
            if st.checkbox('Graph'):
                display_graphical_view(results_df)
        else:
            st.info("No completed assessments found for any student.")
    db.close()

if __name__ == "__main__":
    main()



# def filter_and_display_graph(df, group_by_columns, selected_conditions):
#     if df.empty:
#         st.warning("No data available for visualization based on the current filters.")
#         return

#     chart_type = st.radio("Select Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True)

#     color_maps = {
#         "Depression Status": {
#             "Severe depression": "red",
#             "Moderately severe depression": "orange",
#             "Moderate depression": "yellow",
#             "Mild depression": "blue",
#             "Minimal depression": "green"
#         },
#         "Anxiety Status": {
#             "Severe anxiety": "red",
#             "Moderate anxiety": "orange",
#             "Mild anxiety": "yellow",
#             "Minimal anxiety": "green"
#         },
#         "Suicide Risk": {
#             "High": "red",
#             "Moderate": "yellow",
#             "Low": "green"
#         },
#         "Functioning": {
#             "Extremely difficult": "red",
#             "Very difficult": "orange",
#             "Somewhat difficult": "yellow",
#             "Not difficult at all": "green"}}
    
#     for condition_column in selected_conditions:
#         color_map = color_maps.get(condition_column, {})
#         group_cols = group_by_columns + [condition_column] if group_by_columns else [condition_column]
#         plot_data = df.groupby(group_cols).size().reset_index(name="Count")
        
#         if group_by_columns:
#             total_counts = plot_data.groupby(group_by_columns)["Count"].transform("sum")
#         else:
#             total_count = plot_data["Count"].sum()
#             total_counts = pd.Series([total_count] * len(plot_data))
        
#         plot_data["Percentage"] = (plot_data["Count"] / total_counts * 100).round(1)

#         if chart_type == "Bar Chart":
#             plt.figure(figsize=(12, 7))
#             hue_colors = {cond: color_map.get(cond, "gray") for cond in plot_data[condition_column].unique()}
            
#             if group_by_columns:
#                 x_labels = plot_data[group_by_columns].astype(str).agg(" - ".join, axis=1)
#             else:
#                 x_labels = ["Overall"] * len(plot_data)
                
#             ax = sns.barplot(
#                 data=plot_data,
#                 x=x_labels,
#                 y="Count",
#                 hue=condition_column,
#                 palette=hue_colors)
#             for container in ax.containers:
#                 for bar in container:
#                     height = bar.get_height()
#                     if height > 0:
#                         percentage = plot_data.loc[plot_data["Count"] == height, "Percentage"].values[0]
#                         ax.text(
#                             bar.get_x() + bar.get_width() / 2,
#                             height,
#                             f"{height} ({percentage}%)",
#                             ha='center',
#                             va='bottom',
#                             fontsize=12
#                         )

#             # Title and Labels
#             plt.title(f"{condition_column} by {' + '.join(group_by_columns) if group_by_columns else 'Overall'}", fontsize=20)
#             plt.xticks(rotation=45, ha="right", fontsize=13)
#             plt.tight_layout()

#             # Set font size for the legend
#             plt.legend(title=condition_column, loc="upper right", bbox_to_anchor=(1.15, 1), fontsize=12)
#             st.pyplot(plt)

#         elif chart_type == "Pie Chart":
#             if group_by_columns:
#                 for values, sub_data in plot_data.groupby(group_by_columns):
#                     label = " - ".join(str(v) for v in values) if isinstance(values, tuple) else str(values)
#                     labels = sub_data[condition_column]
#                     sizes = sub_data["Count"]
#                     colors = [color_map.get(cond, "gray") for cond in labels]
                    
#                     fig, ax = plt.subplots()
#                     wedges, texts, autotexts = ax.pie(
#                         sizes,
#                         labels=labels,
#                         autopct="%1.1f%%",
#                         startangle=90,
#                         colors=colors,
#                         textprops={"fontsize": 9}
#                     )
#                     ax.axis("equal")
#                     ax.set_title(f"{condition_column} - {label}")
#                     st.pyplot(fig)
#             else:
#                 labels = plot_data[condition_column]
#                 sizes = plot_data["Count"]
#                 colors = [color_map.get(cond, "gray") for cond in labels]

#                 fig, ax = plt.subplots()
#                 wedges, texts, autotexts = ax.pie(
#                     sizes,
#                     labels=labels,
#                     autopct="%1.1f%%",
#                     startangle=90,
#                     colors=colors,
#                     textprops={"fontsize": 9}
#                 )
#                 ax.axis("equal")
#                 ax.set_title(f"{condition_column} - Overall")
#                 st.pyplot(fig)

# def display_critical_condition_summary(df):
#     conditions = st.multiselect("Comorbities", ["Depression Status", "Anxiety Status", "Suicide Risk"])
#     if not conditions:
#         st.warning("Please select at least one critical condition.")
#         return
#     condition_filters = {}
#     for condition in conditions:
#         condition_filters[condition] = st.selectbox(f"Select Severity for {condition}",
#                                              sorted(df[condition].dropna().unique()))
#     filter_query = (df[conditions[0]] == condition_filters[conditions[0]])
#     for condition in conditions[1:]:
#         filter_query &= (df[condition] == condition_filters[condition])
#     critical_df = df[filter_query]
#     if critical_df.empty:
#         st.warning("No students meet the selected critical condition combination.")
#         return
#     valid_classes = sorted(critical_df['Class'].dropna().unique())
#     valid_streams = sorted(critical_df['Stream'].dropna().unique())
#     valid_screens = sorted(critical_df['Screen_Type'].dropna().unique())
#     selected_class = st.multiselect("Select Class", valid_classes, default=valid_classes)
#     selected_stream = st.multiselect("Select Stream", valid_streams, default=valid_streams)
#     selected_screen_type = st.multiselect("Select Screen Type", valid_screens, default=valid_screens)
#     critical_df = critical_df[
#         (critical_df['Class'].isin(selected_class)) &
#         (critical_df['Stream'].isin(selected_stream)) &
#         (critical_df['Screen_Type'].isin(selected_screen_type))]
#     if critical_df.empty:
#         st.warning("No students meet the selected criteria.")
#         return
#     critical_df['Group'] = critical_df['Class'] + "-" + critical_df['Stream'] + "-" + critical_df['Screen_Type']
#     grouped = critical_df.groupby('Group').size().reset_index(name="Count")
#     total = grouped["Count"].sum()
#     plt.figure(figsize=(12, 6))
#     ax = sns.barplot(data=grouped, x='Group', y="Count", palette="viridis")
#     for i, row in grouped.iterrows():
#         percent = f"{(row['Count'] / total) * 100:.1f}%"
#         ax.text(i, row["Count"], f"{row['Count']} ({percent})", ha='center', va='bottom', fontsize=12)
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
#     title_conditions = " + ".join([f"{condition_filters[cond]}" for cond in conditions])
#     plt.title(f"{title_conditions}", fontsize = 20)
#     plt.tight_layout()
#     st.pyplot(plt)





def main():
    selected = option_menu(
        menu_title=None,
        options=["Dataframe", "Summary Data", "Visio", 'Report'],
        icons=["table", "bar-chart-line", "graph-up", 'printer'],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
            "icon": {"color": "red", "font-size": "15px"},
            "nav-link": {"color": "#d7c4c1", "font-size": "15px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
            "nav-link-selected": {"background-color": "green"},
        },
        key="selected")

    # Check if the data has been already processed and stored in session state
    if "student_appointments" not in st.session_state:
        db = create_connection()
        student_appointments = fetch_multiple_students_appointments(db)
        if not student_appointments:
            st.warning("No student appointments found.")
            db.close()
            return
        all_results = []
        for record in student_appointments:
            appointment_id = record["appointment_id"]
            student_id = record["student_id"]
            student_name = record["name"]
            student_class = record['student_class']
            stream = record['stream']
            term = record['term']
            screen_type = record['screen_type']
            difficulty_level = record['difficulty_level']
            requested_tools_students = fetch_requested_tools_students(db, appointment_id)
            tools_list = list(requested_tools_students.keys())
            student_summary = {
                "Student ID": student_id,
                "Student Name": student_name,
                'Class': student_class,
                'Stream': stream,
                "Appointment ID": appointment_id,
                'Term': term,
                'Screen_Type': screen_type,
                'Functioning': difficulty_level}
            for tool in tools_list:
                if requested_tools_students[tool] == "Completed":
                    if tool == "PHQ-9":
                        phq9_df = fetch_latest_phq9(db, appointment_id)
                        if not phq9_df.empty:
                            phq9_data = phq9_df.iloc[0].to_dict()
                            for key in phq9_data:
                                if isinstance(phq9_data[key], (int, float)):
                                    phq9_data[key] = int(phq9_data[key])
                            student_summary.update(phq9_data)
                    elif tool == "GAD-7":
                        gad7_df = fetch_latest_gad7(db, appointment_id)
                        if not gad7_df.empty:
                            gad7_data = gad7_df.iloc[0].to_dict()
                            for key in gad7_data:
                                if isinstance(gad7_data[key], (int, float)):
                                    gad7_data[key] = int(gad7_data[key])
                            student_summary.update(gad7_data)
            all_results.append(student_summary)
        db.close()

        if not all_results:
            st.info("No completed assessments found for any student.")
            return

        st.session_state.student_appointments = all_results
    else:
        all_results = st.session_state.student_appointments

    results_df = pd.DataFrame(all_results)
    results_df.index = results_df.index + 1

    if selected == "Dataframe":
        with st.sidebar:
            filter_menu = option_menu(
                menu_title="",
                options=["All Results", 'Customize'],
                icons=["table", "table"],
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
                    "icon": {"color": "red", "font-size": "15px"},
                    "nav-link": {"color": "#d7c4c1", "font-size": "15px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                    "nav-link-selected": {"background-color": "green"},
                },
                key="analysis_menu"
            )
        filtered_df = filter_data(results_df, filter_menu)
        st.session_state.filtered_df = filtered_df  # Store filtered data in session state
        styled_results_df = style_fetched_dataframe(filtered_df)
        st.table(styled_results_df)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered Results')
            writer.close()
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name='filtered_results.csv',
            mime='text/csv'
        )

    elif selected == "Summary Data":
        df_data = st.session_state.filtered_df if "filtered_df" in st.session_state else results_df
        st.markdown("#### 📊 Overall Summary")
        conditions = ["Depression Status", "Anxiety Status", "Suicide Risk", "Functioning"]
        summary_data = []
        for cond in conditions:
            value_counts = df_data[cond].value_counts(dropna=False)
            total = value_counts.sum()
            for value, count in value_counts.items():
                percentage = (count / total) * 100
                summary_data.append({
                    "Condition": cond,
                    "Category": value,
                    "Count (Percentage)": f"{count} ({percentage:.1f}%)"
                })

        summary_df = pd.DataFrame(summary_data)
        prev = None
        for i in range(len(summary_df)):
            current = summary_df.at[i, "Condition"]
            if current == prev:
                summary_df.at[i, "Condition"] = ""
            else:
                prev = current

        st.table(summary_df.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', 'blue'), ('font-weight', 'bold'), ('color', 'white')]}
        ]))

        st.markdown("##### Grouped Analysis by Condition")
        available_group_cols = ["Class", "Stream", "Term", "Screen_Type"]
        with st.sidebar.expander('GROUP ANALYSIS', expanded=True):
            group_cols = st.multiselect(
                "Select Grouping Columns",
                options=available_group_cols,
                default=available_group_cols
            )
            filters = {}
            for col in group_cols:
                unique_vals = sorted(df_data[col].dropna().unique().tolist())
                selected_vals = st.multiselect(f"Filter values for {col}", options=unique_vals, default=unique_vals)
                filters[col] = selected_vals
            selected_conditions = st.multiselect(
                "Select Conditions to Analyze",
                options=conditions, default=conditions)
        filtered_df = df_data.copy()
        for col, selected_vals in filters.items():
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]
        grouped_dfs = {}
        if group_cols and selected_conditions:
            for cond in selected_conditions:
                group_df = generate_frequency_table(filtered_df, group_cols, cond)
                if not group_df.empty:
                    safe_sheet_name = cond.replace(" ", "_")[:31]
                    grouped_dfs[safe_sheet_name] = group_df
                    st.markdown(f"##### {cond} by {', '.join(group_cols)}")
                    st.table(group_df.style.set_table_styles([
                        {'selector': 'thead th', 'props': [('background-color', '#2ca02c'), ('color', 'white')]}
                    ]))
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, index=False, sheet_name='Summary_Data')
            for sheet_name, df in grouped_dfs.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        if grouped_dfs:
            st.download_button(
                label="📥 Download All Data (Excel)",
                data=excel_buffer.getvalue(),
                file_name="summary_and_grouped_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("⚠️ No grouped data to include in the Excel file. Please check your filters or selection.")

    elif selected == "Visio":
        col1, co2 = st.columns([2, 3])
        with col1:
            graph_menu = option_menu(
                menu_title="",
                options=["Standard graph", 'Comorbidity graph'],
                icons=["bar-chart-line", "graph-up"],
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "8!important", "background-color": 'black', 'border': '0.01px dotted red'},
                    "icon": {"color": "red", "font-size": "12px"},
                    "nav-link": {"color": "#d7c4c1", "font-size": "12px", "font-weight": 'bold', "text-align": "left", "margin": "0px", "--hover-color": "red"},
                    "nav-link-selected": {"background-color": "green"},
                },
                key="graph_menu")
        graph_filtered_df = filter_graph_data(results_df)
        if graph_menu == 'Standard graph':
            with st.sidebar:
                group_by_column, condition_column = set_visualization_settings(graph_filtered_df)
            filter_and_display_graph(graph_filtered_df, group_by_column, condition_column)
    

        elif graph_menu == 'Comorbidity graph':
            display_critical_condition_summary(graph_filtered_df)

    elif selected == "Report":
        if st.checkbox("Generate PDF Report"):
            filtered_data = st.session_state.filtered_df if "filtered_df" in st.session_state else results_df
            conditions_to_include = st.multiselect(
                "Select Conditions to Include in Report",
                options=["Depression Status", "Anxiety Status", "Suicide Risk", "Functioning"],
                default=["Depression Status", "Anxiety Status"]
            )
            
            # Generate frequency tables for selected conditions
            frequency_tables = {}
            for condition in conditions_to_include:
                frequency_tables[condition] = generate_frequency_table(filtered_data, ["Class", "Stream"], condition)

            # Generate critical condition summary (e.g., severe conditions)
            critical_summary = None
            if "Depression Status" in filtered_data.columns or "Anxiety Status" in filtered_data.columns or "Suicide Risk" in filtered_data.columns:
                critical_summary = display_critical_condition_summary(filtered_data)
            
            # Generate graphs (standard and comorbidity)
            graph_images = {}
            graph_images["Condition Graph"] = filter_and_display_graph(filtered_data, "Class", conditions_to_include[0])

            # Create a PDF report using the selected data
            pdf_buffer = generate_pdf_report(filtered_data, frequency_tables, critical_summary, graph_images)
            
            # Provide a preview of the generated PDF (optional)
            display_pdf(pdf_buffer)
            
            # Option to download the generated PDF
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="mental_health_report.pdf",
                mime="application/pdf"
            )

if __name__ == '__main__':
    main()
