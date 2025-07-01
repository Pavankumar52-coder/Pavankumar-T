# Import necessary libraries for backend
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager # Optional: for automatic driver management
import time, os
import google.generativeai as genai
from starlette.middleware.cors import CORSMiddleware
import dotenv

dotenv.load_dotenv()

# Load Gemini API Key using .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash") # Use gemini-1.5-flash or gemini-pro

# Start FastPAI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
screenshot_dir = os.path.join(BASE_DIR, "screenshots")
os.makedirs(screenshot_dir, exist_ok=True)
print(f"INFO: Screenshots will be saved in: {screenshot_dir}")

# Mount the directory to serve screenshots statically to ui
app.mount("/screenshots", StaticFiles(directory=screenshot_dir), name="screenshots")
print(f"INFO: Static files mounted from /screenshots to {screenshot_dir}")

class EmailRequest(BaseModel):
    prompt: str
    email: str
    password: str

# Function to generate email subject and body using the Gemini API and prompt
def generate_email(user_prompt: str):
    ai_prompt = f"""You are an AI assistant tasked with drafting a professional internship application email.
Based on the following user prompt, generate a suitable email.
User Prompt: "{user_prompt}"
Please provide the output in this exact format:
Subject: [Your suggested subject line]
Body:
[Your email body here, start with "Dear Hiring Team," or "To Whom It May Concern," and include a clear statement of interest in an internship at Insurebuzz AI.]
"""
    try:
        response = model.generate_content(ai_prompt)
        generated_text = response.text.strip()
        
        subject_line = "Internship Application to Insurebuzz"
        email_body = ""

        if "Subject:" in generated_text and "Body:" in generated_text:
            subject_start = generated_text.find("Subject:") + len("Subject:")
            body_start = generated_text.find("Body:") + len("Body:")

            subject_candidate = generated_text[subject_start:generated_text.find("Body:")].strip()
            if subject_candidate:
                subject_line = subject_candidate

            email_body = generated_text[body_start:].strip()
        else:
            email_body = generated_text
            
        if not email_body:
             email_body = f"Dear Hiring Team,\n\nI am writing to express my strong interest in an internship opportunity at Insurebuzz AI, as per your prompt: '{user_prompt}'. I am eager to learn and contribute to your team.\n\nSincerely,\n[Your Name]"

        print(f"DEBUG: Generated Subject: {subject_line}")
        print(f"DEBUG: Generated Body (first 100 chars): {email_body[:100]}...")
        return subject_line, email_body
    except Exception as e:
        print(f"ERROR: In Gemini API call or text generation: {e}")
        return "Internship Application - [AI Generation Failed]", \
               "Dear Hiring Team,\n\nI am writing to express my interest in an internship opportunity at Insurebuzz AI. There was an issue generating the email content via AI. Please consider this application.\n\nSincerely,\n[Your Name or Applicant]"

# Function to take a screenshot of the current browser state and save it
def take_screenshot(driver, name):
    filename = f"{name}.png"
    path = os.path.join(screenshot_dir, filename)
    try:
        driver.save_screenshot(path)
        print(f"DEBUG: Screenshot saved successfully to: {path}")
    except Exception as e:
        print(f"ERROR: Failed to save screenshot {filename} to {path}: {e}")
        # Consider a placeholder image if screenshot fails
    return filename

