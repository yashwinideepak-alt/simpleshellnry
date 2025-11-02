import streamlit as st
import subprocess
import shlex
import os
import threading
from datetime import datetime

# ------------- Streamlit Page Setup -------------
st.set_page_config(page_title="MySimpleShell", page_icon="💻", layout="wide")

st.markdown("<h1 style='text-align:center; color:#4CAF50;'>💻 MySimpleShell - Interactive Shell Environment</h1>", unsafe_allow_html=True)
st.write("### Run shell commands with process execution, redirection, piping, and background operations.")


# ------------- Command Handling Logic -------------
def run_pipeline(cmds):
    """Handles piped commands"""
    processes = []
    prev_process = None

    for cmd in cmds:
        args = shlex.split(cmd)
        if prev_process is None:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(args, stdin=prev_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prev_process = process
        processes.append(process)

    output, error = processes[-1].communicate()
    return output.decode() if output else error.decode()


def handle_command(cmd, background=False):
    """Detects operation type and executes accordingly"""
    try:
        # Piping
        if "|" in cmd:
            cmds = [c.strip() for c in cmd.split("|")]
            output = run_pipeline(cmds)
            return f"[Piping]\n{output}"

        # Append Redirection >>
        elif ">>" in cmd:
            parts = cmd.split(">>")
            main_cmd, filename = parts[0].strip(), parts[1].strip()
            args = shlex.split(main_cmd)
            with open(filename, "a") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE)
            return f"[Output Redirection (Append)] Output appended to {filename}"

        # Output Redirection >
        elif ">" in cmd:
            parts = cmd.split(">")
            main_cmd, filename = parts[0].strip(), parts[1].strip()
            args = shlex.split(main_cmd)
            with open(filename, "w") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE)
            return f"[Output Redirection] Output written to {filename}"

        # Input Redirection <
        elif "<" in cmd:
            parts = cmd.split("<")
            main_cmd, filename = parts[0].strip(), parts[1].strip()
            args = shlex.split(main_cmd)
            with open(filename, "r") as f:
                result = subprocess.run(args, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"[Input Redirection]\n{result.stdout.decode()}"

        # Background Process
        elif background:
            def background_run():
                subprocess.Popen(shlex.split(cmd))
            threading.Thread(target=background_run).start()
            return f"[Process Creation (Background)] {cmd}"

        # Normal Execution
        else:
            result = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"[Process Execution]\n{result.stdout.decode() or result.stderr.decode()}"

    except Exception as e:
        return f"Error: {str(e)}"


# ------------- Shell Interface Section -------------
st.markdown("## ⚙️ Execute a Shell Command")

command = st.text_input("Enter command:", placeholder="e.g., dir | findstr py (for Windows)")
background = st.checkbox("Run in background (&)")
run_button = st.button("Run Command")

if run_button:
    if command.strip():
        output = handle_command(command.strip(), background)
        st.code(output or "(no output)", language="bash")
    else:
        st.warning("Please enter a command before running.")


# ------------- File Creation Section -------------
st.markdown("---")
st.markdown("## 🗂️ Create a New File and Save to Local Drive")

filename = st.text_input("Enter filename (e.g., C:/Users/YourName/Desktop/test.txt):", "C:/Users/Public/sample.txt")
content = st.text_area("Enter file content:", "This is a sample file created from MySimpleShell.")

if st.button("Create File"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        st.success(f"✅ File successfully saved to your system at: {filename}")

        # Add timestamp for reference
        st.info(f"Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        st.error(f"❌ Error saving file: {str(e)}")


# ------------- List Files (Optional for Local Path) -------------
st.markdown("---")
st.markdown("## 📁 View Files in a Folder")

path = st.text_input("Enter folder path (e.g., C:/Users/Public):", "C:/Users/Public")
if st.button("List Files"):
    try:
        files = os.listdir(path)
        st.write(files)
    except Exception as e:
        st.error(f"Error accessing folder: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>Developed with ❤️ using Python and Streamlit</p>", unsafe_allow_html=True)
