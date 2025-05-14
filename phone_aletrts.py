import streamlit as st
from pushbullet import Pushbullet

API_KEY= st.secrets['push_API_KEY']

file  = 'notify.txt'
with open(file, mode='r') as f:
	text = f.read()

pb = Pushbullet(API_KEY)
pus = pb.push_note('Please remember', text)


