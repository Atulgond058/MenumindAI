import streamlit as st
import os
from agent import menumindAIAgent, MenuItem, OrderItem, Order

# custom CSS add kar sakte hain:
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 180px;
        object-fit: cover;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Page Config
st.set_page_config(
    page_title="menumind AI - Smart Dining",
    page_icon="🍔",
    layout="wide"
)

# Images folder path (Apne project structure ke hisaab se adjust kar sakte hain)
IMAGE_DIR = os.path.join("data", "images")

def show_item_image(image_filename: str):
    """Local image file safely load karke Streamlit par render karta hai"""
    if image_filename and image_filename.strip():
        img_path = os.path.join(IMAGE_DIR, image_filename)
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.caption("🖼️ *Image missing*")
    else:
        st.caption("🖼️ *No image available*")

# Initialize Session States for backend persistence
if "agent" not in st.session_state:
    menu_path = os.path.join("data", "menu.json")
    st.session_state.agent = menumindAIAgent(menu_path)

if "cart" not in st.session_state:
    st.session_state.cart = {}  # Format: {item_id: quantity}

# Header Section
st.title("🤖 MenuMind AI")
st.caption("Smart Orders, Smarter Dining | AI Assistant")
st.divider()

# Sidebar - Live Cart / Order Summary
st.sidebar.header("🛒 Your Order Summary")

agent = st.session_state.agent
all_items = agent.get_all_menu_items()
item_dict = {item.id: item for item in all_items}

if not st.session_state.cart:
    st.sidebar.info("Your order is empty. Add items from the menu!")
else:
    total_amount = 0.0
    for item_id, qty in list(st.session_state.cart.items()):
        item = item_dict.get(item_id)
        if item:
            subtotal = item.price * qty
            total_amount += subtotal
            col_a, col_b, col_c = st.sidebar.columns([3, 1, 1])
            col_a.write(f"**{item.name}**\n₹{item.price} x {qty}")
            col_b.write(f"₹{subtotal:.2f}")
            if col_c.button("❌", key=f"remove_{item_id}"):
                del st.session_state.cart[item_id]
                st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader(f"Total: ₹{total_amount:.2f}")
    st.sidebar.divider()

    # --- Customer & Table Details Section ---
    st.sidebar.subheader("👤 Customer Details")
    customer_name = st.sidebar.text_input("Customer Name*", placeholder="Enter your name")
    table_number = st.sidebar.number_input("Table Number", min_value=1, max_value=100, value=1, step=1)

    # --- Smart Validation Checkout Logic ---
    if not customer_name.strip():
        st.sidebar.warning("⚠️ Please enter Customer Name to place order.")
        st.sidebar.button("✅ Confirm & Register Order", type="primary", use_container_width=True, disabled=True)
    else:
        if st.sidebar.button("✅ Confirm & Register Order", type="primary", use_container_width=True):
            st.sidebar.success(f"🎉 Order Registered for {customer_name.strip()} (Table #{table_number})! Sending to Kitchen...")
            st.session_state.cart = {}

# Main UI Tabs
tab1, tab2 = st.tabs(["💬 AI Menu Recommender", "📜 Full Menu"])

# Tab 1: AI Recommendation System
with tab1:
    st.subheader("What are you craving today?")
    st.write("Tell our AI what you like (e.g., *'vegan spicy'*, *'healthy salad'*, *'dessert'*):")

    user_input = st.text_input("Search or describe your requirement:", placeholder="e.g. I want something light and healthy")

    if user_input:
        recommendations = agent.recommend_items(user_input)
        st.success(f"Found {len(recommendations)} matches for your search!")

        cols = st.columns(2)
        for idx, item in enumerate(recommendations):
            with cols[idx % 2]:

                show_item_image(item.image)

                st.markdown(f"### {item.name}")
                st.write(f"**Category:** {item.category} | **Price:** ₹{item.price:.2f}")
                st.write(f"🏷️ *Tags:* {', '.join(item.tags)}")

                if st.button(f"Add {item.name} to Cart", key=f"rec_add_{item.id}"):
                    st.session_state.cart[item.id] = st.session_state.cart.get(item.id, 0) + 1
                    st.toast(f"Added {item.name} to order!", icon="🛒")
                    st.rerun()
                st.divider()

# Tab 2: Full Menu View
with tab2:
    st.subheader("Explore Entire Menu")

    cols = st.columns(3)
    for idx, item in enumerate(all_items):
        with cols[idx % 3]:

            show_item_image(item.image)

            st.write(f"### {item.name}")
            st.write(f"💰 **Price:** ₹{item.price:.2f}")
            st.write(f"📁 **Category:** {item.category}")
            st.caption(f"Tags: {', '.join(item.tags)}")

            if st.button("Add to Order", key=f"menu_add_{item.id}"):
                st.session_state.cart[item.id] = st.session_state.cart.get(item.id, 0) + 1
                st.toast(f"Added {item.name}!", icon="🛒")
                st.rerun()
            st.divider()