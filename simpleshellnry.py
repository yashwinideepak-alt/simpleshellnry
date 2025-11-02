import streamlit as st
import subprocess
import shlex
import os
import threading
import base64
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="NeoShell: Interactive Command Hub",
    page_icon="💠",
    layout="centered"
)

# -------------------- CUSTOM STYLE --------------------
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #f0f4f8 0%, #e4ebf5 100%);
    color: #0a2342;
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1 {
    color: #003366 !important;
    text-align: center;
    font-weight: 700;
}

/* Section headers */
h3 {
    color: #005999;
    border-bottom: 2px solid #cce0ff;
    padding-bottom: 4px;
}

/* Input fields */
.stTextInput > div > div > input, textarea {
    background-color: #ffffff !important;
    border: 1.5px solid #99bbff !important;
    border-radius: 10px !important;
    color: #0a2342 !important;
}

/* Buttons */
.stButton > button {
    background-color: #0078d7 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600;
    padding: 0.6em 1.2em !important;
    transition: all 0.2s ease-in-out;
}

.stButton > button:hover {
    background-color: #005fa3 !important;
    transform: scale(1.02);
}

/* Code block */
code, pre {
    background-color: #f1f6fc !important;
    color: #001f3f !important;
    border-radius: 8px;
    padding: 0.7em;
    font-size: 0.9em;
}

/* Boxes and expanders */
.stExpander {
    border: 1px solid #cce0ff;
    border-radius: 10px;
    background-color: #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1>💠 NeoShell: Interactive Command Hub</h1>", unsafe_allow_html=True)
st.caption("A sleek virtual shell — Execute, Redirect, and Manage processes interactively.")

BASE_DIR = "Documents"
os.makedirs(BASE_DIR, exist_ok=True)

# -------------------- CORE LOGIC --------------------
def run_pipeline(cmds):
    procs = []
    prev = None
    for cmd in cmds:
        args = shlex.split(cmd)
        if prev is None:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            p = subprocess.Popen(args, stdin=prev.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            prev.stdout.close()
        prev = p
        procs.append(p)
    out, err = procs[-1].communicate()
    for p in procs[:-1]:
        p.wait()
    return out, err

def handle_command(cmd: str, background: bool=False):
    cmd = cmd.strip()
    try:
        if not cmd:
            return "(no command entered)"
        if "|" in cmd:
            parts = [p.strip() for p in cmd.split("|")]
            if background:
                threading.Thread(target=lambda: run_pipeline(parts), daemon=True).start()
                return "[Piping] started in background"
            out, err = run_pipeline(parts)
            return "[Piping]\n" + (out or "") + (err or "")
        if ">>" in cmd:
            left, right = cmd.split(">>", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "a", encoding="utf-8") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE, text=True)
            return f"[Append Redirection] added to {filename}"
        if ">" in cmd:
            left, right = cmd.split(">", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE, text=True)
            return f"[Output Redirection] written to {filename}"
        if "<" in cmd:
            left, right = cmd.split("<", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
                p = subprocess.run(args, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "[Input Redirection]\n" + (p.stdout or "") + (p.stderr or "")
        if background or cmd.endswith("&"):
            clean_cmd = cmd.rstrip("&").strip()
            threading.Thread(target=lambda: subprocess.Popen(clean_cmd, shell=True), daemon=True).start()
            return f"[Background Process] started: {clean_cmd}"
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "[Execution Result]\n" + (p.stdout or p.stderr or "(no output)")
    except Exception as e:
        return f"Error: {e}"

# -------------------- COMMAND EXECUTION SECTION --------------------
st.markdown("### ⚙️ Command Execution")
col1, col2 = st.columns([8,1])
cmd_input = col1.text_input("", placeholder="e.g., echo Hello | findstr H  or  echo Hi > out.txt")
run_bg = col2.checkbox("Run in BG")
run_now = col2.button("Execute 🔹")

if run_now:
    if cmd_input.strip():
        result = handle_command(cmd_input, background=run_bg)
        st.code(result, language="bash")
    else:
        st.warning("Enter a valid command.")

# -------------------- FILE CREATION SECTION --------------------
st.markdown("---")
st.markdown("### 📂 File Creation")

fcol1, fcol2 = st.columns([3,7])
filename = fcol1.text_input("File Name", placeholder="e.g., project.txt")
content = fcol2.text_area("File Content", height=180, placeholder="Type your file content here...")

create_clicked = st.button("Create & Auto-Download ⬇️")

if create_clicked:
    if not filename.strip():
        st.warning("Please enter a filename.")
    else:
        file_path = os.path.join(BASE_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        data_bytes = content.encode("utf-8")
        b64 = base64.b64encode(data_bytes).decode()
        href = f"data:application/octet-stream;base64,{b64}"

        st.success(f"File '{filename}' created successfully.")
        auto_html = f"""
        <a id="dl" href="{href}" download="{filename}"></a>
        <script>document.getElementById('dl').click();</script>
        """
        st.markdown(auto_html, unsafe_allow_html=True)
        st.caption(f"File stored temporarily in app environment: {file_path}")

# -------------------- FILE MANAGER --------------------
st.markdown("---")
st.markdown("### 🗂️ File Manager")

files = sorted(os.listdir(BASE_DIR))
if files:
    for fn in files:
        pth = os.path.join(BASE_DIR, fn)
        size = os.path.getsize(pth)
        st.write(f"📘 **{fn}** — {size} bytes")
        with st.expander("Preview " + fn):
            with open(pth, "r", errors="ignore", encoding="utf-8") as f:
                st.text(f.read())
else:
    st.info("No files created yet. Create one above ⬆️")
