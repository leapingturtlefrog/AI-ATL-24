import pandas as pd
from components.start_session import start_session_page

def home_page(st, metrics):
    st.title(f"Welcome Back, {st.session_state.patient_first_name}!")

    # TODO: fix session logs
    # session_logs = ""

    # TODO: this call is working but the old page is still visible
    # st.button("Start New Session", on_click=lambda: start_session_page(st, session_logs))

    st.subheader("Recent Sessions")

    metrics_df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Time Spent", "Pictures Seen", "Responses"])

    metrics_df.reset_index(inplace=True)
    metrics_df.rename(columns={"index": "Session"}, inplace=True)

    metrics_df.set_index("Session", inplace=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Metrics Overview")
        st.dataframe(metrics_df)

    with col2:
        st.write("")
        st.subheader("Session Trends")
        st.line_chart(metrics_df)
