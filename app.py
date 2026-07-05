import streamlit as st
import heapq
from google import genai

# Page Configuration Setup
st.set_page_config(page_title="Smart Logistics Hub & AI Chat Copilot", layout="wide", initial_sidebar_state="expanded")

# Custom Dark Theme Styling (Vercel Production Optimized)
st.markdown("""
    <style>
    .main { background-color: #0F172A; color: #E2E8F0; }
    .stButton>button { background-color: #EF4444; color: white; border-radius: 6px; border: none; font-weight: bold; width: 100%; }
    .stButton>button:hover { background-color: #DC2626; color: white; }
    div[data-testid="stExpander"] { background-color: #1E293B; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# DATABASE MODEL & AI CHAT HUB ENGINE
# =========================================================================
GEMINI_API_KEY = "AQ.Ab8RN6JHeJUJEzNJO96YmUofxdoGSpSt35FWPru0OG5nZlvpEQ"

travel_graph = {
    'Islamabad': [('Peshawar', 1500, 2.0), ('Lahore', 3500, 4.5), ('Abbottabad', 1200, 2.5), ('Haripur', 600, 1.0)],
    'Haripur': [('Islamabad', 600, 1.0), ('Abbottabad', 600, 1.5)],
    'Peshawar': [('Islamabad', 1500, 2.0), ('Swat', 2200, 3.5)],
    'Abbottabad': [('Islamabad', 1200, 2.5), ('Mansehra', 600, 0.8), ('Swat', 3200, 4.8), ('Haripur', 600, 1.5)],
    'Mansehra': [('Abbottabad', 600, 0.8), ('Naran', 2800, 3.5)],
    'Swat': [('Peshawar', 2200, 3.5), ('Abbottabad', 3200, 4.8), ('Chitral', 4500, 6.5)],
    'Chitral': [('Swat', 4500, 6.5)],
    'Naran': [('Mansehra', 2800, 3.5), ('Gilgit', 5500, 6.0)],
    'Gilgit': [('Naran', 5500, 6.0)],
    'Lahore': [('Islamabad', 3500, 4.5), ('Multan', 3200, 4.0), ('Karachi', 14000, 15.0)],
    'Multan': [('Lahore', 3200, 4.0), ('Karachi', 9000, 11.0)],
    'Karachi': [('Lahore', 14000, 15.0), ('Multan', 9000, 11.0)]
}

def get_segment_metrics(current, next_node):
    for neighbor, cost, time in travel_graph.get(current, []):
        if neighbor == next_node:
            return cost, time
    return 0, 0

def execute_logistics_ucs(graph, start, goal, optimization_target):
    priority_queue = [(0, start, [start], 0)]
    visited = set()
    while priority_queue:
        curr_weight, node, path, alt_weight = heapq.heappop(priority_queue)
        if node in visited: continue
        if node == goal: return path, curr_weight, alt_weight
        visited.add(node)
        for neighbor, cost, time in graph.get(node, []):
            if neighbor not in visited:
                selected_weight = cost if optimization_target == 'cost' else time
                secondary_weight = time if optimization_target == 'cost' else cost
                heapq.heappush(priority_queue, (curr_weight + selected_weight, neighbor, path + [neighbor], alt_weight + secondary_weight))
    return None, 0, 0

# =========================================================================
# WEB DASHBOARD INTERFACE LAYOUT
# =========================================================================
st.title("🚚 Smart Logistics Hub & AI Chat Copilot")
st.caption("Real-time Dynamic Route Optimization Engine powered by UCS Algorithm & Gemini Intelligence")

# Split Columns Layout (Left Controls + Right Sidebar Insights)
col_left, col_right = st.columns([2, 1])

cities = sorted(list(travel_graph.keys()))

with col_left:
    st.markdown("### 🛠️ Route Parameters")
    inner_c1, inner_c2 = st.columns(2)
    with inner_c1:
        start_city = st.selectbox("START CITY", cities, index=0)
    with inner_c2:
        end_city = st.selectbox("END CITY", cities, index=2)
        
    metric_target = st.radio("Optimization Target:", ["Minimize Cost (PKR)", "Minimize Time (Hours)"])
    target_slug = "cost" if "Cost" in metric_target else "time"
    
    calculate_click = st.button("Calculate Optimal Freight Route")

with col_right:
    st.markdown("### 📊 System Metadata")
    st.info("""
    - **Engine Compute:** Uniform Cost Search (UCS)
    - **Model Engine:** gemini-2.5-flash
    - **Session Architecture:** Persistent Dynamic Context
    """)

# Persistent Web State Matrix Management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "system_context" not in st.session_state:
    st.session_state.system_context = ""

if calculate_click:
    if start_city == end_city:
        st.error("Validation Error: Start aur End cities unique honi chahiye hain!")
    else:
        path, primary, secondary = execute_logistics_ucs(travel_graph, start_city, end_city, target_slug)
        
        if path:
            total_cost = primary if target_slug == "cost" else secondary
            total_time = secondary if target_slug == "cost" else primary
            
            # Display KPIs Cards
            st.markdown("---")
            st.markdown("### 🏆 Route Optimization Manifest")
            kpi_c1, kpi_c2 = st.columns(2)
            kpi_c1.metric(label="TOTAL FREIGHT COST", value=f"PKR {total_cost:,}")
            kpi_c2.metric(label="TOTAL TRANSIT TIME", value=f"{total_time:.1f} Hours")
            
            # Step by Step Sequence Matrix
            st.markdown("#### 🗺️ Step-by-Step Logistics Sequence Directions")
            table_data = []
            for idx, node in enumerate(path):
                if idx == 0:
                    table_data.append({"Stop No": f"Stop #{idx+1}", "City Name": node, "Segment Detail": "Starting Point", "Metric Cost": "0.0 Metrics"})
                else:
                    s_cost, s_time = get_segment_metrics(path[idx-1], node)
                    if target_slug == "cost":
                        table_data.append({"Stop No": f"Stop #{idx+1}", "City Name": node, "Segment Detail": f"PKR {s_cost:,}", "Metric Cost": f"{s_time:.1f} Hours"})
                    else:
                        table_data.append({"Stop No": f"Stop #{idx+1}", "City Name": node, "Segment Detail": f"{s_time:.1f} Hours", "Metric Cost": f"PKR {s_cost:,}"})
            st.table(table_data)
            
            # Update Gemini Context String
            st.session_state.system_context = f"""
            You are a logistics safety expert chatbot in Pakistan. 
            The user has successfully generated a route from {start_city} to {end_city} via path {" -> ".join(path)}.
            Total Cost: PKR {total_cost:,}, Total Time: {total_time:.1f} Hours.
            Always reply strictly in a blend of Roman Urdu and English. Keep it concise, professional, and practical.
            """
            
            # First AI Advisory Greeting System Trigger
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                init_prompt = f"{st.session_state.system_context}\nProvide an initial brief 2-sentence safe driving advisor welcome statement."
                response = client.models.generate_content(model='gemini-2.5-flash', contents=init_prompt)
                st.session_state.chat_history = [{"role": "assistant", "content": response.text.strip()}]
            except Exception as e:
                st.session_state.chat_history = [{"role": "assistant", "content": f"AI Engine Connection Error: {str(e)}"}]
        else:
            st.error("Engine Fault: Koi viable route nahi mila selected criteria par.")

# --- CHATBOT SCREEN VIEW INTERFACE ---
if st.session_state.system_context:
    st.markdown("---")
    st.markdown("### 💬 Live Gemini Copilot Chat Interface")
    
    # Render historic conversation blocks
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Capture user web text dynamic entries
    if user_input := st.chat_input("Ask a follow up logistics query (e.g., weather updates, traffic delays)..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Stream dynamic execution from background endpoint
        with st.chat_message("assistant"):
            with st.spinner("Gemini typing..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    # Building prompt context array chain
                    full_prompt = f"{st.session_state.system_context}\nChat History Summary:\n"
                    for h in st.session_state.chat_history[-4:]: # Send last 4 messages for token optimization memory
                        full_prompt += f"{h['role']}: {h['content']}\n"
                    full_prompt += f"New User Message: {user_input}\nAssistant:"
                    
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=full_prompt)
                    ai_res = response.text.strip()
                    st.write(ai_res)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_res})
                except Exception as e:
                    st.error(f"Error executing request: {str(e)}")