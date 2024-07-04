from dbally.prompt import PromptTemplate

TEXT2SQL_PROMPT_TEMPLATE = PromptTemplate(
    (
        {
            "role": "system",
            "content": (
                "You are given the following SQL tables:"
                "\n\n{schema}\n\n"
                "Your job is to write queries given a user’s request."
                "Please return only the query, do not provide any extra text or explanation."
            ),
        },
        {
            "role": "user",
            "content": ("{question}"),
        },
    )
)
