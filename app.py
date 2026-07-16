import streamlit as st
from assistant import create_assistant
from db_save import save_conversation

st.set_page_config(page_title="Course Assistant", page_icon="🎓")


@st.cache_resource
def get_assistant():
    return create_assistant()


assistant = get_assistant()

st.title("🎓 Course Assistant")
st.caption("Ask anything about the course — answers come from the course material.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# replay the conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input pinned to the bottom
if question := st.chat_input("Enter your question…"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the course material…"):
            answer = assistant.rag(question)
        st.write(answer)

        record = assistant.last_call
        st.write(f"Response time: {record.response_time:.2f}s")
        st.write(f"Prompt tokens: {record.prompt_tokens}")
        st.write(f"Completion tokens: {record.completion_tokens}")
        st.write(f"Cost: ${record.cost:.4f}")

        conversation_id = save_conversation(record, question, "llm-zoomcamp")
        st.session_state.conversation_id = conversation_id
        
    st.session_state.messages.append({"role": "assistant", "content": answer})