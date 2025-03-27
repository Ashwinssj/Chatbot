

import google.generativeai as genai
import streamlit as st
import time
import random
from utils import SAFETY_SETTTINGS


st.set_page_config(
    page_title="Chat To XYthing",
    page_icon="🔥",
    menu_items={
        'About': "# Make By hiliuxg"
    }
)

st.title("Chat To XYthing")
st.caption("a chatbot, powered by google gemini pro.")


if "app_key" not in st.session_state:
    app_key = st.text_input("Your Gemini App Key", type='password')
    if app_key:
        st.session_state.app_key = app_key

if "history" not in st.session_state:
    st.session_state.history = []

try:
    genai.configure(api_key=st.session_state.app_key)
    model = genai.GenerativeModel(model_name='gemini-pro',
                                generation_config={
                                    'temperature': 0.9,
                                    'top_p': 1,
                                    'top_k': 1,
                                    'max_output_tokens': 2048,
                                })
    chat = model.start_chat(history=st.session_state.history,
                          generation_config=model.generation_config)
except AttributeError as e:
    st.warning("Please Put Your Gemini App Key First.")
    chat = None
except Exception as e:
    st.error(f"Error initializing Gemini: {str(e)}")
    chat = None

with st.sidebar:
    if st.button("Clear Chat Window", use_container_width = True, type="primary"):
        st.session_state.history = []
        st.rerun()

# Add check for chat initialization
if chat is not None:
    for message in chat.history:
        role = "assistant" if message.role == "model" else message.role
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        prompt = prompt.replace('\n', '  \n')
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                if chat is None:
                    st.error("Chat session not initialized. Please check your API key.")
                    return
                
                full_response = ""
                response = chat.send_message(prompt, 
                                          stream=True,
                                          safety_settings=SAFETY_SETTTINGS,
                                          generation_config=model.generation_config)
                for chunk in response:
                    word_count = 0
                    random_int = random.randint(5, 10)
                    for word in chunk.text:
                        full_response += word
                        word_count += 1
                        if word_count == random_int:
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "_")
                            word_count = 0
                            random_int = random.randint(5, 10)
                message_placeholder.markdown(full_response)
                # Only update history if chat is properly initialized
                if chat is not None:
                    st.session_state.history = chat.history
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
