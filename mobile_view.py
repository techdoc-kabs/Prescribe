
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_card import card
import random

st.set_page_config(page_title="Responsive Cards", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .card-wrapper {
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📱💻 Responsive Streamlit Cards (2-column mobile view)")

width = st_javascript("window.innerWidth")
is_mobile = width is not None and width < 768
st.info(f"Screen width: {width}px")

card_data = [
    {"title": "📄 Card 1", "text": "This is card 1", "image": "https://placekitten.com/400/200", "key": "card1"},
    {"title": "📄 Card 2", "text": "This is card 2", "image": "https://placekitten.com/401/200", "key": "card2"},
    {"title": "📄 Card 3", "text": "This is card 3", "image": "https://placekitten.com/402/200", "key": "card3"},
    {"title": "📄 Card 4", "text": "This is card 4", "image": "https://placekitten.com/403/200", "key": "card4"},
]

def get_random_color():
    colors = ["#FF6B6B", "#4ECDC4", "#556270", "#C7F464", "#FFCC5C"]
    return random.choice(colors)

response = st.empty()

# Use 2-column layout on mobile for better fit
if is_mobile:
    st.subheader("📱 Mobile View (2 Columns)")
    rows = [card_data[i:i+2] for i in range(0, len(card_data), 2)]  # split into pairs
    for row in rows:
        cols = st.columns(2)
        for col, item in zip(cols, row):
            color = get_random_color()
            with col:
                clicked = card(
                    title=item["title"],
                    text=item["text"],
                    image=item["image"],
                    key=item["key"],
                    styles={
                        "card": {
                            "width": "100%",
                            "height": "180px",
                            "border-radius": "15px",
                            "background": f"linear-gradient(135deg, {color}, #ffffff)",
                            "color": "white",
                            "box-shadow": "0 3px 6px rgba(0, 0, 0, 0.1)",
                            "border": "1px solid #ccc",
                            "text-align": "center",
                            "padding": "10px",
                            "margin": "0",
                        },
                        "title": {
                            "font-size": "30px",
                            "margin": "0 0 5px 0",
                        },
                        "text": {
                            "font-size": "16px",
                            "margin": "0",
                        },
                    }
                )
                if clicked:
                    response.success(f"You clicked: {item['title']}")

else:
    st.subheader("💻 Desktop View (3 Columns)")
    cols = st.columns(3)
    for col, item in zip(cols, card_data):
        color = get_random_color()
        with col:
            clicked = card(
                title=item["title"],
                text=item["text"],
                image=item["image"],
                key=item["key"],
                styles={
                    "card": {
                        "width": "100%",
                        "height": "220px",
                        "border-radius": "20px",
                        "background": f"linear-gradient(135deg, {color}, #ffffff)",
                        "color": "white",
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                        "border": "1px solid #bbb",
                        "text-align": "center",
                        "padding": "15px",
                        "margin": "0",
                    },
                    "title": {
                        "font-size": "35px",
                        "margin": "0 0 10px 0",
                    },
                    "text": {
                        "font-size": "18px",
                        "margin": "0",
                    },
                }
            )
            if clicked:
                response.success(f"You clicked: {item['title']}")

