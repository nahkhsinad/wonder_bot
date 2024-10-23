import streamlit as st
from openai import OpenAI
import time

# Page config
st.set_page_config(
    page_title="Wonderbot - Your Cement Expert",
    page_icon="https://www.wondercement.com/images/header/new_logo.png",
    layout="centered"
)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set the model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    # System prompt to define bot's behavior
    st.session_state.messages.append({
        "role": "system",
        "content": """You are Wonderbot, a knowledgeable and persuasive sales expert for Wonder Cement. 
        You have deep expertise in cement products and construction. Your key traits:
        - Professional yet friendly communication style
        - Deep understanding of cement products and their applications
        - Focus on customer needs before making recommendations
        - Use persuasive but ethical sales techniques
        - Highlight Wonder Cement's unique benefits
        
        Key products:
        1. Wonder PPC (Portland Pozzolana Cement)
        - Best for residential construction
        - High durability, sulfate resistant
        - Eco-friendly with optimal fly ash content
        - Compressive Strength: 53.50 MPa at 28 days

        2. Wonder Xtreme
        - Premium high-strength cement
        - Perfect for high-rise construction
        - Superior early strength
        - Compressive Strength: 60.00 MPa at 28 days

        3. Wonder Plus
        - Advanced formula with optimal fineness
        - Extensive coverage and superior bonding
        - Premium tamper-proof packaging
        - Ideal for infrastructure projects

        4. Wonder OPC (53 Grade)
        - High early strength
        - Excellent for heavy construction
        - Consistent quality
        - Compressive Strength: 60.00 MPa at 28 days
        
        Just as a new beta feature you may engage with the customer more personally like ask for their names and work in hypothetical scenarios like note their order and share a dummy order confirmation, using best of your knowledge to work as an interactive and smart sales chat bot named wonderbot for selling wonder cement products and use facts to arouse curiousity in the customer to know more and order.
        """
    })

# Title
st.title("🏗️ Wonderbot - Your Cement Expert")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help with your construction needs today?"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Stream the response
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} 
                         for m in st.session_state.messages],
                stream=True,
                temperature=0.7,
            )
            
            # Process the stream
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final response without cursor
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            full_response = "I apologize, but I'm having trouble connecting right now. Please try again or contact our sales team at 1800-180-6677."
            message_placeholder.markdown(full_response)
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a sidebar with company info
with st.sidebar:
    st.image("https://www.wondercement.com/images/header/new_logo.png",
             use_column_width=True)
    
    st.markdown("""
    ### Wonder Cement
    **Headquarters:** Udaipur, Rajasthan, India  
    **Production Capacity:** 18 MTPA
    
    #### Our Products:
    - Portland Pozzolana Cement (PPC)
    - Ordinary Portland Cement (OPC)
    - Wonder Plus (Premium Cement)
    - Wonder Xtreme
    
    *Ek Perfect Shuruaat*
    
    #### Contact Us:
    📞 1800-180-6677  
    📧 info@wondercement.com
    """)
