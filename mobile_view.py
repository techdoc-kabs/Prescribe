# import streamlit as st
# from streamlit_javascript import st_javascript
# from streamlit_card import card

# # Set wide layout
# st.set_page_config(page_title="Responsive Streamlit Card Demo", layout="wide")

# st.title("📱💻 Responsive Streamlit Cards")

# # Detect screen width using JS
# width = st_javascript("window.innerWidth")
# is_mobile = width is not None and width < 768

# st.info(f"Screen width: {width}px")
# st.success("Mobile view" if is_mobile else "Desktop view")

# # Card data
# card_data = [
#     {
#         "title": "Mental Health",
#         "text": "Track screening outcomes",
#         "image": "https://placekitten.com/400/200",
#         "url": None,
#         "key": "card1"
#     },
#     {
#         "title": "Appointments",
#         "text": "View and manage sessions",
#         "image": "https://placekitten.com/401/200",
#         "url": None,
#         "key": "card2"
#     },
#     {
#         "title": "Reports",
#         "text": "Generate PDF reports",
#         "image": "https://placekitten.com/402/200",
#         "url": None,
#         "key": "card3"
#     },
# ]

# # Show response when a card is clicked
# response = st.empty()

# # Render cards based on layout
# if is_mobile:
#     st.subheader("📱 Mobile Cards (Stacked)")
#     for item in card_data:
#         result = card(
#             title=item["title"],
#             text=item["text"],
#             image=item["image"],
#             key=item["key"]
#         )
#         if result:
#             response.success(f"You clicked: {item['title']}")
# else:
#     st.subheader("💻 Desktop Cards (Side by Side)")
#     cols = st.columns(3)
#     for col, item in zip(cols, card_data):
#         with col:
#             result = card(
#                 title=item["title"],
#                 text=item["text"],
#                 image=item["image"],
#                 key=item["key"]
#             )
#             if result:
#                 response.success(f"You clicked: {item['title']}")

# st.divider()
# st.caption("🔁 Resize the window or use a phone to see responsive card layout.")
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_card import card
st.set_page_config(page_title="Tight Card Layout", layout="centered")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .card-wrapper {
        margin-bottom: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📱💻 Streamlit Cards with Minimal Spacing")
width = st_javascript("window.innerWidth")
is_mobile = width is not None and width < 768
st.info(f"Screen width: {width}px")
card_data = [
    {"title": "Card 1", "text": "This is card 1", "image": "https://placekitten.com/400/200", "key": "card1"},
    {"title": "Card 2", "text": "This is card 2", "image": "https://placekitten.com/401/200", "key": "card2"},
    {"title": "Card 3", "text": "This is card 3", "image": "https://placekitten.com/402/200", "key": "card3"},
]
response = st.empty()
if is_mobile:
    st.subheader("📱 Mobile View")
    for item in card_data:
        with st.container():
            with st.markdown('<div class="card-wrapper">', unsafe_allow_html=True):
                result = card(
                    title=item["title"],
                    text=item["text"],
                    image=item["image"],
                    key=item["key"],
                )
            if result:
                response.success(f"You clicked: {item['title']}")
else:
    st.subheader("💻 Desktop View")
    cols = st.columns([1, 1, 1])
    for col, item in zip(cols, card_data):
        with col:
            with st.markdown('<div class="card-wrapper">', unsafe_allow_html=True):
                result = card(
                    title=item["title"],
                    text=item["text"],
                    image=item["image"],
                    key=item["key"],
                )
            if result:
                response.success(f"You clicked: {item['title']}")
