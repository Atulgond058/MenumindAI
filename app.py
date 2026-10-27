import streamlit as st
import os
from agent import menumindAIAgent

# Page Config
st.set_page_config(
    page_title="MenuMind AI - Smart Dining",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS with Smooth Scroll & Animations
st.markdown("""
    <style>
    html {
        scroll-behavior: smooth;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }

    [data-testid="stImage"] img {
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s ease;
    }
    [data-testid="stImage"] img:hover { transform: scale(1.03); }

    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #4338ca 0%, #2563eb 100%);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }

    .badge {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .price-tag { color: #10b981; font-size: 1.25rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

IMAGE_DIR = os.path.join("data", "images")

def show_item_image(image_filename: str):
    if image_filename and image_filename.strip():
        img_path = os.path.join(IMAGE_DIR, image_filename)
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    else:
        st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80", use_container_width=True)

if "agent" not in st.session_state:
    menu_path = os.path.join("data", "menu.json")
    st.session_state.agent = menumindAIAgent(menu_path)

if "cart" not in st.session_state:
    st.session_state.cart = {}

agent = st.session_state.agent
all_items = agent.get_all_menu_items()
item_dict = {item.id: item for item in all_items}

# Sidebar - Cart
st.sidebar.title("🛒 Order Summary")

if not st.session_state.cart:
    st.sidebar.info("Your order is empty. Explore items from the menu!")
else:
    total_amount = 0.0
    for item_id, qty in list(st.session_state.cart.items()):
        item = item_dict.get(item_id)
        if item:
            subtotal = item.price * qty
            total_amount += subtotal
            col_a, col_b, col_c = st.sidebar.columns([3, 1.5, 1])
            col_a.markdown(f"**{item.name}**\n<small>₹{item.price} x {qty}</small>", unsafe_allow_html=True)
            col_b.write(f"₹{subtotal:.2f}")
            if col_c.button("❌", key=f"remove_{item_id}"):
                del st.session_state.cart[item_id]
                st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown(f"### Total: <span class='price-tag'>₹{total_amount:.2f}</span>", unsafe_allow_html=True)
    st.sidebar.divider()

    st.sidebar.subheader("👤 Customer Details")
    customer_name = st.sidebar.text_input("Customer Name*", placeholder="Enter customer name")
    table_number = st.sidebar.number_input("Table Number", min_value=1, max_value=100, value=1, step=1)

    if not customer_name.strip():
        st.sidebar.warning("⚠️ Enter Customer Name to register order.")
        st.sidebar.button("✅ Confirm Order", disabled=True, key="dis_btn")
    else:
        if st.sidebar.button("✅ Confirm & Send to Kitchen", type="primary"):
            st.sidebar.balloons()
            st.sidebar.success(f"🎉 Order Confirmed for {customer_name.strip()} (Table #{table_number})!")
            st.session_state.cart = {}

# Header
st.title("🤖 MenuMind AI")
st.caption("Smart Recommendations & Instant Restaurant Ordering")
st.divider()

tab1, tab2 = st.tabs(["✨ AI Recommendation", "📜 Full Menu"])

with tab1:
    st.subheader("What are you craving today?")
    st.write("Type your preferences (e.g., *'spicy pizza'*, *'healthy salad'*, *'vegan burger'*):")

    user_input = st.text_input("Describe your choice:", placeholder="e.g. I want something light and healthy")
    recommendations = agent.recommend_items(user_input) if user_input else all_items

    if user_input:
        st.success(f"Found {len(recommendations)} recommendations for you!")

    cols = st.columns(2)
    for idx, item in enumerate(recommendations):
        with cols[idx % 2]:
            with st.container(border=True):
                show_item_image(item.image)
                st.markdown(f"### {item.name}")
                st.markdown(f"**Category:** {item.category} | <span class='price-tag'>₹{item.price:.2f}</span>", unsafe_allow_html=True)
                
                tags_html = "".join([f"<span class='badge'>{tag}</span>" for tag in item.tags])
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("")

                if st.button(f"🛒 Add {item.name}", key=f"rec_add_{item.id}"):
                    st.session_state.cart[item.id] = st.session_state.cart.get(item.id, 0) + 1
                    st.toast(f"Added {item.name} to cart!", icon="🛒")
                    st.rerun()

with tab2:
    st.subheader("Explore Our Menu")
    categories = list(set([item.category for item in all_items]))
    selected_cat = st.selectbox("Filter by Category", ["All"] + categories)
    
    filtered_items = [item for item in all_items if selected_cat == "All" or item.category == selected_cat]

    cols = st.columns(3)
    for idx, item in enumerate(filtered_items):
        with cols[idx % 3]:
            with st.container(border=True):
                show_item_image(item.image)
                st.markdown(f"### {item.name}")
                st.markdown(f"<span class='price-tag'>₹{item.price:.2f}</span> | **{item.category}**", unsafe_allow_html=True)
                
                tags_html = "".join([f"<span class='badge'>{tag}</span>" for tag in item.tags])
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("")

                if st.button("Add to Order", key=f"menu_add_{item.id}"):
                    st.session_state.cart[item.id] = st.session_state.cart.get(item.id, 0) + 1
                    st.toast(f"Added {item.name}!", icon="🛒")
                    st.rerun()
