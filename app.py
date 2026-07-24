import streamlit as st
import os
from agent import ManumindAIAgent, MenuItem, OrderItem, Order

# Page Config
st.set_page_config(
    page_title="Manumind AI - Smart Dining",
    page_icon="🍔",
    layout="wide"
)

# Initialize Session States for backend persistence
if "agent" not in st.session_state:
    menu_path = os.path.join("data", "menu.json")
    st.session_state.agent = ManumindAIAgent(menu_path)

if "cart" not in st.session_state:
    st.session_state.cart = {}  # Format: {item_id: quantity}

# Header Section
st.title("🤖 Manumind AI")
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

    if st.sidebar.button("✅ Confirm & Register Order", type="primary", use_container_width=True):
        st.sidebar.success("🎉 Order Registered Successfully! Sending to Kitchen...")
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
            st.write(f"### {item.name}")
            st.write(f"💰 **Price:** ₹{item.price:.2f}")
            st.write(f"📁 **Category:** {item.category}")
            st.caption(f"Tags: {', '.join(item.tags)}")

            if st.button("Add to Order", key=f"menu_add_{item.id}"):
                st.session_state.cart[item.id] = st.session_state.cart.get(item.id, 0) + 1
                st.toast(f"Added {item.name}!", icon="🛒")
                st.rerun()
            st.divider()