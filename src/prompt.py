# src/prompt.py

def format_prompt(data_snippet, user_question):
    return f"""
You are a helpful AI assistant. Use the following food data to answer the user's question.

Food Data Sample:
{data_snippet}

User's Question:
Q: {user_question}
A:"""