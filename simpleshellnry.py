import streamlit as st
import subprocess
import os
import io

# =========================
# 🎨 Custom Styling (Tech Theme)
# =========================
st.set_page_config(page_title="NeoShell: Interactive Command Hub", page_icon="💠", layout="centered")

st.markdown("""
<style>
body {background-color: #eaf0fb;}
.main-title {
  font-size: 2.8em; font-weight: 700; color:#003d9e;
  text-align:center; animation: fadeInDown 0.8s;
}
@keyframes fadeInDown {
  0% {opacity:0; transform:translateY(-15px);}
  100% {opacity:1; transform:translateY(0);}
}
.section-card {
  background:white; padding:20px; border-radius:14px;
  box-shadow:0 3px 10px rgba(0,0,0,0.1); margin-bottom:18px;
}
.badge {
  display:inline-block; padding:4px 10px; border-radius:12px;
  color:white; font-size:0.8em; margin-left:6px;
}
.badge.exec{background:#007bff;}
.badge.pipe{background:#17a2b8;}
.badge.redir{background:#ffc107; color:#222;}
.badge.bg{background:#6f42c1;}
.badge.append{background:#28a745;}
.process-info {
  background:#f4f8ff; padding:10px 15px; border-left:4px solid #003d9e;
  border-radius:6px; margin-top:10px; font-size:0.9em;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🏷️ Header
# =========================
st.markdown("<h1 class='main-title'>💠 NeoShell: Interactive Command Hub</h1>", unsafe_allow_html=True)
st.markdown("#### 💻 Experience a modern take on simple shell operations — with process insights, file handling, and auto downloads.")

# =========================
# 🧩 Command Execution Section
# =========================
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("🧩 Command Execution")

command = st.text_input("💬 Enter a shell command (e.g., `ls`, `grep`, `cat file.txt`, `ls > out.txt`, `cat < in.txt`, `cat file.txt | grep data`, `sleep 5 &`)")

if st.button("▶️ Execute Command"):
    if command:
        # Identify operation type and process name
        if "|" in command:
            op_type = "Piping"
            op_info = "Transfers output of one process as input to another process."
        elif ">" in command and ">>" not in command:
            op_type = "Output Redirection"
            op_info = "Redirects standard output of a process to a file."
        elif ">>" in command:
            op_type = "Append Redirection"
            op_info = "Appends output of a process to an existing file."
        elif "<" in command:
            op_type = "Input Redirection"
            op_info = "Reads input for a process from a file instead of keyboard."
        elif "&" in command:
            op_type = "Background Process"
            op_info = "Runs a process in the background, allowing other commands to execute."
        else:
            op_type = "Process Execution"
            op_info = "Executes a new process using system resources."

        # Badge colors
        type_map = {
            "Process Execution": "exec",
            "Piping": "pipe",
            "Output Redirection": "redir",
            "Input Redirection": "redir",
            "Append Redirection": "append",
            "Background Process": "bg"
        }

        # Display process type and info
        st.markdown(f"🔍 Operation Type: <span class='badge {type_map.get(op_type, 'exec')}'>{op_type}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='process-info'>🧠 <b>Process Description:</b> {op_info}</div>", unsafe_allow_html=True)

        # Execute the command
        try:
            if "&" in command:  # background process
                subprocess.Popen(command.replace("&", ""), shell=True)
                st.success("✅ Background process started!")
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.stdout:
                    st.text_area("📤 Output:", result.stdout, height=150)
                if result.stderr:
                    st.text_area("⚠️ Error:", result.stderr, height=120)
        except Exception as e:
            st.error(f"An error occurred: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 🗂️ File Creation Section
# =========================
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("🗂️ Create a File")

filename = st.text_input("📁 Enter filename (e.g., `notes.txt`)")
file_content = st.text_area("📝 Enter file content here:")

if st.button("💾 Save File"):
    if filename and file_content:
        buffer = io.BytesIO(file_content.encode())
        st.download_button(
            label="⬇️ Download File",
            data=buffer,
            file_name=filename,
            mime="text/plain"
        )
        st.success(f"✅ File '{filename}' created and ready for download.")
    else:
        st.warning("⚠️ Please enter both filename and content.")
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 📂 Files Created Section
# =========================
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("📂 Files Created This Session")

if "created_files" not in st.session_state:
    st.session_state.created_files = []

if filename and st.button("🗃️ Add to Created Files"):
    st.session_state.created_files.append(filename)
    st.success(f"📄 '{filename}' added to created files list!")

if st.session_state.created_files:
    st.write(st.session_state.created_files)
else:
    st.info("📁 No files created yet in this session.")
st.markdown("</div>", unsafe_allow_html=True)
