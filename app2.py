# # # import streamlit as st
# # # import google.generativeai as genai
# # # from dotenv import load_dotenv
# # # import os
# # # import json
# # # import time
# # # from datetime import datetime
# # #
# # # #  Updated Rasa imports for 3.6.21 compatibility
# # # from rasa.core.interpreter import RasaNLUInterpreter
# # # from rasa.model import get_model
# # #
# # # # Load environment variables and configure Gemini
# # # load_dotenv()
# # # genai.configure(api_key=os.getenv("API_KEY"))
# # # gen_ai_model = genai.GenerativeModel("gemini-1.5-flash")
# # #
# # # #  Load the latest Rasa trained model (.tar.gz inside /models)
# # # model_path = "models/nlu-20250620-121753-late-practice.tar.gz"  # Automatically gets latest model
# # # interpreter = RasaNLUInterpreter(model_path)
# # #
# # # #  Load FAQ intents and answers
# # # with open("faq.json", "r") as f:
# # #     faq_data = json.load(f)["intents"]
# # #
# # # #  Logging user interactions
# # # def log_interaction(prompt, response, source):
# # #     log = {
# # #         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# # #         "prompt": prompt,
# # #         "response": response,
# # #         "source": source
# # #     }
# # #     if os.path.exists("logs/chat_logs.json"):
# # #         with open("logs/chat_logs.json", "r") as file:
# # #             data = json.load(file)
# # #     else:
# # #         data = []
# # #     data.append(log)
# # #     with open("logs/chat_logs.json", "w") as file:
# # #         json.dump(data, file, indent=4)
# # #
# # # #  Simulate typing animation
# # # def stream_data(text):
# # #     for word in text.split(" "):
# # #         yield word + " "
# # #         time.sleep(0.02)
# # #
# # # #  Handle intent + fallback logic
# # # def get_response(prompt):
# # #     result = interpreter.parse(prompt)
# # #     intent = result["intent"]["name"]
# # #     confidence = result["intent"]["confidence"]
# # #
# # #     if confidence > 0.7:
# # #         for item in faq_data:
# # #             if item.get("intent") == intent:
# # #                 log_interaction(prompt, item["answer"], f"FAQ ({intent})")
# # #                 return item["answer"]
# # #
# # #     #  Gemini fallback
# # #     response = gen_ai_model.generate_content(
# # #         f"You are a Smart Academy expert. Only respond if sure.\nQuestion: {prompt}"
# # #     ).text.strip()
# # #
# # #     # Escalation condition
# # #     if len(response) < 30 or any(kw in response.lower() for kw in ["i don't know", "please visit", "unfortunately"]):
# # #         fallback = (
# # #             "I'm not confident I can help with that.\n\n"
# # #             "📞 Contact Smart Academy Support:\n"
# # #             "- Phone: +254 712 345 678\n- Email: support@smartacademy.go.ke"
# # #         )
# # #         log_interaction(prompt, fallback, "Escalation")
# # #         return fallback
# # #
# # #     log_interaction(prompt, response, "Gemini")
# # #     return response
# # #
# # # #  Streamlit UI setup
# # # st.set_page_config(page_title="Smart Academy Chatbot", page_icon="📝")
# # # st.title("🧠 Smart Academy Assistant")
# # #
# # # if "messages" not in st.session_state:
# # #     st.session_state.messages = [
# # #         {"role": "assistant", "content": "Hello 👋, how may I help you today?"}
# # #     ]
# # #
# # # # Show chat history
# # # for msg in st.session_state.messages:
# # #     with st.chat_message(msg["role"]):
# # #         st.markdown(msg["content"])
# # #
# # # # Input prompt
# # # if prompt := st.chat_input("Ask me anything about Smart Academy..."):
# # #     st.session_state.messages.append({"role": "user", "content": prompt})
# # #     with st.chat_message("user"):
# # #         st.markdown(prompt)
# # #
# # #     with st.chat_message("assistant"):
# # #         response = get_response(prompt)
# # #         st.write_stream(stream_data(response))
# # #         st.session_state.messages.append({"role": "assistant", "content": response})
# #
# #
# #
# # _____________________________________________________________________________________________________
# #
# # import streamlit as st
# # import google.generativeai as genai
# # from dotenv import load_dotenv
# # import os
# # import json
# # import time
# # from datetime import datetime
# # import requests  # For calling Rasa REST API
# #
# # # Load environment and Gemini
# # load_dotenv()
# # genai.configure(api_key=os.getenv("API_KEY"))
# # gen_ai_model = genai.GenerativeModel("gemini-1.5-flash")
# #
# # # Rasa REST endpoint
# # RASA_NLU_ENDPOINT = "http://localhost:5005/model/parse"
# #
# # # Load FAQ data
# # with open("faq.json", "r") as f:
# #     faq_data = json.load(f)["intents"]
# #
# # # Log interaction to file
# # def log_interaction(prompt, response, source):
# #     log = {
# #         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #         "prompt": prompt,
# #         "response": response,
# #         "source": source
# #     }
# #     os.makedirs("logs", exist_ok=True)
# #     if os.path.exists("logs/chat_logs.json"):
# #         with open("logs/chat_logs.json", "r") as file:
# #             data = json.load(file)
# #     else:
# #         data = []
# #     data.append(log)
# #     with open("logs/chat_logs.json", "w") as file:
# #         json.dump(data, file, indent=4)
# #
# # # text streaming
# # def stream_data(text):
# #     for word in text.split(" "):
# #         yield word + " "
# #         time.sleep(0.02)
# #
# # # Get intent and response
# # def get_response(prompt):
# #     try:
# #         rasa_response = requests.post(
# #             RASA_NLU_ENDPOINT,
# #             json={"text": prompt},
# #             timeout=5
# #         ).json()
# #
# #         intent = rasa_response.get("intent", {}).get("name")
# #         confidence = rasa_response.get("intent", {}).get("confidence", 0)
# #
# #         if confidence > 0.7:
# #             for item in faq_data:
# #                 if item.get("intent") == intent:
# #                     log_interaction(prompt, item["answer"], f"FAQ ({intent})")
# #                     return item["answer"]
# #
# #     except Exception as e:
# #         print("Rasa error:", e)
# #
# #     # Fallback to Gemini
# #     response = gen_ai_model.generate_content(
# #         f"You are a Smart Academy expert. Only respond if sure.\nQuestion: {prompt}"
# #     ).text.strip()
# #
# #     # Escalation fallback
# #     if len(response) < 30 or any(kw in response.lower() for kw in ["i don't know", "please visit", "unfortunately"]):
# #         fallback = (
# #             "I'm not confident I can help with that.\n\n"
# #             "📞 Contact Smart Academy Support:\n"
# #             "- Phone: +254 712 345 678\n- Email: support@smartacademy.go.ke"
# #         )
# #         log_interaction(prompt, fallback, "Escalation")
# #         return fallback
# #
# #     log_interaction(prompt, response, "Gemini")
# #     return response
# #
# # # Streamlit UI
# # st.set_page_config(page_title="Smart Academy Chatbot", page_icon="📝")
# # st.title("🧠 Smart Academy Assistant")
# #
# # if "messages" not in st.session_state:
# #     st.session_state.messages = [
# #         {"role": "assistant", "content": "Hello 👋, how may I help you today?"}
# #     ]
# #
# # for msg in st.session_state.messages:
# #     with st.chat_message(msg["role"]):
# #         st.markdown(msg["content"])
# #
# # if prompt := st.chat_input("Ask me anything about Smart Academy..."):
# #     st.session_state.messages.append({"role": "user", "content": prompt})
# #     with st.chat_message("user"):
# #         st.markdown(prompt)
# #
# #     with st.chat_message("assistant"):
# #         response = get_response(prompt)
# #         st.write_stream(stream_data(response))
# #         st.session_state.messages.append({"role": "assistant", "content": response})
#
# import streamlit as st
# import requests
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# import json
# import time
# from datetime import datetime
# from sentence_transformers import SentenceTransformer, util
# from functools import lru_cache
# import spacy
#
# # Load spaCy for keyword extraction
# nlp = spacy.load("en_core_web_sm")
#
# # Load environment and Gemini
# load_dotenv()
# genai.configure(api_key=os.getenv("API_KEY"))
# encoder = SentenceTransformer("all-MiniLM-L6-v2")
#
# RASA_NLU_ENDPOINT = "http://localhost:5005/model/parse"
#
# # --- Preprocess and cache embedding ---
# def clean_text(text):
#     return text.strip().lower().replace("?", "").replace(".", "")
#
# @lru_cache(maxsize=1000)
# def get_cached_embedding(text):
#     return encoder.encode(text, convert_to_tensor=True)
#
# # ✅ Extract keywords using spaCy
# def extract_keywords(text):
#     doc = nlp(text.lower())
#     keywords = set()
#
#     for chunk in doc.noun_chunks:
#         if len(chunk.text.strip()) > 2:
#             keywords.add(chunk.text.strip())
#
#     for token in doc:
#         if token.pos_ in ["NOUN", "PROPN", "ADJ"] and len(token.text) > 2:
#             keywords.add(token.text.strip())
#
#     return keywords
#
# # Load FAQ and cache embeddings
# faq_data = []
# question_bank = []
# try:
#     with open("faq2.json", "r") as f:
#         faq_data = json.load(f)["intents"]
#         for item in faq_data:
#             for q in item.get("questions", []):
#                 vec = get_cached_embedding(clean_text(q))
#                 question_bank.append((vec, q, item["answer"]))
# except Exception as e:
#     print("❌ Error loading FAQ:", e)
#
# # Logging
# def log_interaction(prompt, response, source):
#     log = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "prompt": prompt,
#         "response": response,
#         "source": source
#     }
#     os.makedirs("logs", exist_ok=True)
#     logs_path = "logs/chat_logs.json"
#     data = []
#     if os.path.exists(logs_path):
#         with open(logs_path, "r") as file:
#             data = json.load(file)
#     data.append(log)
#     with open(logs_path, "w") as file:
#         json.dump(data, file, indent=4)
#
# # Typing animation
# def stream_data(text):
#     for word in text.split(" "):
#         yield word + " "
#         time.sleep(0.005)
#
# # Matching multiple answers based on extracted keywords
# def get_multi_match(prompt):
#     query_vec = get_cached_embedding(clean_text(prompt))
#     keywords = extract_keywords(prompt)
#     matches = []
#
#     for vec, q, answer in question_bank:
#         score = util.cos_sim(query_vec, vec).item()
#         if score > 0.65 and any(kw in clean_text(q) for kw in keywords):
#             matches.append((score, answer))
#
#     matches = sorted(matches, reverse=True)
#     seen = set()
#     responses = []
#     for _, ans in matches:
#         if ans not in seen:
#             responses.append(ans)
#             seen.add(ans)
#         if len(responses) == 3:
#             break
#
#     return "\n\n".join(f"✅ {r}" for r in responses) if responses else None
#
# # Main logic
# def get_response(prompt):
#     cleaned = clean_text(prompt)
#
#     try:
#         rasa_response = requests.post(
#             RASA_NLU_ENDPOINT,
#             json={"text": cleaned},
#             timeout=5
#         ).json()
#
#         intent = rasa_response.get("intent", {}).get("name")
#         confidence = rasa_response.get("intent", {}).get("confidence", 0)
#
#         if confidence > 0.7:
#             for item in faq_data:
#                 title_match = item.get("title", "").lower().replace(" ", "_") == intent
#                 tag_match = intent in [tag.lower().replace(" ", "_") for tag in item.get("tags", [])]
#                 if title_match or tag_match:
#                     log_interaction(prompt, item["answer"], f"FAQ ({intent})")
#                     return item["answer"]
#     except Exception as e:
#         print("❌ Rasa error:", e)
#
#     answer = get_multi_match(prompt)
#     if answer:
#         log_interaction(prompt, answer, "Semantic Multi-Match")
#         return answer
#
#     fallback = (
#         "I'm not confident I can help with that. Please reach out to an agent.\n\n"
#         "📞 Smart Academy Support:\n"
#         "- Phone: +254 712 345 678\n"
#         "- Email: support@smartacademy.go.ke\n"
#         "- Website: https://smartacademy.go.ke"
#     )
#     log_interaction(prompt, fallback, "Escalation")
#     return fallback
#
# # Streamlit UI
# st.set_page_config(page_title="Smart Academy Chatbot", page_icon="🧠")
# st.title("🧠 Smart Academy Assistant")
#
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello 👋, how may I assist you today?"}
#     ]
#
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#
# if prompt := st.chat_input("Ask me anything about Smart Academy..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)
#
#     with st.chat_message("assistant"):
#         response = get_response(prompt)
#         st.write_stream(stream_data(response))
#         st.session_state.messages.append({"role": "assistant", "content": response})
