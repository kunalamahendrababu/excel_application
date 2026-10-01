import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date
from uuid import uuid4

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="🎓",
    layout="wide"
)

DATA_FILE = Path("attendance.json")

STATUS_OPTIONS = [
    "Present",
    "Absent"
]

SEMESTERS = [
    "1-1",
    "1-2",
    "2-1",
    "2-2",
    "3-1",
    "3-2",
    "4-1",
    "4-2"
]


# ============================================================
# BACKEND - JSON STORAGE
# ============================================================

def create_json_file():

    if not DATA_FILE.exists():

        DATA_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


def load_records():

    create_json_file()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):

        return []


def save_records(records):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# BACKEND - CREATE
# ============================================================

def create_attendance(
    student_name,
    roll_number,
    department,
    semester,
    attendance_date,
    status
):

    student_name = student_name.strip()
    roll_number = roll_number.strip()
    department = department.strip()

    if not student_name:

        return False, "Student name is required."

    if not roll_number:

        return False, "Roll number is required."

    if not department:

        return False, "Department is required."

    records = load_records()

    # Prevent duplicate attendance
    for record in records:

        if (
            record["roll_number"].lower()
            == roll_number.lower()
            and record["date"]
            == attendance_date.isoformat()
        ):

            return (
                False,
                "Attendance already exists for this student on this date."
            )

    new_record = {

        "id": str(uuid4()),

        "student_name": student_name,

        "roll_number": roll_number,

        "department": department,

        "semester": semester,

        "date": attendance_date.isoformat(),

        "status": status
    }

    records.append(new_record)

    save_records(records)

    return True, "Attendance marked successfully."


# ============================================================
# BACKEND - UPDATE
# ============================================================

def update_attendance(
    record_id,
    student_name,
    roll_number,
    department,
    semester,
    attendance_date,
    status
):

    student_name = student_name.strip()
    roll_number = roll_number.strip()
    department = department.strip()

    if not student_name:

        return False, "Student name is required."

    if not roll_number:

        return False, "Roll number is required."

    records = load_records()

    for record in records:

        if record["id"] == record_id:

            record["student_name"] = student_name
            record["roll_number"] = roll_number
            record["department"] = department
            record["semester"] = semester
            record["date"] = attendance_date.isoformat()
            record["status"] = status

            save_records(records)

            return True, "Attendance updated successfully."

    return False, "Attendance record not found."


# ============================================================
# BACKEND - DELETE
# ============================================================

def delete_attendance(record_id):

    records = load_records()

    updated_records = [
        record
        for record in records
        if record["id"] != record_id
    ]

    if len(records) == len(updated_records):

        return False

    save_records(updated_records)

    return True


# ============================================================
# BACKEND - FIND RECORD
# ============================================================

def get_record(record_id):

    records = load_records()

    for record in records:

        if record["id"] == record_id:

            return record

    return None


# ============================================================
# BACKEND - ATTENDANCE CALCULATION
# ============================================================

def calculate_percentage(student_records):

    total_classes = len(student_records)

    if total_classes == 0:

        return 0.0

    present_classes = sum(
        1
        for record in student_records
        if record["status"] == "Present"
    )

    percentage = (
        present_classes
        / total_classes
    ) * 100

    return round(
        percentage,
        2
    )


# ============================================================
# BACKEND - STUDENT SUMMARY
# ============================================================

def create_student_summary(records):

    students = {}

    for record in records:

        roll_number = record["roll_number"]

        if roll_number not in students:

            students[roll_number] = {

                "student_name":
                    record["student_name"],

                "roll_number":
                    roll_number,

                "department":
                    record["department"],

                "semester":
                    record["semester"],

                "total_classes":
                    0,

                "present":
                    0,

                "absent":
                    0
            }

        students[roll_number]["total_classes"] += 1

        if record["status"] == "Present":

            students[roll_number]["present"] += 1

        else:

            students[roll_number]["absent"] += 1

    result = []

    for student in students.values():

        total = student["total_classes"]

        present = student["present"]

        student["percentage"] = round(
            (present / total) * 100,
            2
        ) if total else 0

        result.append(student)

    return sorted(
        result,
        key=lambda x: x["roll_number"]
    )


