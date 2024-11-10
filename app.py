import streamlit as st
from openai import OpenAI
import pandas as pd
import base64
from PIL import Image
import io
import os
import time

# Page config
st.set_page_config(
    page_title="Wonderbot - Your Complete Construction Partner",
    page_icon="🏗️",
    layout="wide"
)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session states
if "chat_model" not in st.session_state:
    st.session_state["chat_model"] = "gpt-4-turbo-preview"
if "vision_model" not in st.session_state:
    st.session_state["vision_model"] = "gpt-4o-mini"
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "profession": None,
        "contact": None,
        "project_type": None
    }
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system",
        "content": """You are Wonderbot, a knowledgeable and friendly construction expert. 
        Start by warmly greeting the user and asking for their name if not already known.
        Then naturally progress to understanding their profession and construction needs.
        
        Key traits:
        - Warm and professional tone
        - Ask one question at a time
        - Remember user details and reference them
        - Provide product suggestions based on their needs
        
        Products:
        1. Wonder PPC (Portland Pozzolana Cement)
        - Best for residential construction
        - High durability, sulfate resistant
        - Eco-friendly with optimal fly ash content
        
        2. Wonder Xtreme
        - Premium high-strength cement
        - Perfect for high-rise construction
        - Superior early strength
        
        3. Wonder Plus
        - Advanced formula with optimal fineness
        - Extensive coverage and superior bonding
        - Premium tamper-proof packaging
        
        4. Wonder OPC (53 Grade)
        - High early strength
        - Excellent for heavy construction
        - Consistent quality
        
        Remember to highlight benefits naturally in conversation:
        - Personalized recommendations
        - Project-specific insights
        - Technical support
        - Special offers for registered users
        """
    })

def encode_image(image_file):
    try:
        return base64.b64encode(image_file.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"Error encoding image: {str(e)}")
        return None

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat with Wonderbot", 
    "🎨 Design Analysis & Visualization",
    "🧮 Project Calculator",
    "🏛️ Vastu Guide"
])