# API endpoint to send an email
@app.post("/send-email")
def send_email(req: EmailRequest):
    driver = None
    visual_feedback = [] 

    try:
        for f in os.listdir(screenshot_dir):
            if f.endswith(".png"):
                os.remove(os.path.join(screenshot_dir, f))
        print(f"DEBUG: Cleared old screenshots from {screenshot_dir}")

        subject, body = generate_email(req.prompt)

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--window-size=1920,1080") 
        try:
            driver_path = ChromeDriverManager().install()
            print(f"DEBUG: Chromedriver managed by webdriver_manager: {driver_path}")
        except Exception as e:
            print(f"WARNING: webdriver_manager failed. Falling back to hardcoded path. Error: {e}")
            driver_path = "C:/Users/pavan/Music/chromedriver-win64/chromedriver.exe" 
            print(f"DEBUG: Using hardcoded Chromedriver path: {driver_path}")

        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        wait = WebDriverWait(driver, 30)

        print("DEBUG: Step 1: Navigating to Gmail...")
        driver.get("https://mail.google.com")
        screenshot_name = take_screenshot(driver, "step_1_gmail_login_page")
        visual_feedback.append({"image": screenshot_name, "message": "Navigated to Gmail login page."})
        
        print("DEBUG: Step 2: Entering email address...")
        email_input_field = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        email_input_field.send_keys(req.email)
        
        email_next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        email_next_button.click()
        screenshot_name = take_screenshot(driver, "step_2_email_entered")
        visual_feedback.append({"image": screenshot_name, "message": "Entered email address and clicked Next."})

        print("DEBUG: Step 3: Entering password (handling potential challenges)...")
        try:
            password_input_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input_field.send_keys(req.password)
            password_next_button = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
            password_next_button.click()
            screenshot_name = take_screenshot(driver, "step_3_password_entered")
            visual_feedback.append({"image": screenshot_name, "message": "Entered password and clicked Next."})

        except Exception as e:
            print(f"ERROR: Could not find password field directly. Potential Gmail authentication challenge: {e}")
            screenshot_name = take_screenshot(driver, "step_3_gmail_auth_challenge")
            visual_feedback.append({"image": screenshot_name, "message": "Encountered a potential Gmail authentication challenge. This might require manual intervention (e.g., CAPTCHA, 2FA or 'Confirm it's you' screens). Automation might be blocked here."})
            raise Exception(f"Gmail authentication challenge detected or element not found: {e}. Please ensure your account does not have unusual security checks or try an App Password.")

        print("DEBUG: Step 4: Waiting for inbox to load...")
        compose_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Compose"]')))
        screenshot_name = take_screenshot(driver, "step_4_inbox_loaded")
        visual_feedback.append({"image": screenshot_name, "message": "Successfully logged in; Gmail inbox loaded."})

        print("DEBUG: Step 5: Clicking Compose button...")
        compose_button.click()
        screenshot_name = take_screenshot(driver, "step_5_compose_clicked")
        visual_feedback.append({"image": screenshot_name, "message": "Clicked the 'Compose' button."})

        print("DEBUG: Step 6: Filling in email details...")
        to_input = wait.until(EC.presence_of_element_located((By.NAME, 'to')))
        to_input.send_keys("reportinsurebuzz@gmail.com")

        subject_input = wait.until(EC.presence_of_element_located((By.NAME, 'subjectbox')))
        subject_input.send_keys(subject)

        body_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Message Body']")))
        body_input.send_keys(body)
        
        screenshot_name = take_screenshot(driver, "step_6_email_filled")
        visual_feedback.append({"image": screenshot_name, "message": "Email recipient, subject, and body filled."})

        print("DEBUG: Step 7: Sending the email...")
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Send"]')))
        send_button.click()
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[contains(text(), "Sending...")]')))
            print("DEBUG: 'Sending...' message disappeared.")
        except:
            print("WARNING: 'Sending...' message did not disappear or was not found.")
        time.sleep(2) 
        screenshot_name = take_screenshot(driver, "step_7_email_sent_confirmation")
        visual_feedback.append({"image": screenshot_name, "message": "Email sent successfully!"})
        
        print("DEBUG: Automation completed successfully.")
        return JSONResponse(status_code=200, content={
            "status": "✅ Email Automation Completed!", 
            "visual_feedback": visual_feedback 
        })

    except Exception as e:
        print(f"ERROR: During automation: {str(e)}")
        if driver:
            error_screenshot_name = take_screenshot(driver, "error_final_state")
            visual_feedback.append({"image": error_screenshot_name, "message": f"Automation failed at this stage: {str(e)}"})
        
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "visual_feedback": visual_feedback 
        })
    finally:
        if driver:
            driver.quit()

# Root endpoint to check if the backend is running
@app.get("/")
def read_root():
    return {"message": "FastAPI Gmail Automation Agent Backend is running."}