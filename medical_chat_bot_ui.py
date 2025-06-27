import streamlit as st
import requests
import json
import os

# --- Configuration ---
# IMPORTANT: DO NOT hardcode your API key directly in production code.
# For Streamlit, the recommended way is to use Streamlit Secrets.
# Create a .streamlit/secrets.toml file in your project root with:
# GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY"
# Then access it via st.secrets["GEMINI_API_KEY"]
# For local testing, you can set it as an environment variable (e.g., in your terminal before running streamlit)
# export GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY" (Linux/macOS)
# set GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY (Windows cmd)

# Try to get API key from Streamlit secrets, then environment variable, then fallback
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"] # CORRECTED LINE: Access by key name "GEMINI_API_KEY"
elif os.getenv("GEMINI_API_KEY"):
    API_KEY = os.getenv("GEMINI_API_KEY")
else:
    API_KEY = "" # Fallback for local dev if not set via env var or secrets; will likely cause 403 error without a key.
    st.error("API Key not found. Please set GEMINI_API_KEY in .streamlit/secrets.toml or as an environment variable.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="

# --- Chatbot Logic (adapted for Streamlit) ---

def call_gemini_api(messages_history):
    """
    Calls the Gemini API with the given chat history.

    Args:
        messages_history (list): A list of messages in the format
                                 [{'role': 'user', 'parts': [{text: '...'}]},
                                  {'role': 'model', 'parts': [{text: '...'}]}]
                                 This list should already contain the system prompt.

    Returns:
        str: The generated response from the Gemini model, or an error message.
    """
    if not API_KEY:
        return "Error: API Key is missing. Please configure it."

    payload = {
        "contents": messages_history
    }

    try:
        response = requests.post(
            f"{API_URL}{API_KEY}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           result["candidates"][0]["content"]["parts"][0].get("text"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # More detailed error logging for debugging
            st.error(f"Warning: Unexpected API response structure. Full response: {json.dumps(result, indent=2)}")
            return "I'm sorry, I couldn't get a clear response from the medical assistant at this moment. Please try again."

    except requests.exceptions.HTTPError as e:
        error_msg = f"An HTTP error occurred: {e}. Response: {e.response.text}"
        st.error(error_msg)
        return "I'm experiencing a problem connecting to the medical assistant. Please ensure your API key is correct."
    except requests.exceptions.ConnectionError as e:
        error_msg = f"A connection error occurred: {e}. Please check your internet connection."
        st.error(error_msg)
        return "I couldn't connect to the internet. Please check your connection."
    except requests.exceptions.Timeout as e:
        error_msg = f"The request timed out: {e}. The medical assistant might be busy."
        st.error(error_msg)
        return "The request took too long. Please try again."
    except requests.exceptions.RequestException as e:
        error_msg = f"An unknown request error occurred: {e}."
        st.error(error_msg)
        return "An unexpected error occurred while communicating. Please try again."
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse the medical assistant's response (JSON error): {e}. Raw response: {response.text if 'response' in locals() else 'No response'}"
        st.error(error_msg)
        return "I received an unreadable response from the medical assistant. Please try again."

# --- Streamlit UI ---

st.set_page_config(page_title="Medical Assistant Bot", page_icon="??")
st.title("?? Medical Assistant Bot")
st.write("Hello! I'm your Medical Assistant Bot. I can provide general health information and specialized advice.")
st.warning("?? **Disclaimer:** I am an AI and cannot provide medical diagnoses, prescriptions, or professional medical advice. Always consult a qualified healthcare professional for any medical concerns.")


# System prompt (crucial for role switching and behavior)
SYSTEM_PROMPT = """
You are a highly intelligent and compassionate Medical Assistant Bot. Your primary goal is to provide accurate, helpful, and context-specific medical guidance while always prioritizing user safety and advising professional consultation.

You operate in two modes:

1.  **General Medical Assistant**:
    * **Purpose**: To address common health concerns, provide general well-being advice, offer preliminary information about mild symptoms, and answer simple health-related inquiries.
    * **Tone**: Friendly, informative, and reassuring.
    * **Examples**: "What are good ways to stay hydrated?", "I have a common cold, what can I do?", "What's the recommended daily intake of Vitamin C?"

2.  **Specialist Medical Advisor**:
    * **Purpose**: To handle advanced, complex, or highly specific medical queries requiring in-depth knowledge in a particular medical field (e.g., cardiology, neurology, oncology, pharmacology). This mode is triggered by detailed symptom descriptions, questions about specific diseases, drug interactions, or when the user explicitly asks for specialist advice.
    * **Tone**: Professional, precise, and highly detailed.
    * **Examples**: "I have persistent chest pain radiating to my left arm and shortness of breath, what could be the possible causes?", "Tell me about the latest non-surgical treatments for spinal stenosis.", "What are the contraindications for patients with kidney disease taking Metformin?", "Can you explain the mechanism of action of SSRIs?"

**Instructions for Dynamic Role Switching:**

* **Default Mode**: Begin every conversation implicitly as a **General Medical Assistant**.
* **Switching to Specialist**: Analyze the user's query for keywords, detail, and complexity. If the query is detailed, highly specific, involves complex medical terminology, discusses severe symptoms, asks about specific diseases, drug interactions, or requests in-depth medical analysis, **switch to Specialist Medical Advisor mode for that response.**
* **Acknowledging Specialist Mode**: When you switch to and respond as a **Specialist Medical Advisor**, explicitly state it at the beginning of your response. For example: "As a Specialist Medical Advisor, based on your description,..." or "In my capacity as a Specialist Medical Advisor, I can explain that..."
* **Always Disclaim**: Regardless of the mode, **ALWAYS** include a disclaimer at the end of every response reminding the user that you are an AI and cannot provide professional medical diagnosis or treatment. **Strongly advise them to consult a qualified healthcare professional for any medical concerns.**
* **Maintain Context**: Use the chat history to understand the ongoing conversation and provide relevant follow-up.
* **Clarity and Brevity**: Provide clear, concise, and easy-to-understand information. Avoid medical jargon where simpler terms suffice, but use precise terminology when acting as a specialist.
* **Ethical Boundaries**: Never give a definitive diagnosis, prescribe medication, or tell the user to stop taking medication. Never encourage self-treatment for serious conditions.
"""

# Initialize chat history in Streamlit's session state
# This is crucial for maintaining conversation across reruns of the script
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the system prompt as the first message from the "user" role for the model's context
    # followed by an initial message from the "model" for the user.
    st.session_state.messages.append({"role": "user", "parts": [{"text": SYSTEM_PROMPT}]})
    st.session_state.messages.append({"role": "model", "parts": [{"text": "Hello! I'm your Medical Assistant Bot. How can I help you today?"}]})


# Display chat messages from history on app rerun
# We skip the very first message (the system prompt) when displaying to the user
for message in st.session_state.messages[1:]: # Start from index 1 to skip the initial system prompt
    # Streamlit's chat_message supports 'user' and 'assistant' roles
    # We map 'model' role from Gemini to 'assistant' for display
    role_for_display = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role_for_display):
        st.markdown(message["parts"][0]["text"])

# Accept user input
if prompt := st.chat_input("Ask your medical question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass the full conversation history to the API call
            full_conversation_for_api = [
                {"role": msg["role"], "parts": msg["parts"]}
                for msg in st.session_state.messages
            ]
            bot_response = call_gemini_api(full_conversation_for_api)
            st.markdown(bot_response)

    # Add bot response to chat history
    st.session_state.messages.append({"role": "model", "parts": [{"text": bot_response}]})
