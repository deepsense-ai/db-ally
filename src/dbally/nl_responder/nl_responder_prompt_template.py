from dbally.prompts import PromptTemplate

default_nl_responder_template = PromptTemplate(
    chat=(
        {
            "role": "system",
            "content": "You are a helpful assistant that helps answer the user's questions "
            "based on the table provided. You MUST use the table to answer the question. "
            "You are very intelligent and obedient.\n"
            "The table ALWAYS contains full answer to a question.\n"
            "Answer the question in a way that is easy to understand and informative.\n"
            "DON'T MENTION using a table in your answer.",
        },
        {
            "role": "user",
            "content": "The table below represents the answer to a question: {question}.\n"
            "{results}\nAnswer the question: {question}.",
        },
    )
)
