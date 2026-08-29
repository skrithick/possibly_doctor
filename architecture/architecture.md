# My Architectural Choices

1. I've chosen to scrape all the non-medquad files as markdown as:
    - Firecrawl parsers help in removing covers and bibliography. It also takes just some basic string manipulation to remove unwanted content. The headings also allow for structural chunking.

2. I've defined my rag pipeline in a self contained class, so that instances can be made of it and used from seperate files. Also it allows for a single-time definition of the embeddings, llms, database etc. which saves memory and increases speed.

3. I've used 3 llm calls:
    - One for the main response
    - One for safety checking
    - One for summarizing

4. Safety Checking:
    - Keyword flagging allows speedy catches
    - LLM flagging after the keyword checks adds complete security.

5. Response Generation:
    - All the responses are formatted using pydantic, so no broken requests or responses are made by the api.

6. Models:
    - I chose gemini-3.1-flash-lite due to it's fast responses and it's really good adherence to prompts.
    - I chose voyageai (mostly coz it has a really good free tier) but also because it has an exceptional embedding system with a huge vocabulary.
    - I chose voyage rerank 2.5 lite due to it's speed and the fact that it also returns confidence scores.

7. Confidence
    - I rely on the mathematical confidence by the reranker as in the off-chance that the LLM hallucinates, the project is saved.
    - However, I take the difference between the LLM Confidence and the mathematical confidence as 'overconfidence' which helps in determining performance.