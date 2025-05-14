
import pandas as pd
import os
import appointments
import requested_tools
from datetime import datetime
import captured_responses 
import seaborn as sns
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import io
import base64

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import tempfile
import plotly.express as px
import tempfile
from reportlab.platypus import Image


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
        {'selector': 'thead th', 'props': [('background-color', 'lightblue'), ('color', 'black'), ('font-weight', 'bold')]}])


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


def filter_data(df, filter_mode):
    if filter_mode == "All Results":
        return df

    with st.sidebar.expander("🎯:green[FILTER OPTIONS]", expanded=True):
        filter_options = ["Class", "Stream", "Term", "Screen Type", "Condition"]
        selected_filters = st.multiselect("Choose filter levels", filter_options)

        if "Class" in selected_filters:
            class_filter = st.multiselect("Select Class", df["Class"].dropna().unique())
            if class_filter:
                df = df[df["Class"].isin(class_filter)]

        if "Stream" in selected_filters:
            stream_filter = st.multiselect("Select Stream", df["Stream"].dropna().unique())
            if stream_filter:
                df = df[df["Stream"].isin(stream_filter)]

        if "Term" in selected_filters:
            term_filter = st.multiselect("Select Term", df["Term"].dropna().unique())
            if term_filter:
                df = df[df["Term"].isin(term_filter)]

        if "Screen Type" in selected_filters:
            screen_type_filter = st.multiselect("Select Screen Type", df["Screen_Type"].dropna().unique())
            if screen_type_filter:
                df = df[df["Screen_Type"].isin(screen_type_filter)]

        if "Condition" in selected_filters:
            st.markdown("#### 🧠 Select Mental Health Conditions to Filter")

            # Detect available mental health columns
            condition_options = []
            if 'Depression Status' in df.columns:
                condition_options.append("Depression Status")
            if 'Anxiety Status' in df.columns:
                condition_options.append("Anxiety Status")
            if 'Suicide Risk' in df.columns:
                condition_options.append("Suicide Risk")
            if 'Functioning' in df.columns:
                condition_options.append("Functioning")
            selected_conditions = st.multiselect("Select Conditions", condition_options)
            if "Depression Status" in selected_conditions:
                values = df["Depression Status"].dropna().unique()
                selected_values = st.multiselect("→ Depression Status", values)
                if selected_values:
                    df = df[df["Depression Status"].isin(selected_values)]
                else:
                    df = df[df["Depression Status"].notnull()]

            if "Anxiety Status" in selected_conditions:
                values = df["Anxiety Status"].dropna().unique()
                selected_values = st.multiselect("→ Anxiety Status", values)
                if selected_values:
                    df = df[df["Anxiety Status"].isin(selected_values)]
                else:
                    df = df[df["Anxiety Status"].notnull()]

            if "Suicide Risk" in selected_conditions:
                values = df["Suicide Risk"].dropna().unique()
                selected_values = st.multiselect("→ Suicide Risk", values)
                if selected_values:
                    df = df[df["Suicide Risk"].isin(selected_values)]
                else:
                    df = df[df["Suicide Risk"].notnull()]

            if "Functioning" in selected_conditions:
                values = df["Functioning"].dropna().unique()
                selected_values = st.multiselect("→ Functioning Status", values)
                if selected_values:
                    df = df[df["Functioning"].isin(selected_values)]
                else:
                    df = df[df["Functioning"].notnull()]

    with st.sidebar.expander(f':blue[COLUMN DISPLAY]', expanded=True):
        filter_columns = st.checkbox("Filter Columns")
        available_columns = df.columns.tolist()
        if filter_columns:
            selected_columns = st.multiselect("Select Columns to Display", available_columns)
            if selected_columns:
                df = df[selected_columns]
            else:
                df = df[available_columns]
        else:
            df = df[available_columns]

    return df



