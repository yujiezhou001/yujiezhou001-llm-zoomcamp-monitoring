import streamlit as st
from assistant import create_assistant
from db_save import save_conversation
from db_feedback import save_feedback

st.set_page_config(page_title="Course Assistant", page_icon="🎓")


@st.cache_resource
def get_assistant():
    return create_assistant()


assistant = get_assistant()

st.title("🎓 Course Assistant")
st.caption("Ask anything about the course — answers come from the course material.")

if "messages" not in st.session_state:
    st.session_state.messages = []


def record_feedback(index):
    """Runs before the rerun when a thumb is clicked."""
    choice = st.session_state[f"fb_{index}"]     # 0 = 👎, 1 = 👍, None = untouched
    if choice is None:
        return
    score = 1 if choice == 1 else -1
    msg = st.session_state.messages[index]
    msg["feedback"] = score
    save_feedback(msg["conversation_id"], "user", score=score)


# --- replay the conversation (feedback + metrics live here, per answer) ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant":
            m = msg["metrics"]
            st.caption(
                f"⏱ {m['response_time']:.2f}s · "
                f"🔢 {m['prompt_tokens']}+{m['completion_tokens']} tokens · "
                f"💲 {m['cost']:.4f}"
            )

            if msg["feedback"] is None:
                st.feedback("thumbs", key=f"fb_{i}",
                            on_change=record_feedback, args=(i,))
            else:
                st.caption("👍 Thanks for the feedback!" if msg["feedback"] == 1
                           else "👎 Thanks — noted, we'll use it to improve.")

# --- input pinned to the bottom ---
if question := st.chat_input("Enter your question…"):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("Searching the course material…"):
        answer = assistant.rag(question)

    record = assistant.last_call
    conversation_id = save_conversation(record, question, "llm-zoomcamp")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "conversation_id": conversation_id,
        "metrics": {
            "response_time": record.response_time,
            "prompt_tokens": record.prompt_tokens,
            "completion_tokens": record.completion_tokens,
            "cost": record.cost,
        },
        "feedback": None,
    })
    st.rerun()