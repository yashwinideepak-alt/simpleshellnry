import streamlit as st
import subprocess
from io import BytesIO

# ============================
# PAGE CONFIG + STYLE
# ============================
st.set_page_config(page_title="NeoShell: Interactive Command Hub", page_icon="💠")

st.markdown("""
    <style>
        body {background-color: #eef3fb;}
        .main-title {font-size: 2.4em; font-weight: 700; color: #004aad; text-align:center;}
        .stButton>button {
            background-color: #0066ff !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 600;
            font-size: 16px;
            width: 100%;
            height: 45px;
        }
        .stButton>button:hover {transform: scale(1.03);}
        .file-box {
            border: 2px solid #004aad;
            padding: 10px;
            border-radius: 10px;
            background-color: #ffffff;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💠 NeoShell: Interactive Command Hub</div>", unsafe_allow_html=True)

# Store files in session
if "files" not in st.session_state:
    st.session_state.files = {}

# ============================
# COMMAND EXECUTION
# ============================
st.subheader("🧩 Command Execution")

col1, col2, col3 = st.columns([7, 2, 2])
cmd = col1.text_input("", placeholder="Example: echo Hello | findstr H")
run_bg = col2.checkbox("Run in BG")
run_btn = col3.button("🚀 Execute")

if run_btn and cmd.strip():
    try:
        if run_bg:
            subprocess.Popen(cmd, shell=True)
            st.success("✅ Command running in background!")
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            st.code(result.stdout if result.stdout else result.stderr or "Done ✅")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ============================
# FILE CREATION
# ============================
st.subheader("📂 Create a File")

fname = st.text_input("File name:", "output.txt")
fdata = st.text_area("Enter file content:")

if st.button("💾 Save File"):
    if fname.strip():
        st.session_state.files[fname] = fdata.encode()
        st.success(f"✅ File '{fname}' saved successfully!")
    else:
        st.warning("⚠️ Enter a valid file name.")

# ============================
# FILES CREATED SECTION ✅
# ============================
st.subheader("🗂️ Files Created")

if st.session_state.files:
    for file_name, file_bytes in st.session_state.files.items():
        with st.container():
            st.markdown(f"<div class='file-box'><b>{file_name}</b></div>", unsafe_allow_html=True)

            dcol1, dcol2 = st.columns([2, 2])

            # View content
            if dcol1.button(f"📖 View {file_name}", key=file_name):
                st.text_area("Content:", file_bytes.decode(), height=120)

            # Download
            dcol2.download_button(
                label=f"⬇️ Download {file_name}",
                data=file_bytes,
                file_name=file_name,
                mime="text/plain"
            )
else:
    st.info("📭 No files created yet!")


st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>NeoShell v3.0 — Enhanced File Manager ✅</p>", unsafe_allow_html=True)
