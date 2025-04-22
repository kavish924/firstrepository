import streamlit as st
import sqlite3
import pandas as pd
import os

# ---------------------------
# DATABASE FUNCTIONS
# ---------------------------
def create_connection():
    conn = sqlite3.connect('scan_reports.db')
    return conn

def create_table():
    conn = create_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scan_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            scan_type TEXT,
            scan_summary TEXT,
            scan_date TEXT,
            radiologist_name TEXT,
            file_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_scan_report(patient_name, age, gender, scan_type, scan_summary, scan_date, radiologist_name, file_name):
    conn = create_connection()
    conn.execute('''
        INSERT INTO scan_reports (
            patient_name, age, gender, scan_type, scan_summary, scan_date, radiologist_name, file_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (patient_name, age, gender, scan_type, scan_summary, scan_date, radiologist_name, file_name))
    conn.commit()
    conn.close()

def get_all_scan_reports():
    conn = create_connection()
    df = pd.read_sql_query('SELECT * FROM scan_reports', conn)
    conn.close()
    return df

def search_scan_reports(patient_name):
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM scan_reports WHERE patient_name LIKE ?", conn, params=('%' + patient_name + '%',))
    conn.close()
    return df

# ---------------------------
# STREAMLIT UI
# ---------------------------
def main():
    st.set_page_config(page_title="Scan Report Management", layout="wide")
    st.title("🩻 Hospital Scan Report Portal")

    menu = ["Register Scan Report", "View All Reports", "Search by Patient"]
    choice = st.sidebar.selectbox("Menu", menu)

    create_table()

    upload_dir = "uploaded_scans"
    os.makedirs(upload_dir, exist_ok=True)

    if choice == "Register Scan Report":
        st.subheader("Register New Scan Report")

        with st.form("scan_form"):
            patient_name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            scan_type = st.selectbox("Scan Type", ["X-ray", "MRI", "CT Scan", "Ultrasound", "Other"])
            scan_summary = st.text_area("Scan Result Summary")
            scan_date = st.date_input("Scan Date")
            radiologist_name = st.text_input("Radiologist Name")
            scan_file = st.file_uploader("Upload Scan File (optional)", type=["pdf", "jpg", "png", "jpeg"])

            submitted = st.form_submit_button("Submit Scan Report")
            file_name = ""

            if submitted:
                if scan_file is not None:
                    file_name = os.path.join(upload_dir, scan_file.name)
                    with open(file_name, "wb") as f:
                        f.write(scan_file.getbuffer())

                add_scan_report(
                    patient_name, age, gender, scan_type, scan_summary,
                    str(scan_date), radiologist_name, file_name
                )
                st.success(f"Scan report for '{patient_name}' added successfully!")

    elif choice == "View All Reports":
        st.subheader("All Scan Reports")
        df = get_all_scan_reports()
        st.dataframe(df.drop(columns=["file_name"]), use_container_width=True)

    elif choice == "Search by Patient":
        st.subheader("Search Scan Reports by Patient Name")
        search_name = st.text_input("Enter patient name")
        if search_name:
            df = search_scan_reports(search_name)
            if not df.empty:
                for _, row in df.iterrows():
                    st.write(f"### 🧍 Patient: {row['patient_name']} ({row['gender']}, {row['age']} y/o)")
                    st.write(f"**Scan Type:** {row['scan_type']}")
                    st.write(f"**Date:** {row['scan_date']}")
                    st.write(f"**Radiologist:** {row['radiologist_name']}")
                    st.write("**Summary:**")
                    st.info(row['scan_summary'])

                    if row['file_name']:
                        st.markdown(f"[🖼️ View Scan File]({row['file_name']})", unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.warning("No records found.")

if __name__ == '__main__':
    main()
