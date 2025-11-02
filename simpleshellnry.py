# simple_shell_app.py
import streamlit as st
import subprocess
import os
import io
import time
from datetime import datetime
from pathlib import Path
import threading
import base64

# -------------------- Page config + Styling --------------------
st.set_page_config(page_title="NeoShell: Interactive Command Hub",
                   page_icon="💠", layout="centered")

st.markdown("""
<style>
/* Page */
body {background: linear-gradient(180deg,#eef4fb 0%, #f7fbff 100%);}
.main-title {font-size:2.4rem; color:#012a4a; text-align:center; font-weight:700; margin-bottom:4px;}
.subtitle {color:#345; text-align:center; margin-bottom:18px;}
.section-card {background:#fff; padding:18px; border-radius:12px; box-shadow:0 6px 18px rgba(2,24,60,0.06); margin-bottom:18px;}
.badge {display:inline-block; padding:6px 10px; border-radius:999px; color:white; font-weight:700; font-size:0.85em;}
.badge.exec{background:#007bff;}
.badge.pipe{background:#17a2b8;}
.badge.redir{background:#ffb020; color:#122;}
.badge.append{background:#28a745;}
.badge.bg{background:#6f42c1;}
.process-box {background:#f2f7ff; padding:10px 12px; border-left:4px solid #007bff; border-radius:6px; margin-top:10px;}
.code-area pre {background:#f6fbff !important; color:#022; padding:10px; border-radius:8px;}
.file-card {border:1px solid #e2eefc; border-radius:10px; padding:10px; background:#fff; margin-bottom:10px;}
.small-muted {color:#6b7280; font-size:0.9em;}
.exec-row {display:flex; gap:8px; align-items:center;}
/* make button columns consistent height */
.stButton > button {height:44px; border-radius:10px;}
/* responsive tweaks */
@media (max-width:600px) {
  .main-title {font-size:1.6rem;}
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💠 NeoShell: Interactive Command Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Run commands, inspect process type & time, create files and download — files are accessible to shell commands.</div>", unsafe_allow_html=True)

# -------------------- Workspace setup --------------------
WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

# Keep created-files metadata in session
if "created_files" not in st.session_state:
    st.session_state.created_files = {}  # filename -> {ts, size}

# -------------------- Helper functions --------------------
def classify_command(cmd: str, background_flag: bool):
    s = cmd.strip()
    if not s:
        return "No Command", "No operation"
    if "|" in s:
        return "Piping", "Transfers output of one process as input to another."
    if ">>" in s:
        return "Append Redirection", "Appends a process's output to a file."
    if ">" in s:
        return "Output Redirection", "Redirects a process's output to a file."
    if "<" in s:
        return "Input Redirection", "Uses a file as input for a process."
    if background_flag or s.endswith("&"):
        return "Background Process", "Runs a process in the background without blocking."
    return "Process Execution", "Executes a single process and waits for it."

def run_command(cmd: str, background: bool=False):
    """Run shell command with cwd=WORKSPACE so created files are visible."""
    cmd = cmd.strip()
    if not cmd:
        return {"stdout":"", "stderr":"", "time":0.0, "status":"empty"}

    op_type, op_info = classify_command(cmd, background)

    start = time.perf_counter()
    try:
        if op_type == "Background Process":
            # start and return immediately
            clean = cmd.rstrip("&").strip()
            p = subprocess.Popen(clean, shell=True, cwd=str(WORKSPACE))
            elapsed = time.perf_counter() - start
            return {"stdout":f"Background process started (PID: {p.pid})", "stderr":"", "time":elapsed, "op_type":op_type, "op_info":op_info}
        else:
            # Use shell=True so pipes / redirections are interpreted by shell; set cwd so files are accessed relative to workspace
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
            elapsed = time.perf_counter() - start
            return {"stdout":res.stdout, "stderr":res.stderr, "time":elapsed, "op_type":op_type, "op_info":op_info}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"stdout":"", "stderr":str(e), "time":elapsed, "op_type":op_type, "op_info":op_info}

def add_created_file(fname: str):
    path = WORKSPACE / fname
    try:
        size = path.stat().st_size
    except Exception:
        size = 0
    st.session_state.created_files[fname] = {"ts": datetime.now().isoformat(timespec="seconds"), "size": size}

# -------------------- SECTION 1: Command Execution --------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("🧩 Command Execution (workspace = `workspace/`)")

col_cmd, col_bg, col_run = st.columns([8,1,1])
command = col_cmd.text_input("Enter shell command", placeholder="e.g., ls | grep .py   or   echo hi > file.txt")
bg_flag = col_bg.checkbox("Run BG")
run_pressed = col_run.button("Execute")

if run_pressed:
    if not command.strip():
        st.warning("Please enter a command.")
    else:
        # run command in a thread when piping/background to avoid blocking UI if necessary
        # But for immediate results we run synchronously unless background.
        res = run_command(command, background=bg_flag)
        op_type = res.get("op_type")
        op_info = res.get("op_info")
        exec_time = res.get("time", 0.0)

        # Badge mapping
        bmap = {"Process Execution":"exec","Piping":"pipe","Output Redirection":"redir",
                "Input Redirection":"redir","Append Redirection":"append","Background Process":"bg"}

        badge_class = bmap.get(op_type,"exec")
        st.markdown(f"🔍 Operation type: <span class='badge {badge_class}'>{op_type}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='process-box'><b>Process description:</b> {op_info}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:8px'><span class='small-muted'>⏱ Execution time:</span> <b>{exec_time:.4f} s</b></div>", unsafe_allow_html=True)

        # show output / error
        if res.get("stdout"):
            st.markdown("<div class='code-area'>", unsafe_allow_html=True)
            st.code(res["stdout"], language="bash")
            st.markdown("</div>", unsafe_allow_html=True)
        if res.get("stderr"):
            st.error(res["stderr"])

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- SECTION 2: File creation --------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("📂 Create a File (saved to workspace and available to commands)")

fcol1, fcol2 = st.columns([3,9])
filename = fcol1.text_input("Filename", value="example.txt", help="Enter name like notes.txt")
content = fcol2.text_area("File content", value="", height=160)

create_clicked = st.button("💾 Create & Download")

if create_clicked:
    if not filename.strip():
        st.warning("Enter a filename.")
    else:
        # Save to workspace so shell commands can access it
        path = WORKSPACE / filename
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            add_created_file(filename)
            # Prepare bytes for download
            b = content.encode("utf-8")
            st.success(f"✅ File '{filename}' saved to workspace/")
            # Automatic download (user-initiated click triggered by button - safe)
            st.download_button(label="⬇️ Download file to your system", data=b, file_name=filename, mime="text/plain")
        except Exception as e:
            st.error(f"Could not create file: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- SECTION 3: Files Created (browser) --------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("📁 Files Created (workspace/)")

# Update created_files list by scanning workspace as well (in case files were created by shell commands)
for p in sorted(WORKSPACE.iterdir()):
    if p.is_file():
        if p.name not in st.session_state.created_files:
            add_created_file(p.name)

if st.session_state.created_files:
    for name, meta in st.session_state.created_files.items():
        row = st.container()
        with row:
            st.markdown(f"<div class='file-card'><b>📄 {name}</b>  <span class='small-muted'> — created: {meta.get('ts')}  •  {meta.get('size',0)} bytes</span></div>", unsafe_allow_html=True)
            pc1, pc2, pc3 = st.columns([4,2,1])
            # preview
            if pc1.button(f"📖 Preview {name}", key=f"view_{name}"):
                try:
                    txt = (WORKSPACE / name).read_text(encoding="utf-8")
                    st.text_area(f"Contents of {name}", txt, height=200)
                except Exception as e:
                    st.error(f"Cannot read file: {e}")
            # download
            try:
                with open(WORKSPACE / name, "rb") as fh:
                    data = fh.read()
                pc2.download_button(label=f"⬇️ Download", data=data, file_name=name, mime="text/plain")
            except Exception as e:
                pc2.error("Download error")
            # delete
            if pc3.button("🗑️ Delete", key=f"del_{name}"):
                try:
                    path = WORKSPACE / name
                    if path.exists():
                        path.unlink()
                    st.session_state.created_files.pop(name, None)
                    st.success(f"Deleted {name}")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")
else:
    st.info("No files created yet. Use 'Create a File' or run commands that produce files (e.g., `echo hi > file.txt`).")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Footer --------------------
st.markdown("<div style='text-align:center; color:#5b6b78; margin-top:14px;'>NeoShell • polished shell demo • files stored in <code>workspace/</code></div>", unsafe_allow_html=True)