#### GRAPHS/VISIO #######
def filter_graph_data(df):
    with st.sidebar.expander('Filters', expanded = True):
        selected_classes = st.multiselect("Select Class", sorted(df["Class"].dropna().unique()))
        if selected_classes:
            df = df[df["Class"].isin(selected_classes)]
        selected_streams = st.multiselect("Select Stream", sorted(df["Stream"].dropna().unique()))
        if selected_streams:
            df = df[df["Stream"].isin(selected_streams)]
        selected_terms = st.multiselect("Select Term", sorted(df["Term"].dropna().unique()))
        if selected_terms:
            df = df[df["Term"].isin(selected_terms)]
        selected_screen_types = st.multiselect("Select Screen Type", sorted(df["Screen_Type"].dropna().unique()))
        if selected_screen_types:
            df = df[df["Screen_Type"].isin(selected_screen_types)]
        if "Gender" in df.columns:
            selected_genders = st.multiselect("Select Gender", sorted(df["Gender"].dropna().unique()))
            if selected_genders:
                df = df[df["Gender"].isin(selected_genders)]
    return df

def set_visualization_settings(df):
    with st.sidebar.expander('GROUP BY', expanded = True):
        group_by_columns = st.multiselect(
            "Group By (optional, you can select multiple)", 
            options=["Class", "Stream", "Gender", "Screen_Type"],
            default=[] )
        available_conditions = [col for col in df.columns if col in ["Depression Status", "Anxiety Status", "Suicide Risk", "Functioning"]]
        selected_conditions = st.multiselect(
            "Select Conditions to Visualize",
            options=available_conditions,
            default=available_conditions)
    return group_by_columns, selected_conditions



