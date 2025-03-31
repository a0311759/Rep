import streamlit as st
import json
import os
import subprocess

DB_FILE = "users.json"
CODE_DIR = "user_codes"

# Ensure users.json exists
def load_users():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Ensure user code directories exist
def ensure_user_dir(username):
    user_path = os.path.join(CODE_DIR, username)
    os.makedirs(user_path, exist_ok=True)
    return user_path

# User authentication
def authenticate(username, password):
    users = load_users()
    return users.get(username) == password

def register_user(username, password):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = password
    save_users(users)
    ensure_user_dir(username)
    return True

def run_code(code):
    with open("temp.py", "w") as f:
        f.write(code)
    result = subprocess.run(["python", "temp.py"], capture_output=True, text=True)
    return result.stdout + result.stderr

# Streamlit UI
st.title("Online Code Storage & Execution Platform")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if register_user(new_username, new_password):
                st.success("User registered! Please log in.")
            else:
                st.error("Username already exists.")
else:
    # Dashboard Navigation
    st.sidebar.title("Dashboard")
    user_path = ensure_user_dir(st.session_state.username)
    code_files = os.listdir(user_path)
    selected_file = st.sidebar.selectbox("Select file", ["New File"] + code_files)
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    
    st.subheader(f"Welcome, {st.session_state.username}")
    
    code_content = "" if selected_file == "New File" else open(os.path.join(user_path, selected_file)).read()
    code = st.text_area("Your Code", value=code_content, height=250)
    filename = st.text_input("Filename", value=selected_file if selected_file != "New File" else "script.py")
    
    if st.button("Save Code"):
        with open(os.path.join(user_path, filename), "w") as f:
            f.write(code)
        st.success("Code saved successfully!")


    
    if st.button("Run Code"):
        output = run_code(code)
        st.text_area("Output", value=output, height=200, disabled=True)
