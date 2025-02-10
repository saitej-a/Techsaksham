import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

# Initialize chatbot class
class HealthcareChatbot:
    def __init__(self):
        self.greetings = ["hi", "hello", "hey", "good morning"]
        self.emergency_keywords = ["chest pain", "difficulty breathing", "severe bleeding", 
                                 "unconscious", "stroke", "heart attack"]
        self.symptom_responses = {
            "headache": "Headaches can be caused by tension, dehydration, or migraines. Stay hydrated and rest. If persistent, consult a doctor.",
            "fever": "Fever often indicates infection. Monitor temperature, stay hydrated. If over 103°F or lasting 3+ days, seek help.",
            "cough": "Coughs can be viral or allergic. Stay hydrated. If with fever/breathing issues, see a doctor.",
            "rash": "Rashes may be allergies/infections. Avoid scratching. Consult dermatologist if persists.",
        }
        self.medication_info = {
            "paracetamol": "Paracetamol: Pain/fever relief. Max 4000mg/day for adults. Consult doctor.",
            "ibuprofen": "Ibuprofen: NSAID for pain/inflammation. Take with food. Not for ulcers/kidney issues.",
            "antihistamine": "Antihistamines: Allergy relief. May cause drowsiness. Follow instructions.",
        }
        # self.disclaimer = "\n\n⚠️ I'm not a doctor. Always consult a healthcare professional."
        
        # Initialize DistilGPT2
        self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        self.model = AutoModelForCausalLM.from_pretrained("distilgpt2")
        self.chat_history_ids = None

    def generate_response(self, text):
        try:
            inputs = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')
            outputs = self.model.generate(
                inputs,
                max_length=200,
                pad_token_id=self.tokenizer.eos_token_id,
                temperature=0.7,
                no_repeat_ngram_size=2
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.split('\n')[0]
        except:
            return "I'm having trouble understanding. Could you rephrase?"

    def respond(self, message):
        message = message.lower()
        
        if any(re.search(rf'\b{kw}\b', message) for kw in self.emergency_keywords):
            return "🚨 EMERGENCY: Call local emergency services immediately!"
        
        if any(greeting in message for greeting in self.greetings):
            return f"Hello! I'm Sia, your health assistant. How can I help?"
            
        for symptom, response in self.symptom_responses.items():
            if re.search(rf'\b{symptom}\b', message):
                return response 
        
        for med, info in self.medication_info.items():
            if re.search(rf'\b{med}\b', message):
                return info
        
        if "exercise" in message:
            return f"Aim for 150 mins moderate exercise weekly."
        
        if "diet" in message:
            return f"Eat balanced meals with fruits, veggies, and whole grains."
        
        return self.generate_response(message)

# Streamlit UI
@st.cache_resource
def load_chatbot():
    return HealthcareChatbot()

def main():
    st.set_page_config(page_title="Health Assistant Sia", page_icon="⚕️")
    
    st.title("Health Assistant Sia")
    st.markdown("""
    <style>
    .css-1v0mbdj {max-width: 65%;}
    .user-message { border-radius: 10px; padding: 10px; margin: 5px 0;}
    .bot-message {border-radius: 10px; padding: 10px; margin: 5px 0;}
    </style>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm Sia. Ask me about health topics, symptoms, or general wellness advice."})

    chatbot = load_chatbot()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div class="{message["role"]}-message">{message["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Type your health question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

        with st.spinner("Getting your responce ready..."):
            response = chatbot.respond(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(f'<div class="bot-message">{response}</div>', unsafe_allow_html=True)

    st.sidebar.markdown("## About")
    st.sidebar.info("This AI health assistant provides general wellness information and should not be used as a substitute for professional medical advice.")

if __name__ == "__main__":
    main()