# Tab 1: Main Chat Interface
with tab1:
    st.title("🏗️ Wonderbot - Your Cement Expert")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("How can I help with your construction needs today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["chat_model"],
                    messages=[{"role": m["role"], "content": m["content"]} 
                             for m in st.session_state.messages],
                    stream=True,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Chat error: {str(e)}")
                full_response = "I apologize, but I'm having trouble connecting. Please try again."
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# Tab 2: Design Analysis & Visualization
with tab2:
    st.title("Design Analysis & Visualization")
    
    analysis_option = st.radio(
        "Choose an option:",
        ["📋 Analyze Existing Design", "🎨 Generate Design Visualization"]
    )
    
    if analysis_option == "📋 Analyze Existing Design":
        uploaded_file = st.file_uploader(
            "Upload your design (JPG, PNG)", 
            type=['jpg', 'jpeg', 'png']
        )
        
        if uploaded_file:
            # Show image preview
            st.image(uploaded_file, caption="Uploaded Design", use_column_width=True)
            
            if st.button("Analyze Design"):
                with st.spinner("Analyzing your design..."):
                    try:
                        # Encode image
                        base64_image = encode_image(uploaded_file)
                        
                        if base64_image:
                            response = client.chat.completions.create(
                                model=st.session_state["vision_model"],
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": """Analyze this construction design and provide insights about:
                                                1. Overall Design Assessment
                                                2. Material Requirements
                                                3. Structural Considerations
                                                4. Suggested Improvements
                                                5. Wonder Cement Product Recommendations"""
                                            },
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                max_tokens=500
                            )
                            
                            analysis = response.choices[0].message.content
                            
                            # Display analysis
                            st.success("Analysis Complete!")
                            st.markdown("### Design Analysis Results")
                            st.markdown(analysis)
                            
                            # Action items
                            with st.expander("📋 Recommended Next Steps"):
                                st.write("Based on this analysis, we recommend:")
                                st.write("1. Schedule a consultation with our experts")
                                st.write("2. Get a detailed material estimate")
                                st.write("3. Discuss bulk pricing options")
                                if st.button("Contact Sales Team"):
                                    st.info("📞 Call 1800-180-6677 for immediate assistance")
                                    
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
                        st.info("Please try a different image or contact support.")

    else:
        st.write("✨ Let AI visualize your construction design ideas!")
        design_prompt = st.text_area(
            "Describe your design vision:",
            height=100,
            placeholder="Example: A modern two-story house with large windows and an open floor plan..."
        )
        
        if st.button("Generate Design") and design_prompt:
            with st.spinner("Creating your design visualization..."):
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=f"Professional architectural visualization: {design_prompt}. Photorealistic, detailed architectural rendering, modern construction style.",
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    st.image(response.data[0].url, caption="Generated Design")
                    
                    # Add helpful next steps
                    st.success("Design generated successfully!")
                    st.markdown("### Would you like to:")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Get Material Estimate"):
                            st.switch_tab("Project Calculator")
                    with col2:
                        if st.button("Discuss with Expert"):
                            st.switch_tab("Chat with Wonderbot")
                            
                except Exception as e:
                    st.error(f"Image generation error: {str(e)}")

# Tab 3: Project Calculator
with tab3:
    st.title("Project Calculator")
    
    # Project details collection
    col1, col2 = st.columns(2)
    
    with col1:
        project_type = st.selectbox(
            "Project Type",
            ["Residential", "Commercial", "Industrial", "Infrastructure"]
        )
        floors = st.number_input("Number of Floors", min_value=1, value=1)
        
    with col2:
        total_area = st.number_input(
            "Total Construction Area (sq ft)",
            min_value=100,
            value=1000
        )
        construction_type = st.selectbox(
            "Construction Type",
            ["Basic", "Premium", "Luxury"]
        )
    
    if st.button("Calculate Requirements"):
        with st.spinner("Calculating..."):
            # Basic calculation logic
            cement_per_sqft = {
                "Basic": 0.35,
                "Premium": 0.40,
                "Luxury": 0.45
            }[construction_type]
            
            total_cement = total_area * floors * cement_per_sqft
            
            # Display results in tabs
            result_tab1, result_tab2 = st.tabs(["Material Requirements", "Timeline"])
            
            with result_tab1:
                st.markdown("### Estimated Material Requirements")
                
                materials_df = pd.DataFrame({
                    'Material': [
                        'Wonder PPC Cement',
                        'Sand',
                        'Aggregate',
                        'Steel',
                        'Bricks'
                    ],
                    'Quantity': [
                        f"{total_cement:.0f} bags",
                        f"{total_cement*4.5:.0f} cubic ft",
                        f"{total_cement*6.5:.0f} cubic ft",
                        f"{total_area*0.006*floors:.0f} tons",
                        f"{total_area*8*floors:.0f} pieces"
                    ],
                    'Estimated Cost (₹)': [
                        f"{total_cement*350:,.0f}",
                        f"{total_cement*4.5*30:,.0f}",
                        f"{total_cement*6.5*35:,.0f}",
                        f"{total_area*0.006*floors*58000:,.0f}",
                        f"{total_area*8*floors*8:,.0f}"
                    ]
                })
                
                st.dataframe(materials_df, use_container_width=True)
                
            with result_tab2:
                st.markdown("### Project Timeline")
                
                timeline_df = pd.DataFrame({
                    'Phase': [
                        'Foundation',
                        'Structure',
                        'Finishing',
                        'Completion'
                    ],
                    'Duration (weeks)': [4, 12, 8, 2],
                    'Cement Required (bags)': [
                        f"{total_cement*0.3:.0f}",
                        f"{total_cement*0.4:.0f}",
                        f"{total_cement*0.3:.0f}",
                        "N/A"
                    ]
                })
                
                st.dataframe(timeline_df, use_container_width=True)

# Tab 4: Vastu Guide
with tab4:
    st.title("Vastu Guide")
    
    st.write("""
    ### Quick Vastu Consultation
    Select the area you'd like Vastu guidance for:
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        vastu_area = st.selectbox(
            "Choose area:",
            ["Main Entrance", "Kitchen", "Bedroom", "Living Room", 
             "Bathroom", "Study Room", "Construction Material Storage"]
        )
    
    if vastu_area:
        with st.spinner("Getting Vastu recommendations..."):
            try:
                response = client.chat.completions.create(
                    model=st.session_state["chat_model"],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a Vastu expert. Provide practical Vastu advice with reasoning."
                        },
                        {
                            "role": "user",
                            "content": f"Provide Vastu guidelines for {vastu_area}, including direction, placement, and material considerations."
                        }
                    ]
                )
                
                # Display the response in a structured way
                st.markdown("### Vastu Guidelines")
                st.markdown(response.choices[0].message.content)
                
                # Add helpful resources
                with st.expander("📚 Additional Resources"):
                    st.markdown("""
                    - Schedule a detailed Vastu consultation
                    - Download Vastu guidelines PDF
                    - Connect with our Vastu experts
                    """)
                    
            except Exception as e:
                st.error(f"Error fetching Vastu guidance: {str(e)}")

# Sidebar
with st.sidebar:
    st.title("Wonder Cement")
    
    # User info display
    if st.session_state.user_info["name"]:
        st.success(f"Welcome, {st.session_state.user_info['name']}!")
        if st.session_state.user_info["profession"]:
            st.write(f"Profession: {st.session_state.user_info['profession']}")
        if st.session_state.user_info["project_type"]:
            st.write(f"Project Interest: {st.session_state.user_info['project_type']}")
    
    st.markdown("""
    ### Quick Links
    - 📞 Helpline: 1800-180-6677
    - 📧 Email: info@wondercement.com
    
    ### Our Products
    1. **Wonder PPC**
       - Residential construction
       - High durability
    
    2. **Wonder Xtreme**
       - High-rise buildings
       - Superior strength
    
    3. **Wonder Plus**
       - Premium quality
       - Better coverage
    
    4. **Wonder OPC**
       - Heavy construction
       - Early strength
    
    ### Current Offers 🎉
    - Bulk order discounts
    - Free technical consultation
    - Site visit assistance
    """)
