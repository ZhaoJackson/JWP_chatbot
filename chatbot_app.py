# chatbot_app.py
from src.commonconst import *
from src.prompt import *

# === Initialize Chat State ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are an expert SDG reporting assistant. Your goal is to help United Nations teams "
                "understand and improve Joint WorkPlans to the Sustainable Development Goals (SDGs). "
                "Use official UN language, provide structured insights, and ensure clarity and relevance in every answer."
            )
        },
        {
            "role": "assistant",
            "content": "👋 Ask me a question about Joint Workplans reporting!"
        }
    ]

# === Display Chat History ===
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Show "How to Use?" Help Button ONLY after greeting ===
if len(st.session_state.messages) == 2 and st.session_state.messages[-1]["content"].startswith("👋"):
    with st.expander("📘 How to Use?"):
        st.markdown(
            """
            The data is downloaded from [UN INFO](https://uninfo.org/data-explorer/cooperation-framework/activity-report), 
            where you can access the data by selecting **"Search by Name/Code"** in Additional filters 
            and download the CSV file to your local machine.

            We integrate with the **OpenAI o1 model** to process the uploaded data, 
            mainly to **summarize your queries intelligently**.
            """
        )

# === Load CSV and Data Summary ===
@st.cache_data
def load_csv_data(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame()

def summarize_data(df, n=5):
    try:
        return df.head(n).to_string(index=False)
    except Exception as e:
        return f"Error summarizing data: {e}"

# === Chat Input and Model Interaction ===
if prompt := st.chat_input("Ask your SDG reporting question here..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    df = load_csv_data("src/data/food.csv")
    if df.empty:
        assistant_reply = "⚠️ Food dataset failed to load."
    else:
        context = summarize_data(df)
        enriched_prompt = format_prompt(context, prompt)
        enriched_messages = st.session_state.messages[:-1] + [{"role": "user", "content": enriched_prompt}]

        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=enriched_messages
                )
                assistant_reply = response.choices[0].message.content
        except Exception as e:
            assistant_reply = f"❌ Error communicating with Azure OpenAI: {e}"

    with st.chat_message("assistant"):
        st.markdown(assistant_reply or "⚠️ No response received.")
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})