import random
import pandas as pd
from components.start_session import start_session_page

def home_page(st, metrics, name):
    st.title(f"Welcome Back, {name}!")



    metrics_df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Time Spent", "Pictures Seen", "Responses"])

    metrics_df.reset_index(inplace=True)
    metrics_df.rename(columns={"index": "Session"}, inplace=True)

    metrics_df['Session'] = metrics_df['Session'].astype(int)
    metrics_df['Session'] = "Session " + metrics_df['Session'].astype(str)

    metrics_df['Session Number'] = metrics_df['Session'].str.extract('(\d+)').astype(int)
    metrics_df.sort_values('Session Number', inplace=True)

    metrics_df.set_index("Session", inplace=True)
    metrics_df.drop(columns='Session Number', inplace=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Metrics Overview")
        st.dataframe(metrics_df)

    with col2:
        st.write("")
        st.subheader("Session Trends")
        st.line_chart(metrics_df)

