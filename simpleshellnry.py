import streamlit as st
import subprocess, os, time
from pathlib import Path
from datetime import datetime

# ---------- Page Setup ----------
st.set_page_config(page_title="⚙️ NeoShell Workbench", page_icon="💠", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
<style>
body {background:linear-gradient(180deg,#f4f7fb 0%,#edf2f8 100%);}
h1,h2,h3{color:#003566;}
.section{background:#ffffff;border-radius:12px;box-shadow:0 6px 14px rgba(0,0,0,0.05);padding:20px;margin-bottom:18px;}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;color:#fff;font-weight:700;font-size:0.85em;}
.exec{background:#007bff;} .pipe{background:#17a2b8;}
.redir{background:#ffb020;color:#222;} .append{background:#28a745;}
.bg{background:#6f42c1;} .info{color:#5b6b78;font-size:0.9em;}
.stButton>button{height:44px;border-radius:10px;background:#007bff;color:white;font-weight:600;border:none;}
.stButton>button:hover{background:#005fcc;color:white;}
</style>
""", unsafe_allow_html=True)

# ---------- Workspace Directory ----------
WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

if "created_files" not in st.session_state:
    st.session_state.created_files = {}

def refresh_files():
    for f in WORKSPACE.iterdir():
        if f.is_file() and f.name not in st.session_state.created_files:
            st.session_state.created_files[f.name] = {
                "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "size": f.stat().st_size,
            }

# ---------- Helper ----------
def classify(cmd, bg):
    if "|" in cmd: return "Piping","Connects output of one command as input to another."
    if ">>" in cmd: return "Append Redirection","Appends output to an existing file."
    if ">" in cmd: return "Output Redirection","Writes command output to a new file."
    if "<" in cmd: return "Input Redirection","Takes input from a file."
    if bg or cmd.strip().endswith("&"): return "Background Process","Runs a command in background."
    return "Process Execution","Runs a standard command and waits for completion."

def run_command(cmd, bg):
    op_type, desc = classify(cmd,bg)
    start = time.perf_counter()
    try:
        if op_type=="Background Process":
            clean = cmd.rstrip("&").strip()
            p = subprocess.Popen(clean,shell=True,cwd=str(WORKSPACE))
            return op_type,desc,0.0,f"Started background PID {p.pid}",""
        res = subprocess.run(cmd,shell=True,capture_output=True,text=True,cwd=str(WORKSPACE))
        t = time.perf_counter()-start
        refresh_files()
        return op_type,desc,t,res.stdout,res.stderr
    except Exception as e:
        return op_type,desc,0.0,"",str(e)

# ---------- Title ----------
st.markdown("<h1 style='text-align:center;'>⚙️ NeoShell Workbench</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#345;'>Interactive technical shell with file access & visual feedback</p>", unsafe_allow_html=True)

# ======================================================
# SECTION 1: Command Execution
# ======================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🧩 Command Execution")

c1,c2,c3 = st.columns([7,2,2])
cmd = c1.text_input("Enter command",placeholder="e.g., ls | grep .py   or   cat file.txt")
bg = c2.checkbox("Background")
run = c3.button("Execute")

if run:
    if not cmd.strip():
        st.warning("Enter a command first.")
    else:
        t,desc,time_taken,out,err = run_command(cmd,bg)
        color = {"Process Execution":"exec","Piping":"pipe",
                 "Output Redirection":"redir","Input Redirection":"redir",
                 "Append Redirection":"append","Background Process":"bg"}[t]
        st.markdown(f"**Operation Type:** <span class='badge {color}'>{t}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:4px;'><b>Description:</b> {desc}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info'>⏱️ Execution Time: {time_taken:.4f} s</div>", unsafe_allow_html=True)
        if out: st.code(out)
        if err: st.error(err)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# SECTION 2: File Creation
# ======================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📂 Create File")
f1,f2 = st.columns([3,7])
fname = f1.text_input("Filename",value="example.txt")
content = f2.text_area("Content",height=150)
if st.button("💾 Create & Download"):
    if fname.strip()=="":
        st.warning("Provide filename.")
    else:
        path = WORKSPACE / fname
        path.write_text(content,encoding="utf-8")
        st.session_state.created_files[fname] = {"ts":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                 "size":len(content.encode())}
        with open(path,"rb") as f: data=f.read()
        st.success(f"File '{fname}' created and saved in workspace.")
        st.download_button("⬇️ Download File",data=data,file_name=fname,mime="text/plain")
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# SECTION 3: Files Created
# ======================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📁 Files Created")
refresh_files()

if st.session_state.created_files:
    for name,meta in st.session_state.created_files.items():
        colA,colB,colC = st.columns([6,2,2])
        colA.markdown(f"**📄 {name}**  <span class='info'>({meta['size']} bytes • {meta['ts']})</span>", unsafe_allow_html=True)
        if colB.button("📖 Preview",key=f"v_{name}"):
            try:
                txt = (WORKSPACE/name).read_text()
                st.text_area(f"Contents of {name}",txt,height=150)
            except Exception as e: st.error(e)
        with open(WORKSPACE/name,"rb") as f: data=f.read()
        colC.download_button("⬇️",data=data,file_name=name,mime="text/plain",key=f"d_{name}")
else:
    st.info("No files yet. Use 'Create File' or shell redirection to make one.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#555;'>NeoShell Workbench • files live in workspace/ directory</p>", unsafe_allow_html=True)