# ============================================================
# SESSION STATE
# ============================================================

if "editing_id" not in st.session_state:

    st.session_state.editing_id = None


# ============================================================
# HEADER
# ============================================================

st.title("🎓 Student Attendance Tracker")

st.write(
    "Manage student attendance using structured JSON data."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📌 Navigation")

    page = st.radio(
        "Select Page",
        [
            "Dashboard",
            "Mark Attendance",
            "Attendance Records"
        ]
    )

    st.divider()

    st.info(
        "No traditional database is used. "
        "Attendance records are stored in attendance.json."
    )


# ============================================================
# LOAD DATA
# ============================================================

records = load_records()

student_summary = create_student_summary(records)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header("📊 Attendance Dashboard")

    total_students = len(student_summary)

    total_records = len(records)

    total_present = sum(
        1
        for record in records
        if record["status"] == "Present"
    )

    overall_percentage = (

        total_present
        / total_records
        * 100

        if total_records > 0
        else 0
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👨‍🎓 Students",
        total_students
    )

    col2.metric(
        "📋 Records",
        total_records
    )

    col3.metric(
        "✅ Present",
        total_present
    )

    col4.metric(
        "📊 Overall Attendance",
        f"{overall_percentage:.2f}%"
    )

    st.divider()

    if not student_summary:

        st.info(
            "No attendance data available."
        )

    else:

        summary_df = pd.DataFrame(
            student_summary
        )

        # ----------------------------------------------------
        # CHART
        # ----------------------------------------------------

        st.subheader(
            "📊 Student Attendance Percentage"
        )

        chart_data = (
            summary_df
            .set_index("student_name")
            [["percentage"]]
        )

        st.bar_chart(
            chart_data
        )

        # ----------------------------------------------------
        # SUMMARY TABLE
        # ----------------------------------------------------

        st.subheader(
            "📋 Student Summary"
        )

        display_df = summary_df[
            [
                "student_name",
                "roll_number",
                "department",
                "semester",
                "total_classes",
                "present",
                "absent",
                "percentage"
            ]
        ].copy()

        display_df.columns = [

            "Student",

            "Roll Number",

            "Department",

            "Semester",

            "Total Classes",

            "Present",

            "Absent",

            "Attendance %"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # LOW ATTENDANCE
        # ----------------------------------------------------

        st.subheader(
            "⚠️ Attendance Below 75%"
        )

        low_attendance = summary_df[
            summary_df["percentage"] < 75
        ]

        if low_attendance.empty:

            st.success(
                "No student is below 75%."
            )

        else:

            st.warning(
                "The following students have attendance below 75%."
            )

            st.dataframe(
                low_attendance[
                    [
                        "student_name",
                        "roll_number",
                        "percentage"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# MARK ATTENDANCE
# ============================================================

elif page == "Mark Attendance":

    st.header("📝 Mark Student Attendance")

    editing_record = None

    if st.session_state.editing_id:

        editing_record = get_record(
            st.session_state.editing_id
        )

    if editing_record:

        st.subheader(
            "✏️ Edit Attendance"
        )

    else:

        st.subheader(
            "➕ Add Attendance"
        )

    # --------------------------------------------------------
    # CUSTOM FORM
    # --------------------------------------------------------

    with st.form("attendance_form"):

        col1, col2 = st.columns(2)

        with col1:

            student_name = st.text_input(
                "Student Name",
                value=(
                    editing_record["student_name"]
                    if editing_record
                    else ""
                ),
                placeholder="Enter student name"
            )

            roll_number = st.text_input(
                "Roll Number",
                value=(
                    editing_record["roll_number"]
                    if editing_record
                    else ""
                ),
                placeholder="Example: 24JR1A05P6"
            )

            department = st.text_input(
                "Department",
                value=(
                    editing_record["department"]
                    if editing_record
                    else "CSE"
                )
            )

        with col2:

            semester = st.selectbox(
                "Semester",
                SEMESTERS,
                index=(
                    SEMESTERS.index(
                        editing_record["semester"]
                    )
                    if editing_record
                    and editing_record["semester"] in SEMESTERS
                    else 0
                )
            )

            attendance_date = st.date_input(
                "Attendance Date",
                value=(
                    date.fromisoformat(
                        editing_record["date"]
                    )
                    if editing_record
                    else date.today()
                )
            )

            status = st.radio(
                "Attendance Status",
                STATUS_OPTIONS,
                horizontal=True,
                index=(
                    STATUS_OPTIONS.index(
                        editing_record["status"]
                    )
                    if editing_record
                    else 0
                )
            )

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        if editing_record:

            submit_button = st.form_submit_button(
                "Update Attendance",
                use_container_width=True
            )

        else:

            submit_button = st.form_submit_button(
                "Save Attendance",
                use_container_width=True
            )

        if submit_button:

            if editing_record:

                success, message = update_attendance(

                    editing_record["id"],

                    student_name,

                    roll_number,

                    department,

                    semester,

                    attendance_date,

                    status
                )

            else:

                success, message = create_attendance(

                    student_name,

                    roll_number,

                    department,

                    semester,

                    attendance_date,

                    status
                )

            if success:

                st.success(message)

                st.session_state.editing_id = None

                st.rerun()

            else:

                st.error(message)

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if editing_record:

        if st.button(
            "Cancel Edit"
        ):

            st.session_state.editing_id = None

            st.rerun()


# ============================================================
# ATTENDANCE RECORDS
# ============================================================

elif page == "Attendance Records":

    st.header("📋 Attendance Records")

    records = load_records()

    if not records:

        st.info(
            "No attendance records available."
        )

    else:

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            search = st.text_input(
                "🔎 Search Student",
                placeholder="Name or roll number"
            )

        with col2:

            status_filter = st.selectbox(
                "Filter Status",
                [
                    "All",
                    "Present",
                    "Absent"
                ]
            )

        filtered_records = []

        for record in records:

            matches_search = (

                not search

                or search.lower()
                in record["student_name"].lower()

                or search.lower()
                in record["roll_number"].lower()
            )

            matches_status = (

                status_filter == "All"

                or record["status"]
                == status_filter
            )

            if matches_search and matches_status:

                filtered_records.append(record)

        # ----------------------------------------------------
        # DISPLAY RECORDS
        # ----------------------------------------------------

        for record in filtered_records:

            with st.container(border=True):

                col1, col2, col3, col4, col5 = st.columns(
                    [1.2, 1.4, 1.2, 2.5, 1.2]
                )

                col1.write(
                    record["date"]
                )

                col2.write(
                    record["roll_number"]
                )

                col3.write(
                    record["status"]
                )

                col4.write(
                    f"**{record['student_name']}**  \n"
                    f"{record['department']} • "
                    f"{record['semester']}"
                )

                if col5.button(
                    "✏️ Edit",
                    key=f"edit_{record['id']}"
                ):

                    st.session_state.editing_id = record["id"]

                    st.rerun()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{record['id']}"
                ):

                    delete_attendance(
                        record["id"]
                    )

                    st.success(
                        "Attendance record deleted."
                    )

                    st.rerun()

        st.caption(
            f"Showing {len(filtered_records)} "
            f"of {len(records)} records."
        )

        st.divider()

        # ----------------------------------------------------
        # ATTENDANCE CALCULATOR
        # ----------------------------------------------------

        st.subheader(
            "🧮 Attendance Percentage Calculator"
        )

        roll_numbers = sorted(
            set(
                record["roll_number"]
                for record in records
            )
        )

        selected_roll = st.selectbox(
            "Select Student",
            roll_numbers
        )

        selected_records = [

            record
            for record in records

            if record["roll_number"]
            == selected_roll
        ]

        percentage = calculate_percentage(
            selected_records
        )

        student_name = (
            selected_records[0]["student_name"]
        )

        total_classes = len(
            selected_records
        )

        present_classes = sum(

            1
            for record in selected_records

            if record["status"]
            == "Present"
        )

        absent_classes = (

            total_classes
            - present_classes
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Student",
            student_name
        )

        col2.metric(
            "Total Classes",
            total_classes
        )

        col3.metric(
            "Present",
            present_classes
        )

        col4.metric(
            "Attendance",
            f"{percentage:.2f}%"
        )

        if percentage < 75:

            st.warning(
                "⚠️ Attendance is below 75%."
            )

        else:

            st.success(
                "✅ Attendance is 75% or above."
            )
