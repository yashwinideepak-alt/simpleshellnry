import streamlit as st
import subprocess
import shlex
import os
import threading
import base64
from io import BytesIO
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="MySimpleShell", page_icon="💻", layout="centered")

st.title("💻 MySimpleShell")
st.markdown("Light, simple shell UI — runs commands, supports pipes/redirection/background, and auto-downloads created files.")

# create a local folder in the app environment (not required for download, but useful to keep files)
BASE_DIR = "Documents"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------- Helper: pipeline runner ----------
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

# ---------- Command handler ----------
def handle_command(cmd: str, background: bool=False):
    cmd = cmd.strip()
    try:
        if not cmd:
            return "(no command entered)"

        # piping
        if "|" in cmd:
            parts = [p.strip() for p in cmd.split("|")]
            if background:
                threading.Thread(target=lambda: run_pipeline(parts), daemon=True).start()
                return "[Piping] started in background"
            out, err = run_pipeline(parts)
            header = "[Piping]\n"
            return header + (out or "") + (err or "")

        # append redirection
        if ">>" in cmd:
            left, right = cmd.split(">>", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "a", encoding="utf-8") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE, text=True)
            return f"[Output Redirection (Append)] appended to {filename}"

        # output redirection
        if ">" in cmd:
            left, right = cmd.split(">", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
                subprocess.run(args, stdout=f, stderr=subprocess.PIPE, text=True)
            return f"[Output Redirection] written to {filename}"

        # input redirection
        if "<" in cmd:
            left, right = cmd.split("<", 1)
            args = shlex.split(left)
            filename = right.strip()
            with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
                p = subprocess.run(args, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "[Input Redirection]\n" + (p.stdout or "") + (p.stderr or "")

        # background process
        if background or cmd.endswith("&"):
            # strip trailing &
            clean_cmd = cmd.rstrip("&").strip()
            threading.Thread(target=lambda: subprocess.Popen(clean_cmd, shell=True), daemon=True).start()
            return f"[Process Creation (Background)] {clean_cmd}"

        # normal execution
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "[Process Execution]\n" + (p.stdout or p.stderr or "(no output)")
    except FileNotFoundError:
        return "Error: command not found"
    except Exception as e:
        return f"Error: {e}"

# ---------- UI: Commands ----------
st.subheader("Run a command")
col1, col2 = st.columns([8,1])
cmd_input = col1.text_input("", placeholder="e.g., echo Hello | grep H  OR  echo Hi > out.txt")
run_bg = col2.checkbox("Background")
run_now = col2.button("Run")

if run_now:
    if cmd_input.strip() == "":
        st.warning("Enter a command first.")
    else:
        output = handle_command(cmd_input, background=run_bg)
        st.code(output, language="bash")

# ---------- UI: File creation (auto-download) ----------
st.markdown("---")
st.subheader("Create a file (auto-download)")

fcol1, fcol2 = st.columns([3,7])
filename = fcol1.text_input("Filename (e.g., notes.txt)", value="")
content = fcol2.text_area("File content", value="", height=160)

create_clicked = st.button("Create File and Download")

if create_clicked:
    if not filename.strip():
        st.warning("Please enter a filename (e.g., notes.txt).")
    else:
        # save in app environment
        path = os.path.join(BASE_DIR, filename)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
        except Exception as e:
            st.error(f"Could not save file in app environment: {e}")
            path = None

        # prepare bytes for download
        data_bytes = content.encode("utf-8")
        b64 = base64.b64encode(data_bytes).decode()
        data_href = f"data:application/octet-stream;base64,{b64}"

        st.success(f"File '{filename}' created.")

        # Insert an anchor tag and auto-click via JS (works when browser allows it after your interaction)
        auto_click_html = f"""
        <a id="dl" href="{data_href}" download="{filename}">Download link</a>
        <script>
        const a = document.getElementById('dl');
        if (a) {{
            a.click();
        }}
        </script>
        """
        st.markdown(auto_click_html, unsafe_allow_html=True)

        # Fallback download button (in case browser blocks auto-click)
        st.download_button("If not downloaded automatically, click to download", data=data_bytes, file_name=filename, mime="text/plain")

        # show location inside app environment for reference
        if path:
            st.info(f"(Saved in app environment: {path})")
            st.caption(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------- UI: Show files in app environment ----------
st.markdown("---")
st.subheader("Files created in app environment (Documents/)")

files = sorted(os.listdir(BASE_DIR))
if files:
    for fn in files:
        pth = os.path.join(BASE_DIR, fn)
        size = os.path.getsize(pth)
        st.write(f"• {fn} — {size} bytes")
        with open(pth, "r", errors="ignore", encoding="utf-8") as fh:
            txt = fh.read()
        with st.expander("Preview " + fn):
            st.text(txt)
else:
    st.info("No files created yet.")
