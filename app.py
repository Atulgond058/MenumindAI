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
st.markdown("""
    <style>
    /* Simple & Clean Light Theme */
    html {
        scroll-behavior: smooth;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Clean Image Styling */
    [data-testid="stImage"] img {
        height: 190px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    /* Simple Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Clean Solid Buttons */
    div.stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
    }

    /* Simple Tags/Badges */
    .badge {
        background-color: #e0e7ff;
        color: #3730a3;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
        font-weight: 500;
    }

    .price-tag {
        color: #059669;
        font-size: 1.2rem;
        font-weight: 700;
    }
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
