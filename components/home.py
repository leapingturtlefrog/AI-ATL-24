import streamlit as st

def home_page(st, metrics, name):
    st.title(f"Welcome Back, {name}!")
    st.subheader("Recent Sessions")

    # key is date, valiue is metrics (list[time spent, pictures seen, responses, etc.])
    for key, value in metrics.items():
        st.write(f"{key}: {value}")


