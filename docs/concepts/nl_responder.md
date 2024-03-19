# Concept: Natural Language Responder

Natural Language Responder is an LLM-based component engineered to understand both user queries expressed in natural language and relevant data that answers this question, and formulate precise responses to address the user's questions effectively. It serves as an intermediary between users and data, facilitating seamless interaction and enabling users to obtain actionable insights effortlessly.

!!! example

    For the given data extracted from the table:

    | name | country | position | university | skills | tags |
    | ---- | ------- | -------- | ---------- | ------ | ---- |
    | Emily Chen | Canada | Data Scientist | University of Toronto | R; Python; Machine Learning | Data Analysis Research |

    when asked “Find all candidates suitable for a data scientist position who lives in Canada?” an LLM might generate a natural language response like this
    “Emily Chen from Canada is a suitable candidate for the Data Scientist position. Emily Chen has 3 years of experience and holds a degree from the University of Toronto. She is proficient in R, Python, and Machine Learning, with skills in Data Analysis and Research.”.

In this way, Natural Language Responder simplifies the process of obtaining data-driven insights by enabling users to receive responses in a format they understand, eliminating the need to navigate complex tables.

!!! note

    For large tables, when the prompt exceeds the maximum prompt length accepted by the model, Natural Language Responder will return a description of the results based on the query, omitting table analysis step.
