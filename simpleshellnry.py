import streamlit as st
import subprocess
import os
import time
from io import BytesIO

# ----------------------- Page Setup -----------------------
st.set_page_config(page_title="Simple Shell", page_icon="💻", layout="centered")
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #f5f5f5;
    }
    .stTextArea > div > textarea {
        background-color: #1a1a1a;
        color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💻 Interactive Simple Shell Simulator")
st.markdown("A stylish and interactive mini shell that supports execution, redirection, piping, background tasks, and file creation 📁")

# Create folder for virtual files (app environment)
BASE_DIR = "Documents"
os.makedirs(BASE_DIR, exist_ok=True)

# ----------------------------------------------------------
# 🧠 SHELL COMMAND EXECUTION
# ----------------------------------------------------------
st.header("⚙️ Run Shell Commands")
command = st.text_input("Enter a shell command (supports |, >, <, &, etc.):")

if st.button("▶️ Execute Command"):
    if command:
        st.markdown("### 🧩 Process Details")

        # Identify process type
        if "|" in command:
            st.info("🔹 **Process Type:** Piping — connects output of one command to another.")
        elif ">" in command or "<" in command:
            st.info("🔹 **Process Type:** Redirection — redirects input/output between files.")
        elif "&" in command:
            st.info("🔹 **Process Type:** Background — runs asynchronously.")
        else:
            st.info("🔹 **Process Type:** Execution — standard process run.")

        # Measure execution time
        start_time = time.time()
        try:
            if "&" in command:
                process = subprocess.Popen(command.replace("&", ""), shell=True)
                st.success(f"✅ Background process started (PID: {process.pid})")
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                end_time = time.time()
                elapsed = end_time - start_time

                # Output results
                st.code(result.stdout if result.stdout else "No output", language="bash")
                if result.stderr:
                    st.error(result.stderr)

                # Show timing info
                st.markdown(f"⏱ **Execution Time:** {elapsed:.4f} seconds")
        except Exception as e:
            st.error(f"Error occurred: {e}")
    else:
        st.warning("Please enter a command first!")

# ----------------------------------------------------------
# 🧾 PROCESS COMPARISON (Performance Check)
# ----------------------------------------------------------
st.header("🔍 Compare Two Processes")
col1, col2 = st.columns(2)
cmd1 = col1.text_input("First Command:")
cmd2 = col2.text_input("Second Command:")

if st.button("⚖️ Compare Performance"):
    if cmd1 and cmd2:
        results = []
        for i, cmd in enumerate([cmd1, cmd2], start=1):
            start = time.time()
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            end = time.time()
            results.append({
                "cmd": cmd,
                "time": end - start,
                "output": result.stdout.strip() or "(no output)",
                "error": result.stderr.strip()
            })

        # Show comparison
        for idx, r in enumerate(results, start=1):
            st.markdown(f"### 🧠 Command {idx}: `{r['cmd']}`")
            st.write(f"⏱ **Time Taken:** {r['time']:.4f} seconds")
            st.text_area("📤 Output", r['output'], height=100)
            if r['error']:
                st.error(r['error'])

        if results[0]["time"] < results[1]["time"]:
            st.success("✅ Command 1 executed faster!")
        elif results[0]["time"] > results[1]["time"]:
            st.success("✅ Command 2 executed faster!")
        else:
            st.info("Both commands executed in roughly the same time.")
    else:
        st.warning("Enter both commands to compare.")

# ----------------------------------------------------------
# 📝 FILE CREATION WITH DOWNLOAD
# ----------------------------------------------------------
st.header("📝 Create and Download a File")
filename = st.text_input("Enter file name (e.g., report.txt):")
content = st.text_area("Enter content for the file:")

if st.button("💾 Create & Download File"):
    if filename.strip():
        file_path = os.path.join(BASE_DIR, filename)
        with open(file_path, "w") as f:
            f.write(content)

        # Convert to bytes for download
        file_bytes = BytesIO(content.encode("utf-8"))
        st.success(f"✅ File '{filename}' created successfully!")

        st.download_button(
            label="📥 Download File",
            data=file_bytes,
            file_name=filename,
            mime="text/plain",
        )
    else:
        st.warning("Please enter a valid file name!")

# ----------------------------------------------------------
# 📂 FILE LIST SECTION
# ----------------------------------------------------------
st.header("📂 Files Created in Environment")
files = os.listdir(BASE_DIR)
if files:
    for file in files:
        file_path = os.path.join(BASE_DIR, file)
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()
        with st.expander(f"📘 {file}"):
            st.text(content)
else:
    st.info("No files have been created yet.")
