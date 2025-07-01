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