def filter_and_display_graph(df, group_by_columns, selected_conditions):
    if df.empty:
        st.warning("No data available for visualization based on the current filters.")
        return
    chart_type = st.radio("Select Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True)
    color_maps = {
        "Depression Status": {
            "Severe depression": "red",
            "Moderately severe depression": "orange",
            "Moderate depression": "yellow",
            "Mild depression": "blue",
            "Minimal depression": "green"
        },
        "Anxiety Status": {
            "Severe anxiety": "red",
            "Moderate anxiety": "orange",
            "Mild anxiety": "yellow",
            "Minimal anxiety": "green"
        },
        "Suicide Risk": {
            "High": "red",
            "Moderate": "yellow",
            "Low": "green"
        },
        "Functioning": {
            "Extremely difficult": "red",
            "Very difficult": "orange",
            "Somewhat difficult": "yellow",
            "Not difficult at all": "green"
        }
    }

    for condition_column in selected_conditions:
        color_map = color_maps.get(condition_column, {})
        group_cols = group_by_columns + [condition_column] if group_by_columns else [condition_column]
        plot_data = df.groupby(group_cols).size().reset_index(name="Count")

        if group_by_columns:
            total_counts = plot_data.groupby(group_by_columns)["Count"].transform("sum")
        else:
            total_count = plot_data["Count"].sum()
            total_counts = pd.Series([total_count] * len(plot_data))
        
        plot_data["Percentage"] = (plot_data["Count"] / total_counts * 100).round(1)

        if chart_type == "Bar Chart":
            plot_data["Group"] = plot_data[group_by_columns].astype(str).agg(" - ".join, axis=1) if group_by_columns else "Overall"
            fig = px.bar(
                plot_data,
                x="Group",
                y="Count",
                color=condition_column,
                color_discrete_map=color_map,
                text=plot_data["Count"].astype(str) + " (" + plot_data["Percentage"].astype(str) + "%)",
                barmode="stack"
            )
            fig.update_layout(
                title=f"{condition_column} by {' + '.join(group_by_columns) if group_by_columns else 'Overall'}",
                xaxis_title="Group",
                yaxis_title="Count",
                legend_title=condition_column,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie Chart":
            if group_by_columns:
                for values, sub_data in plot_data.groupby(group_by_columns):
                    label = " - ".join(str(v) for v in values) if isinstance(values, tuple) else str(values)
                    fig = px.pie(
                        sub_data,
                        names=condition_column,
                        values="Count",
                        title=f"{condition_column} - {label}",
                        color=condition_column,
                        color_discrete_map=color_map,
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.pie(
                    plot_data,
                    names=condition_column,
                    values="Count",
                    title=f"{condition_column} - Overall",
                    color=condition_column,
                    color_discrete_map=color_map,
                )
                st.plotly_chart(fig, use_container_width=True)


### GRAPH FOR COMORBIDTIES #######
def display_critical_condition_summary(df):
    conditions = st.sidebar.multiselect("Comorbities", ["Depression Status", "Anxiety Status", "Suicide Risk"])
    if not conditions:
        st.warning("Please select at least one critical condition.")
        return
    condition_filters = {}
    for condition in conditions:
        condition_filters[condition] = st.sidebar.selectbox(f"Select Severity for {condition}",
                                           sorted(df[condition].dropna().unique()))
    filter_query = (df[conditions[0]] == condition_filters[conditions[0]])
    for condition in conditions[1:]:
        filter_query &= (df[condition] == condition_filters[condition])
    critical_df = df[filter_query]

    if critical_df.empty:
        st.warning("No students meet the selected critical condition combination.")
        return
    valid_classes = sorted(critical_df['Class'].dropna().unique())
    valid_streams = sorted(critical_df['Stream'].dropna().unique())
    valid_screens = sorted(critical_df['Screen_Type'].dropna().unique())
    with st.sidebar.expander('FILTERS', expanded=True):
        selected_class = st.multiselect("Select Class", valid_classes, default=valid_classes)
        selected_stream = st.multiselect("Select Stream", valid_streams, default=valid_streams)
        selected_screen_type = st.multiselect("Select Screen Type", valid_screens, default=valid_screens)
    critical_df = critical_df[
        (critical_df['Class'].isin(selected_class)) &
        (critical_df['Stream'].isin(selected_stream)) &
        (critical_df['Screen_Type'].isin(selected_screen_type))]
    if critical_df.empty:
        st.warning("No students meet the selected criteria.")
        return
    critical_df['Group'] = critical_df['Class'] + "-" + critical_df['Stream'] + "-" + critical_df['Screen_Type']
    grouped = critical_df.groupby('Group').size().reset_index(name="Count")
    total = grouped["Count"].sum()
    grouped["Percentage"] = (grouped["Count"] / total * 100).round(1)
    grouped["Label"] = grouped["Count"].astype(str) + " (" + grouped["Percentage"].astype(str) + "%)"
    fig = px.bar(
        grouped,
        x="Group",
        y="Count",
        text="Label",
        title=" + ".join(condition_filters.values()),
        color="Group",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=False)



#### FREQENCY TABLES
def generate_frequency_table(df, group_cols, condition_col):
    grouped = df.groupby(group_cols + [condition_col]).size().reset_index(name='Count')
    total_per_group = grouped.groupby(group_cols)['Count'].transform('sum')
    grouped['Percentage'] = (grouped['Count'] / total_per_group * 100)
    grouped['Count (Percentage)'] = grouped.apply(
        lambda row: f"{row['Count']} ({row['Percentage']:.1f}%)", axis=1
    )

    grouped = grouped.sort_values(group_cols + [condition_col]).reset_index(drop=True)
    for col in group_cols:
        prev_val = None
        for i in range(len(grouped)):
            if grouped.at[i, col] == prev_val:
                grouped.at[i, col] = ""
            else:
                prev_val = grouped.at[i, col]

    return grouped[group_cols + [condition_col, 'Count (Percentage)']]




##### PDF REPORTS #######
def draw_header(canvas, doc):
    width, height = letter
    header_height = 750
    left_x = 30
    center_x = 150
    right_x = 450

    logo_left_path = "nag.png"
    logo_right_path = "my_logo.png"
    if os.path.exists(logo_left_path):
        canvas.drawImage(logo_left_path, left_x, header_height - 20, width=60, height=60)
    if os.path.exists(logo_right_path):
        canvas.drawImage(logo_right_path, right_x, header_height, width=100, height=30)

    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(center_x, 770, "LOGOS HEALTH & TECHCONSULTANTS LTD.")
    canvas.setFont("Helvetica", 12)
    canvas.drawString(center_x, header_height, "SOROTI UNIVERSITY")
    canvas.drawString(center_x, header_height - 15, "Kampala, Uganda")
    canvas.drawString(center_x, header_height - 30, "+256 781238761")
    canvas.drawString(center_x, header_height - 45, "kabpol14@gmail.com")

    canvas.setStrokeColorRGB(0, 0, 0)
    canvas.setLineWidth(1)
    canvas.line(30, header_height - 60, 580, header_height - 60)

def no_header(canvas, doc):
    pass

def display_pdf(pdf_buffer):
    base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
    pdf_display_html = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="500"></iframe>'
    st.markdown(pdf_display_html, unsafe_allow_html=True)

def generate_plotly_charts_and_save(df, group_by_columns, selected_conditions, chart_type="Bar Chart"):
    chart_images = []
    color_maps = {
        "Depression Status": {
            "Severe depression": "red",
            "Moderately severe depression": "orange",
            "Moderate depression": "yellow",
            "Mild depression": "blue",
            "Minimal depression": "green"
        },
        "Anxiety Status": {
            "Severe anxiety": "red",
            "Moderate anxiety": "orange",
            "Mild anxiety": "yellow",
            "Minimal anxiety": "green"
        },
        "Suicide Risk": {
            "High": "red",
            "Moderate": "yellow",
            "Low": "green"
        },
        "Functioning": {
            "Extremely difficult": "red",
            "Very difficult": "orange",
            "Somewhat difficult": "yellow",
            "Not difficult at all": "green"
        }
    }

    for condition in selected_conditions:
        color_map = color_maps.get(condition, {})
        if chart_type == "Pie Chart":
            plot_data = df[condition].value_counts().reset_index()
            plot_data.columns = [condition, "Count"]

            fig = px.pie(
                plot_data,
                names=condition,
                values="Count",
                color=condition,
                color_discrete_map=color_map,
                title=f"{condition} Distribution"
            )
            fig.update_traces(textinfo='label+percent')
            fig.update_layout(
                paper_bgcolor='lightblue',
                plot_bgcolor='lightgrey',
            )

        else: 
            group_cols = group_by_columns + [condition] if group_by_columns else [condition]
            plot_data = df.groupby(group_cols).size().reset_index(name="Count")

            if group_by_columns:
                total_counts = plot_data.groupby(group_by_columns)["Count"].transform("sum")
            else:
                total_count = plot_data["Count"].sum()
                total_counts = pd.Series([total_count] * len(plot_data))

            plot_data["Percentage"] = (plot_data["Count"] / total_counts * 100).round(1)
            plot_data["Group"] = plot_data[group_by_columns].astype(str).agg(" - ".join, axis=1) if group_by_columns else "Overall"

            fig = px.bar(
                plot_data,
                x="Group",
                y="Count",
                color=condition,
                color_discrete_map=color_map,
                text=plot_data["Count"].astype(str) + " (" + plot_data["Percentage"].astype(str) + "%)",
                barmode="stack",
                title=f"{condition} by {' + '.join(group_by_columns) if group_by_columns else 'Overall'}"
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                paper_bgcolor='lightblue',
                plot_bgcolor='lightgrey',
                xaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False),
                yaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False)
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.write_image(tmpfile.name, width=800, height=500)
            chart_images.append(tmpfile.name)

    return chart_images



def generate_pdf_report(df, include_table, include_summary, include_chart, chart_type):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Spacer(1, 40))
    story.append(Paragraph("Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 8))
    
    
    if include_table:
        story.append(Paragraph("Filtered Student Data", styles["Heading3"]))
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1, colWidths=[doc.width / len(df.columns)] * len(df.columns))
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    if include_summary:
        story.append(Paragraph("Summary Statistics", styles["Heading3"]))
        conditions = ["Depression Status", "Anxiety Status", "Suicide Risk", "Functioning"]
        summary_data = []
        for cond in conditions:
            value_counts = df[cond].value_counts(dropna=False)
            total = value_counts.sum()
            for value, count in value_counts.items():
                percentage = (count / total) * 100
                summary_data.append({
                    "Condition": cond,
                    "Category": value,
                    "Count (Percentage)": f"{count} ({percentage:.1f}%)"})
        summary_df = pd.DataFrame(summary_data)
        prev = None
        for i in range(len(summary_df)):
            current = summary_df.at[i, "Condition"]
            if current == prev:
                summary_df.at[i, "Condition"] = ""
            else:
                prev = current
        summary_table_data = [summary_df.columns.tolist()] + summary_df.astype(str).values.tolist()
        summary_table = Table(summary_table_data, repeatRows=1, colWidths=[doc.width / len(summary_df.columns)] * len(summary_df.columns))
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))
        story.append(Paragraph("Grouped Analysis by Condition", styles["Heading3"]))
        available_group_cols = ["Class", "Stream", "Term", "Screen_Type"]
        group_cols = ["Class", "Stream"]  
        grouped_dfs = {}
        for cond in conditions:
            group_df = generate_frequency_table(df, group_cols, cond)
            if not group_df.empty:
                safe_sheet_name = cond.replace(" ", "_")[:31]
                grouped_dfs[safe_sheet_name] = group_df
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"{cond} Grouped by {', '.join(group_cols)}", styles["Heading3"]))
                grouped_table_data = [group_df.columns.tolist()] + group_df.astype(str).values.tolist()
                grouped_table = Table(grouped_table_data, repeatRows=1, colWidths=[doc.width / len(group_df.columns)] * len(group_df.columns))
                grouped_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black)
                ]))
                story.append(grouped_table)
                story.append(Spacer(1, 12))

    if include_chart:
        story.append(Paragraph("Visual Charts", styles["Heading3"]))
        selected_conditions = ["Depression Status", "Anxiety Status", "Suicide Risk", "Functioning"]
        if chart_type == 'Pie Chart':
            pie_charts = generate_plotly_charts_and_save(df, group_by_columns=[], selected_conditions=selected_conditions, chart_type="Pie Chart")
            for pie in pie_charts:
                story.append(Image(pie, width=500, height=300))
                story.append(Spacer(1, 12))

        else:
            bar_charts = generate_plotly_charts_and_save(df, group_by_columns=["Class", "Stream"], selected_conditions=selected_conditions, chart_type="Bar Chart")
            for bar in bar_charts:
                story.append(Image(bar, width=500, height=300))
                story.append(Spacer(1, 12))
    doc.build(story, onFirstPage=draw_header, onLaterPages=no_header)
    buffer.seek(0)
    return buffer



