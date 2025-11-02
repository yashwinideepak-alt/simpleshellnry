import streamlit as st
import subprocess
import os
from io import BytesIO

# ============================
# 🎨 Custom CSS Styling
# ============================
st.set_page_config(page_title="NeoShell: Interactive Command Hub", page_icon="💠", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #f4f7fb;
            color: #222;
            font-family: 'Segoe UI', sans-serif;
        }
        .main-title {
            font-size: 2.5em;
            font-weight: 700;
            color: #004aad;
            text-align: center;
            margin-bottom: 0.3em;
        }
        .sub-title {
            font-size: 1.1em;
            color: #5b5b5b;
            text-align: center;
            margin-bottom: 2em;
        }
        .stTextInput > div > div > input {
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        .stButton>button {
            background-color: #007bff !important;
            color: white !important;
            border-radius: 10px !important;
            height: 45px;
            width: 100%;
            font-weight: 600;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #0056b3 !important;
            transform: scale(1.03);
        }
        .stDownloadButton>button {
            background-color: #28a745 !important;
            color: white !important;
            border-radius: 10px !important;
            height: 45px;
            width: 100%;
            font-weight: 600;
            font-size: 16px;
        }
        .stDownloadButton>button:hover {
            background-color: #1e7e34 !important;
            transform: scale(1.03);
        }
    </style>
""", unsafe_allow_html=True)

# ============================
# 🧠 Title Section
# ============================
st.markdown("<div class='main-title'>💠 NeoShell: Interactive Command Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Run commands, create files, and explore process operations — all in one clean, technical shell.</div>", unsafe_allow_html=True)

# ============================
# 🧱 Command Execution
# ============================
st.markdown("### 🧩 Command Execution")

col1, col2, col3 = st.columns([7, 2, 2])
cmd_input = col1.text_input("", placeholder="e.g., echo Hello | findstr H  or  echo Hi > out.txt")
run_bg = col2.checkbox("Run in BG")
run_now = col3.button("🚀 Execute")

if run_now and cmd_input:
    try:
        if run_bg:
            subprocess.Popen(cmd_input, shell=True)
            st.success("✅ Command running in background!")
        else:
            result = subprocess.run(cmd_input, shell=True, capture_output=True, text=True)
            st.code(result.stdout if result.stdout else result.stderr or "✅ Command executed successfully.", language="bash")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ============================
# 📝 File Creation Section
# ============================
st.markdown("### 📂 Create & Download a File")

filename = st.text_input("Enter file name (with .txt or .docx extension):", "os_output.txt")
file_content = st.text_area("Enter file content:", height=150, placeholder="Type your file content here...")

if st.button("💾 Create & Download File"):
    if filename.strip():
        try:
            # Save file temporarily in memory for download
            buffer = BytesIO()
            buffer.write(file_content.encode())
            buffer.seek(0)

            st.download_button(
                label="⬇️ Download Your File",
                data=buffer,
                file_name=filename,
                mime="text/plain"
            )
            st.success(f"✅ File '{filename}' created successfully! Click above to download.")
        except Exception as e:
            st.error(f"❌ Error creating file: {e}")
    else:
        st.warning("⚠️ Please enter a valid filename.")

# ============================
# ⚙️ System Info Section
# ============================
st.markdown("### 🖥️ Quick System Info")
try:
    uname = os.uname()
    st.text(f"System: {uname.sysname}")
    st.text(f"Node Name: {uname.nodename}")
    st.text(f"Release: {uname.release}")
    st.text(f"Version: {uname.version}")
    st.text(f"Machine: {uname.machine}")
except Exception:
    st.info("ℹ️ System info not available on this platform.")

# ============================
# 📘 Footer
# ============================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#777;'>🧠 Developed with 💙 using Streamlit • NeoShell v2.0</p>", unsafe_allow_html=True)
