import streamlit as st
import subprocess
import shlex
import os
import threading

st.title("🖥️ MySimpleShell - Web Interface")

st.markdown("### Run Shell Commands")
command = st.text_input("Enter command:", placeholder="e.g., ls | grep py")
background = st.checkbox("Run in background (&)")
run_button = st.button("Run")

output_area = st.empty()

# --- Helper function for pipelines ---
def run_pipeline(cmds):
    procs = []
    prev = None
    for cmd in cmds:
        args = shlex.split(cmd)
        p = subprocess.Popen(args, stdin=prev.stdout if prev else None,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if prev:
            prev.stdout.close()
        prev = p
        procs.append(p)
    out, err = procs[-1].communicate()
    for p in procs[:-1]:
        p.wait()
    return out, err

# --- Modified handle_command with operation labels ---
def handle_command(cmd, background=False):
    # Piping
    if "|" in cmd:
        cmds = [c.strip() for c in cmd.split("|")]
        operation = "Piping"
        if background:
            threading.Thread(target=run_pipeline, args=(cmds,), daemon=True).start()
            return f"[{operation} - Running in background]\n"
        out, err = run_pipeline(cmds)
        return f"[{operation}]\n" + out + err

    # Output redirection
    if ">" in cmd and ">>" not in cmd:
        parts = cmd.split(">")
        command = parts[0].strip()
        outfile = parts[1].strip()
        operation = "Output Redirection"
        with open(outfile, "w") as f:
            subprocess.run(shlex.split(command), stdout=f, text=True)
        return f"[{operation}] Output written to {outfile}\n"

    if ">>" in cmd:
        parts = cmd.split(">>")
        command = parts[0].strip()
        outfile = parts[1].strip()
        operation = "Output Redirection (Append)"
        with open(outfile, "a") as f:
            subprocess.run(shlex.split(command), stdout=f, text=True)
        return f"[{operation}] Output appended to {outfile}\n"

    # Input redirection
    if "<" in cmd:
        parts = cmd.split("<")
        command = parts[0].strip()
        infile = parts[1].strip()
        operation = "Input Redirection"
        with open(infile, "r") as f:
            result = subprocess.run(shlex.split(command), stdin=f, capture_output=True, text=True)
        return f"[{operation}]\n" + result.stdout + result.stderr

    # Background process
    if background:
        operation = "Process Creation (Background)"
        subprocess.Popen(shlex.split(cmd))
        return f"[{operation}] {cmd}\n"

    # Normal command execution
    operation = "Process Execution"
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return f"[{operation}]\n" + result.stdout + result.stderr

# --- Run button logic ---
if run_button:
    if command.strip():
        out = handle_command(command.strip(), background)
        output_area.code(out or "(no output)")

# --- File creation section ---
st.markdown("---")
st.subheader("📁 Create and View File")

filename = st.text_input("Filename:", "notes.txt")
content = st.text_area("File content:", "Hello from my simple shell!")

if st.button("Create File"):
    with open(filename, "w") as f:
        f.write(content)
    st.success(f"File '{filename}' created!")
    with open(filename, "r") as f:
        st.code(f.read())

# --- Show existing files ---
st.markdown("### 📂 Existing Files in VM:")
files = os.listdir(".")
st.write(files)