#### REPORT ######
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
            "nav-link-selected": {"background-color": "green"},},
        key="selected")
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
                key="analysis_menu")
        filtered_df = filter_data(results_df, filter_menu)
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
            mime='text/csv')

    elif selected == "Summary Data":
        df_data = results_df
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
                    "Count (Percentage)": f"{count} ({percentage:.1f}%)"})

        summary_df = pd.DataFrame(summary_data)
        prev = None
        for i in range(len(summary_df)):
            current = summary_df.at[i, "Condition"]
            if current == prev:
                summary_df.at[i, "Condition"] = ""
            else:
                prev = current
        st.table(summary_df.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', 'blue'), ('font-weight', 'bold'), ('color', 'white')]}]))
        st.markdown("##### Grouped Analysis by Condition")
        available_group_cols = ["Class", "Stream", "Term", "Screen_Type"]
        with st.sidebar.expander('GROUP ANALYSIS', expanded=True):
            group_cols = st.multiselect(
                "Select Grouping Columns",
                options=available_group_cols,
                default=available_group_cols)
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
                        {'selector': 'thead th', 'props': [('background-color', '#2ca02c'), ('color', 'white')]}]))
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
        col1, co2  = st.columns([2,3])
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
        if  graph_menu == 'Standard graph':
            with st.sidebar:
                group_by_column, condition_column = set_visualization_settings(graph_filtered_df)
            filter_and_display_graph(graph_filtered_df, group_by_column, condition_column)
        elif graph_menu == 'Comorbidity graph':
            display_critical_condition_summary(graph_filtered_df)


    if selected == "Report":     
        with st.sidebar.expander('GENERATE PDF REPORT', expanded=True):
            include_table = st.toggle("Include Table", value=True)
            include_summary = st.toggle("Include Summary", value=True)
            include_chart = st.toggle("Include Chart", value=True)
            if include_chart:
                chart_type = st.radio("Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True)
            else:
                chart_type = "Bar Chart"
        if st.sidebar.checkbox("Generate Report"):
            pdf_buffer = generate_pdf_report(results_df, include_table, include_summary, include_chart, chart_type)
            display_pdf(pdf_buffer)
            st.sidebar.download_button("Download PDF", data=pdf_buffer.getvalue(), file_name="impact_report.pdf")
            
if __name__ == '__main__':
    main()





