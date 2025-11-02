import streamlit as st
import subprocess
import shlex
import os
import threading
import base64
from datetime import datetime

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="NeoShell: Interactive Command Hub",
    page_icon="💠",
    layout="centered"
)

# ---------- Custom Styling ----------
st.markdown("""
<style>
/* Overall page background */
.stApp {
    background-color: #f6f9fc;
}

/* Headers */
h1, h2, h3, h4 {
    color: #0a2342;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Inputs and buttons */
.stTextInput > div > div > input, textarea {
    background-color: #ffffff !important;
    border: 1px solid #b8c2cc !important;
    border-radius: 10px !important;
    color: #0a2342 !important;
}

.stButton > button {
    background-color: #0078d4 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500;
    padding: 0.6em 1.2em !important;
    transition: background-color 0.2s ease;
}

.stButton > button:hover {
    background-color: #005fa3 !important;
}

/* Code blocks */
code, pre {
    background-color: #eaf1f8 !important;
    color: #0a2342 !important;
    border-radius: 8px;
    padding: 0.6em;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<h1 style='text-align:center;'>💠 NeoShell: Interactive Command Hub</h1>", unsafe_allow_html=True)
st.caption("A lightweight virtual shell environment — Execute, Redirect, and Manage processes seamlessly.")

# ---------- Folder setup ----------
BASE_DIR = "Documents"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------- Core Logic ----------
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

# ---------- Command Section ----------
st.markdown("### ⚙️ Command Execution")
col1, col2 = st.columns([8,1])
cmd_input = col1.text_input("", placeholder="e.g., echo Hello | grep H  or  echo Hi > out.txt")
run_bg = col2.checkbox("Run in BG")
run_now = col2.button("Execute 🔹")

if run_now:
    if cmd_input.strip():
        result = handle_command(cmd_input, background=run_bg)
        st.code(result, language="bash")
    else:
        st.warning("Enter a valid command.")

# ---------- File Creation ----------
st.markdown("---")
st.markdown("### 📂 File Creation")

fcol1, fcol2 = st.columns([3,7])
filename = fcol1.text_input("File Name", placeholder="e.g., report.txt")
content = fcol2.text_area("File Content", height=180, placeholder="Enter text here...")

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
        <a id="dl" href="{href}" download="{filename}">Download</a>
        <script>document.getElementById('dl').click();</script>
        """
        st.markdown(auto_html, unsafe_allow_html=True)

        st.caption(f"Saved temporarily in app environment: {file_path}")

# ---------- File Manager ----------
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
    st.info("No files yet. Create one above ⬆️")
