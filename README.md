# Chat-Based Gmail Automation Agent

## Overview:
This project overview is a chat-based AI agent that automates the process of sending an application via Gmail. The agent takes a natural prompt, logs into Gmail using browser automation and login credentials of user, generates the email using Gemini AI, and sends it — all while showing visual feedback.

---

## Tech Stack:
- **Frontend:** Streamlit (Chat UI + Screenshot Display)
- **Backend:** FastAPI
- **Automation:** Selenium WebDriver
- **AI Model:** Gemini (Google Generative AI)
- **Others:** WebDriverManager, dotenv

---

## Architecture & Flow:

User sends a prompt
       |
       V
  Streamlit Chat 
       |
       V
   FastAPI 
      |
      V
   Gemini AI
     |
     V
  Selenium
     |
     V
Gmail UI + Screenshots

---

## Gmail Auth Handling:

Gmail blocks headless/automated logins with 2FA, CAPTCHA, and security prompts. To handle this:

- For this i used a real Chrome browser with visible UI (headed).
- Screenshots are taken at every step to simulate live feedback.
- If Gmail blocks login, user is advised to manually log in the browser.

---

## Gmail Automation Challenge:
1. Due to google restricted policy gmail has stopped my selenium anti-bot to login with my credentials.
2. There are 3 ways to get this challenge done:
   a. We can use smtp to send mail to to given receipient address using gemini llm.(not required)
   b. One more way is that  we can use manual login with login credentials or handling recaptcha using automation logic or we can use trusted browser.
   c. One more way is that we can use GCP and google cloud studio to avoid blockings of selenium driver which is a complex way which requires premium account.

## Setup Instructions:

1. Clone the repo.
2. Install all dependencies which are required.

## Run Instructions:
1. After cloning the github repo please install all dependencies.
2. Now first run FastAPI.
3. Secondly run Streamlit ui file to interact with the chatbot.
4. You can copy and paste the given url to interact with the chatbot.

## Prompts:
  All prompts are included in the code files itself along with screenshots.
