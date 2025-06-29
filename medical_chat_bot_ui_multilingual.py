import streamlit as st
import requests
import json
import os

# --- Configuration ---
# Your API key will be provided by the Canvas environment if left as an empty string.
# IMPORTANT: For Streamlit Cloud, remember to set this as a secret in your app settings.
# For local testing, ensure GEMINI_API_KEY is set in .streamlit/secrets.toml or as an environment variable.
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    API_KEY = os.getenv("GEMINI_API_KEY")
else:
    API_KEY = "" # Fallback for local dev if not set via env var or secrets; will cause 403 error without a key.
    st.error("API Key not found. Please set GEMINI_API_KEY in .streamlit/secrets.toml or as an environment variable.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="

# --- Language Definitions ---
LANGUAGE_MAP = {
    "English": {
        "model_instruction": "English",
        "greeting": "Hello! I'm your online Doctor. How can I help you today?",
        "disclaimer": "🚨 **Disclaimer:** I am an AI and cannot provide medical diagnoses, prescriptions, or professional medical advice. Always consult a qualified healthcare professional for any medical concerns.",
        "placeholder": "Ask your medical question here...",
        "thinking": "Thinking...",
        "api_error_response": "I'm sorry, I couldn't get a clear response from the medical assistant at this moment. Please try again.",
        "http_error": "I'm experiencing a problem connecting to the medical assistant. Please ensure your API key is correct.",
        "connection_error": "I couldn't connect to the internet. Please check your connection.",
        "timeout_error": "The request took too long. Please try again.",
        "unknown_error": "An unexpected error occurred while communicating. Please try again.",
        "json_error": "I received an unreadable response from the medical assistant. Please try again.",
        "api_key_missing": "Error: API Key is missing. Please configure it."
    },
    "Hindi": {
        "model_instruction": "Hindi",       
        "greeting": "नमस्ते! मैं आपका मेडिकल असिस्टेंट बॉट हूँ। मैं आज आपकी कैसे मदद कर सकता हूँ?",
        "disclaimer": "🚨: मैं एक AI हूँ और चिकित्सीय निदान, नुस्खे या पेशेवर चिकित्सीय सलाह प्रदान नहीं कर सकता। किसी भी चिकित्सीय चिंता के लिए हमेशा एक योग्य स्वास्थ्य पेशेवर से परामर्श करें।",
        "placeholder": "यहां अपना चिकित्सीय प्रश्न पूछें...",
        "thinking": "सोच रहा हूँ...",
        "api_error_response": "क्षमा करें, मुझे इस समय मेडिकल असिस्टेंट से स्पष्ट प्रतिक्रिया नहीं मिल पाई। कृपया पुनः प्रयास करें।",
        "http_error": "मुझे मेडिकल असिस्टेंट से कनेक्ट करने में समस्या आ रही है। कृपया सुनिश्चित करें कि आपकी API कुंजी सही है।",
        "connection_error": "मैं इंटरनेट से कनेक्ट नहीं हो सका। कृपया अपना इंटरनेट कनेक्शन जांचें।",
        "timeout_error": "अनुरोध में बहुत अधिक समय लगा। कृपया पुनः प्रयास करें।",
        "unknown_error": "संचार करते समय एक अप्रत्याशित त्रुटि हुई। कृपया पुनः प्रयास करें।",
        "json_error": "मुझे मेडिकल असिस्टेंट से एक अपठनीय प्रतिक्रिया मिली। कृपया पुनः प्रयास करें।",
        "api_key_missing": "त्रुटि: API कुंजी गुम है। कृपया इसे कॉन्फ़िगर करें।"
    },
    "Bengali": {
        "model_instruction": "Bengali",
        "greeting": "নমস্কার! আমি আপনার মেডিকেল অ্যাসিস্ট্যান্ট বট। আমি আজ আপনাকে কীভাবে সাহায্য করতে পারি?",
        "disclaimer": "🚨: আমি একটি AI এবং চিকিৎসার নির্ণয়, প্রেসক্রিপশন, বা পেশাদার চিকিৎসা পরামর্শ প্রদান করতে পারি না। যেকোনো চিকিৎসার জন্য সর্বদা একজন যোগ্য স্বাস্থ্যসেবা পেশাদারের সাথে পরামর্শ করুন।",
        "placeholder": "এখানে আপনার চিকিৎসা প্রশ্ন জিজ্ঞাসা করুন...",
        "thinking": "ভাবছি...",
        "api_error_response": "দুঃখিত, এই মুহূর্তে আমি মেডিকেল অ্যাসিস্ট্যান্টের কাছ থেকে স্পষ্ট প্রতিক্রিয়া পেতে পারিনি। অনুগ্রহ করে আবার চেষ্টা করুন।",
        "http_error": "মেডিকেল অ্যাসিস্ট্যান্টের সাথে সংযোগ করতে সমস্যা হচ্ছে। অনুগ্রহ করে নিশ্চিত করুন আপনার API কী সঠিক।",
        "connection_error": "আমি ইন্টারনেটের সাথে সংযোগ করতে পারিনি। অনুগ্রহ করে আপনার ইন্টারনেট সংযোগ পরীক্ষা করুন।",
        "timeout_error": "অনুরোধটি সম্পূর্ণ হতে অনেক বেশি সময় লেগেছে। অনুগ্রহ করে আবার চেষ্টা করুন।",
        "unknown_error": "যোগাযোগ করার সময় একটি অপ্রত্যাশিত ত্রুটি ঘটেছে। অনুগ্রহ করে আবার চেষ্টা করুন।",
        "json_error": "মেডিকেল অ্যাসিস্ট্যান্টের কাছ থেকে একটি অপাঠ্য প্রতিক্রিয়া পেয়েছি। অনুগ্রহ করে আবার চেষ্টা করুন।",
        "api_key_missing": "ত্রুটি: API কী অনুপস্থিত। অনুগ্রহ করে এটি কনফিগার করুন।"
    }
}

# --- System Prompt Generation ---
def get_system_prompt(language_code):
    """Generates the dynamic system prompt based on the selected language."""
    # The core prompt structure remains the same, but we instruct the model
    # to respond in the chosen language.
    return f"""
    You are a highly intelligent and compassionate Medical Assistant Bot. Your primary goal is to provide accurate, helpful, and context-specific medical guidance while always prioritizing user safety and advising professional consultation.
    The user will interact with you in {language_code}, and you **MUST** respond entirely in {language_code}. Also, you should try to understand the user's prompt even if it's in {language_code}.

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

# --- Chatbot Logic (adapted for Streamlit) ---

def call_gemini_api(messages_history, current_language_settings):
    """
    Calls the Gemini API with the given chat history.

    Args:
        messages_history (list): A list of messages for the Gemini API.
        current_language_settings (dict): Language-specific settings for error messages.

    Returns:
        str: The generated response from the Gemini model, or an error message.
    """
    if not API_KEY:
        return current_language_settings["api_key_missing"]

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
            st.error(f"Warning: Unexpected API response structure. Full response: {json.dumps(result, indent=2)}")
            return current_language_settings["api_error_response"]

    except requests.exceptions.HTTPError as e:
        st.error(f"An HTTP error occurred: {e}. Response: {e.response.text}")
        return current_language_settings["http_error"]
    except requests.exceptions.ConnectionError as e:
        st.error(f"A connection error occurred: {e}")
        return current_language_settings["connection_error"]
    except requests.exceptions.Timeout as e:
        st.error(f"The request timed out: {e}")
        return current_language_settings["timeout_error"]
    except requests.exceptions.RequestException as e:
        st.error(f"An unknown request error occurred: {e}")
        return current_language_settings["unknown_error"]
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse the response (JSON error): {e}. Raw response: {response.text if 'response' in locals() else 'No response'}")
        return current_language_settings["json_error"]


# --- Streamlit UI ---

# st.set_page_config(page_header="Online Doctor", page_icon="🩺", layout="centered")

# Initialize selected_language in session state
if "selected_language" not in st.session_state:
    st.session_state.selected_language = None

# Show language selection if not already selected
if st.session_state.selected_language is None:
    st.subheader("Welcome to your online Doctor:B.Chakraborty")
    st.write("Please select your preferred language:")

    # Using radio buttons for language selection
    selected_lang_display = st.radio(
        "Choose Language",
        list(LANGUAGE_MAP.keys()),
        index=0, # Default to English
        horizontal=True
    )

    if st.button("Start Chat"):
        st.session_state.selected_language = selected_lang_display
        # Initialize chat history with language-specific content
        st.session_state.messages = []
        # Add the system prompt first
        st.session_state.messages.append({"role": "user", "parts": [{"text": get_system_prompt(LANGUAGE_MAP[st.session_state.selected_language]["model_instruction"])}]})
        # Add the initial greeting from the model
        st.session_state.messages.append({"role": "model", "parts": [{"text": LANGUAGE_MAP[st.session_state.selected_language]["greeting"] + "\n\n" + LANGUAGE_MAP[st.session_state.selected_language]["disclaimer"]}]})
        st.rerun() # Rerun the app to show the chat interface
else:
    # Language is selected, display the chat interface
    current_lang_settings = LANGUAGE_MAP[st.session_state.selected_language]

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.subheader(f"🩺 Online Doctor Biswadeep ({st.session_state.selected_language})")
    with col2:
        if st.button("Change Language", key="change_lang_button"):
            st.session_state.selected_language = None
            st.session_state.messages = [] # Clear messages on language change
            st.rerun()

    st.write(current_lang_settings["disclaimer"])

    # Display chat messages from history on app rerun
    # We skip the very first message (the system prompt) when displaying to the user
    for message in st.session_state.messages[1:]: # Start from index 1 to skip the initial system prompt
        role_for_display = "assistant" if message["role"] == "model" else message["role"]
        with st.chat_message(role_for_display):
            st.markdown(message["parts"][0]["text"])

    # Accept user input
    if prompt := st.chat_input(current_lang_settings["placeholder"]):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner(current_lang_settings["thinking"]):
                # Pass the full conversation history to the API call
                full_conversation_for_api = [
                    {"role": msg["role"], "parts": msg["parts"]}
                    for msg in st.session_state.messages
                ]
                bot_response = call_gemini_api(full_conversation_for_api, current_lang_settings)
                st.markdown(bot_response)

        # Add bot response to chat history
        st.session_state.messages.append({"role": "model", "parts": [{"text": bot_response}]})

