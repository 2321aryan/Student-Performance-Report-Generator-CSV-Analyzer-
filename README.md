# 📊 Student Performance Report Generator (CSV Analyzer)

A smart **CSV-to-Report Data Analyzer** that processes multiple student result files, cleans the data, and generates meaningful academic reports such as **Top performers**, **subject-wise rankings**, and **pass/fail analysis**.

---

## 📌 Project Overview

This project is designed to help **teachers, institutions, and students** analyze academic performance efficiently.
It allows users to upload **multiple CSV files**, automatically cleans and merges the data, and produces **rank-based and subject-wise reports**.

The system transforms raw CSV files into **actionable insights** without manual calculations.

---

## ✨ Key Features

* 📂 Upload **multiple CSV files at once**
* 🧹 Automatic **data cleaning & preprocessing**
* 🔗 Merge multiple datasets into one report
* 🏆 **Top 10 students overall** (based on total/percentage)
* 📘 **Top 5 students per subject**
* ✅ **Pass vs Fail analysis**
* 📊 Structured report-ready output
* ⚡ Fast and user-friendly workflow

---

## 📈 Analysis Performed

### 🔹 Overall Performance

* Total marks calculation
* Percentage calculation
* Rank generation
* Top 10 students list

### 🔹 Subject-wise Performance

* Subject-wise ranking
* Top 5 students in **each subject**

### 🔹 Result Classification

* Pass / Fail determination
* Summary statistics

---

## 🛠️ Technologies Used

* **Python**
* **Pandas** – Data cleaning & processing
* **CSV Processing**
* *(Optional)* Streamlit / Matplotlib for visualization

---

## 📂 Project Structure (Example)

```text
student-report-generator/
│
├── app.py / main.py          # Core logic
├── utils/
│   ├── data_cleaning.py
│   └── analysis.py
├── sample_csv/
│   └── students.csv
├── output/
│   └── reports/
└── README.md
```

---

## 📄 CSV File Requirements

Each CSV file should contain:

* Student name column
* Subject-wise marks (numeric)

Example:

```csv
Name,Maths,Physics,Chemistry,English
Aryan,85,78,90,88
Rahul,72,65,70,75
```

The system automatically:

* Detects subject columns
* Handles missing or invalid values
* Merges multiple files safely

---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies

```bash
pip install pandas
```

### 2️⃣ Run the Program

```bash
python app.py
```

### 3️⃣ Upload / Select CSV Files

* Select one or multiple CSV files
* The system processes and generates reports automatically

---

## 🎯 Use Cases

* School & college result analysis
* Academic performance tracking
* Faculty reporting tools
* BCA / MCA / Data Science mini projects
* CSV data analytics practice

---

## ⚠️ Notes

* Marks are assumed to be numeric
* Pass/Fail threshold can be customized
* Designed for **educational and reporting purposes**
* Not intended for production without validation

---

## 📜 License

This project is open-source and intended for **educational and academic use**.
