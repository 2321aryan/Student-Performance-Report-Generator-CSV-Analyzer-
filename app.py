from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import pandas as pd
import io, uuid

app = Flask(__name__)
app.secret_key = "dev-secret"

# Temporary in-memory storage
STORE = {}


# --------------------------------------------------
# Helper: safely read CSV
# --------------------------------------------------
def try_read_csv_bytes(raw: bytes):
    for enc in ("utf-8", "latin1", "cp1252"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except Exception:
            continue
    raise ValueError("Unsupported CSV encoding")


# --------------------------------------------------
# Clean Data (PROTECT student_name)
# --------------------------------------------------
def clean_dataframe(df, opts):
    df = df.copy()

    # Normalize column names
    df.columns = [str(c).strip().replace("\n", " ").replace("\r", " ") for c in df.columns]

    # Detect student name column early
    name_col = next(
        (c for c in df.columns if c.lower() in ["student_name", "name", "student"]),
        None
    )

    if opts.get("drop_empty_rows"):
        df = df.dropna(how="all")

    if opts.get("drop_empty_cols"):
        df = df.dropna(axis=1, how="all")

    if opts.get("drop_duplicates"):
        df = df.drop_duplicates()

    if opts.get("strip_whitespace"):
        for c in df.select_dtypes(include="object").columns:
            df[c] = df[c].astype(str).str.strip()

    # Convert numbers EXCEPT student name
    if opts.get("convert_numbers"):
        for c in df.columns:
            if c == name_col:
                continue
            if not pd.api.types.is_numeric_dtype(df[c]):
                temp = df[c].astype(str).str.replace(",", "").str.replace("%", "")
                conv = pd.to_numeric(temp, errors="coerce")
                if conv.notna().mean() > 0.5:
                    df[c] = conv

    # Fill missing values
    if opts.get("fill_missing"):
        for c in df.columns:
            if c == name_col:
                df[c] = df[c].fillna("")
            else:
                df[c] = df[c].fillna(0 if pd.api.types.is_numeric_dtype(df[c]) else "")

    return df


# --------------------------------------------------
# Home
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", merged=None, cleaned=None, top10=None, key=None)


# --------------------------------------------------
# Merge CSV files
# --------------------------------------------------
@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("csv_files")
    if not files:
        flash("No files selected.")
        return redirect(url_for("index"))

    dfs = [try_read_csv_bytes(f.read()) for f in files]
    merged = pd.concat(dfs, ignore_index=True, sort=False)

    key = str(uuid.uuid4())

    buf = io.BytesIO()
    merged.to_csv(buf, index=False)
    buf.seek(0)

    STORE[key] = {
        "merged_df": merged,
        "merged_csv": buf.getvalue(),
        "cleaned_df": None,
        "cleaned_xlsx": None,
        "top10_xlsx": None
    }

    return render_template(
        "index.html",
        merged=merged.head(10).to_html(index=False),
        cleaned=None,
        top10=None,
        key=key
    )


# --------------------------------------------------
# Clean merged data
# --------------------------------------------------
@app.route("/clean", methods=["POST"])
def clean():
    key = request.form.get("key")

    if not key or key not in STORE:
        flash("Session expired. Please upload again.")
        return redirect(url_for("index"))

    df = STORE[key]["merged_df"]

    opts = {
        "drop_empty_rows": "drop_empty_rows" in request.form,
        "drop_empty_cols": "drop_empty_cols" in request.form,
        "drop_duplicates": "drop_duplicates" in request.form,
        "strip_whitespace": "strip_whitespace" in request.form,
        "convert_numbers": "convert_numbers" in request.form,
        "fill_missing": "fill_missing" in request.form,
    }

    cleaned = clean_dataframe(df, opts)
    STORE[key]["cleaned_df"] = cleaned

    buf = io.BytesIO()
    cleaned.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    STORE[key]["cleaned_xlsx"] = buf.getvalue()

    return render_template(
        "index.html",
        merged=df.head(10).to_html(index=False),
        cleaned=cleaned.head(10).to_html(index=False),
        top10=None,
        key=key
    )


# --------------------------------------------------
# TOP 10 STUDENTS (FIXED & CORRECT)
# --------------------------------------------------
@app.route("/top10", methods=["POST"])
def top10():
    key = request.form.get("key")

    if not key or key not in STORE:
        flash("Session expired.")
        return redirect(url_for("index"))

    df = STORE[key]["cleaned_df"]
    if df is None:
        flash("Please clean data first.")
        return redirect(url_for("index"))

    df = df.copy()

    # Detect student name column (STRICT)
    name_col = next(
        (c for c in df.columns if c.lower() in ["student_name", "name", "student"]),
        None
    )

    if name_col is None:
        flash("Student name column not found.")
        return redirect(url_for("index"))

    # Use ONLY subject marks columns
    marks_cols = [
        c for c in df.columns
        if c.endswith("_marks") and pd.api.types.is_numeric_dtype(df[c])
    ]

    if not marks_cols:
        flash("No subject marks columns found.")
        return redirect(url_for("index"))

    # Calculate totals & percentage
    df["Total_Marks"] = df[marks_cols].sum(axis=1)

    max_total = 100 * len(marks_cols)  # each subject out of 100
    df["Percentage"] = (df["Total_Marks"] / max_total) * 100
    df["Percentage"] = df["Percentage"].round(2)

    # Rank students
    top10_df = df.sort_values("Percentage", ascending=False).head(10).copy()
    top10_df.insert(0, "Rank", range(1, len(top10_df) + 1))

    result_cols = ["Rank", name_col] + marks_cols + ["Total_Marks", "Percentage"]
    result = top10_df[result_cols]

    # Save Top-10 Excel
    buf = io.BytesIO()
    result.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    STORE[key]["top10_xlsx"] = buf.getvalue()

    return render_template(
        "index.html",
        merged=STORE[key]["merged_df"].head(10).to_html(index=False),
        cleaned=STORE[key]["cleaned_df"].head(10).to_html(index=False),
        top10=result.to_html(index=False),
        key=key
    )


# --------------------------------------------------
# Download files
# --------------------------------------------------
@app.route("/download/<key>/<filetype>")
def download(key, filetype):
    if not key or key not in STORE:
        flash("Session expired.")
        return redirect(url_for("index"))

    if filetype == "merged":
        return send_file(io.BytesIO(STORE[key]["merged_csv"]),
                         download_name="merged.csv", as_attachment=True)

    if filetype == "cleaned":
        return send_file(io.BytesIO(STORE[key]["cleaned_xlsx"]),
                         download_name="cleaned.xlsx", as_attachment=True)

    if filetype == "top10":
        return send_file(io.BytesIO(STORE[key]["top10_xlsx"]),
                         download_name="top10_students.xlsx", as_attachment=True)

    flash("Invalid download request.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
