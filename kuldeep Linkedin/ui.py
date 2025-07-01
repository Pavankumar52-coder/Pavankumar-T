# Import necessary libraries for Frontend
import streamlit as st
import requests
import time # Import time for small delays

# Frontend UI configuration
st.set_page_config(page_title="📧 AI Gmail Agent", layout="wide")
st.title("🤖 Chat-Based Gmail Automation Agent")

# Frontend UI content
st.markdown("""
Welcome! This agent helps you automate sending emails via Gmail using natural language.
Enter your request below, and the agent will guide you through the process,
showing you each step with visual feedback.
""")

# Initialize session state variables for persistent data
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""
if "email_address" not in st.session_state:
    st.session_state.email_address = ""
if "password_input" not in st.session_state:
    st.session_state.password_input = ""
if "processing_status" not in st.session_state:
    st.session_state.processing_status = "Awaiting your command..."
if "visual_steps" not in st.session_state:
    st.session_state.visual_steps = []
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# Main chat input for the user prompt
user_prompt = st.text_input("Tell me what email to send:", 
                            placeholder="e.g., Send an internship email to Insurebuzz expressing my interest in AI.",
                            key="user_prompt_input") 

# Display current status in a more prominent way
status_container = st.empty()
status_container.info(f"**Current Status:** {st.session_state.processing_status}")

# Input fields for entering the email address and password
with st.expander("Gmail Credentials (Required for Automation)", expanded=False):
    st.warning("Please use a **dedicated Gmail account** for this task. Do not use your primary personal Gmail account for security reasons. For Google accounts with 2-Factor Authentication (2FA) enabled, you might need to generate an 'App password' for programmatic access instead of your regular password.")
    with st.form("credentials_form"):
        email = st.text_input("Gmail Address:", value=st.session_state.email_address)
        password = st.text_input("Gmail Password / App Password:", type="password", value=st.session_state.password_input)
        
        send_button = st.form_submit_button("Start Email Automation")

if send_button:
    st.session_state.prompt_input = user_prompt
    st.session_state.email_address = email
    st.session_state.password_input = password
    
    if not st.session_state.prompt_input:
        st.error("Please enter a command for the email.")
    elif not st.session_state.email_address or not st.session_state.password_input:
        st.error("Please provide your Gmail address and password/App password.")
    else:
        st.session_state.processing_status = "Initiating automation... Please wait."
        status_container.info(f"**Current Status:** {st.session_state.processing_status}")
        st.session_state.visual_steps = []
        st.session_state.last_error = None
        # Placeholder for visual feedback
        visual_feedback_container = st.container()
        with st.spinner("Executing automation steps..."):
            try:
                # Send the request to the FastAPI backend
                response = requests.post("http://localhost:8000/send-email", json={
                    "prompt": st.session_state.prompt_input,
                    "email": st.session_state.email_address,
                    "password": st.session_state.password_input
                }, timeout=180)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.processing_status = data.get("status", "Automation completed.")
                    status_container.success(f"**Status:** {st.session_state.processing_status}")
                    st.subheader("📸 Visual Journey of Automation:")
                    
                    if not data.get("visual_feedback"):
                        st.warning("No visual feedback steps received from the backend.")

                    for i, step in enumerate(data.get("visual_feedback", [])):
                        with visual_feedback_container:
                            st.markdown(f"---")
                            step_message = step.get('message', 'No description available.')
                            step_image = step.get('image')
                            st.write(f"**Step {i+1}:** {step_message}")
                            
                            if step_image:
                                image_url = f"http://localhost:8000/screenshots/{step_image}"
                                try:
                                    st.image(image_url, caption=f"Screenshot: {step_message}", use_column_width=True)
                                    print(f"DEBUG_FRONTEND: Successfully tried to load image: {image_url}") # Debug print
                                except Exception as img_e:
                                    st.error(f"Could not load image '{step_image}' from '{image_url}': {img_e}")
                                    print(f"ERROR_FRONTEND: Failed to load image {image_url}: {img_e}") # Debug print
                            else:
                                st.warning("No image filename provided for this step.")
                            time.sleep(0.5) 
                    
                    status_container.success(f"**Final Status:** {st.session_state.processing_status}")

                else:
                    error_data = response.json()
                    error_message = error_data.get("error", "An unknown error occurred.")
                    st.session_state.last_error = error_message
                    st.session_state.processing_status = f"Automation Failed: {error_message}"
                    status_container.error(f"**Status:** {st.session_state.processing_status} - {st.session_state.last_error}")

                    if "visual_feedback" in error_data:
                        st.subheader("📸 Visual Feedback (Error Trace):")
                        for i, step in enumerate(error_data["visual_feedback"]):
                            with visual_feedback_container:
                                st.markdown(f"---")
                                step_message = step.get('message', 'No description available.')
                                step_image = step.get('image')
                                st.write(f"**Step {i+1} (Error Trace):** {step_message}")
                                if step_image:
                                    image_url = f"http://localhost:8000/screenshots/{step_image}"
                                    try:
                                        st.image(image_url, caption=f"Screenshot at error step {i+1}: {step_message}", use_column_width=True)
                                        print(f"DEBUG_FRONTEND: Successfully tried to load error image: {image_url}") # Debug print
                                    except Exception as img_e:
                                        st.error(f"Could not load error image '{step_image}' from '{image_url}': {img_e}")
                                        print(f"ERROR_FRONTEND: Failed to load error image {image_url}: {img_e}") # Debug print
                                else:
                                    st.warning("No image filename provided for this error step.")
                                time.sleep(0.5)

            except requests.exceptions.ConnectionError:
                st.session_state.last_error = "Could not connect to the backend server. Please ensure the FastAPI backend is running at http://localhost:8000."
                st.session_state.processing_status = "Connection Error."
                status_container.error(f"**Status:** {st.session_state.processing_status} - {st.session_state.last_error}")
            except requests.exceptions.Timeout:
                st.session_state.last_error = "The backend request timed out (it took longer than 3 minutes). This might indicate a very slow automation process, a stuck browser, or complex Gmail security checks."
                st.session_state.processing_status = "Request Timed Out."
                status_container.error(f"**Status:** {st.session_state.processing_status} - {st.session_state.last_error}")
            except Exception as e:
                st.session_state.last_error = f"An unexpected error occurred in the Streamlit app: {e}"
                st.session_state.processing_status = "Frontend Error."
                status_container.error(f"**Status:** {st.session_state.processing_status} - {st.session_state.last_error}")

# Display last error if any, at the bottom of the page
if st.session_state.last_error:
    st.error(f"**Last Recorded System Error:** {st.session_state.last_error}")

st.markdown("---")