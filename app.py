import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Ask a 10-K", page_icon="📊")
st.title("📊 Ask a 10-K")
st.caption("Ask questions about Apple, JPMorgan, and Walmart's SEC 10-K filings.")

question = st.text_input("Your question:", placeholder="What are the main risk factors?")

if st.button("Ask") and question:
    with st.spinner("Searching filings and generating answer..."):
        response = requests.post(API_URL, json={"question": question})

    if response.status_code == 200:
        data = response.json()
        st.markdown(data["answer"])

        st.subheader("Sources")
        for s in data["sources"]:
            st.write(f"📄 **{s['source']}** — page {s['page']} (relevance: {s['score']})")
    else:
        st.error(f"Something went wrong: {response.status_code}")