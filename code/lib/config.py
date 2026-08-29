# I put all the stuff I was too lazy change here
# I'm sure there's a better way to do this but then again, lazy

llm_model = 'gemini-3.1-flash-lite'
checker_model = 'gemini-3.1-flash-lite'
summarizer_model = 'gemini-3.1-flash-lite'
rerank_model = 'rerank-2.5-lite'
embedding_model = 'voyage-4-lite'
memory = 5

dangerous_words = [
    'suicide',
    'harm',
    'self-harm',
    'self harm',
    'kill',
    'murder',
    'abort',
    'lethal dose',
    'poison',
    'narcotics',
    'heroin',
    'incapacitating agents',
    'knock out',
    'knockout',
    'illegal drug',
    'fentanyl',
    'cocaine',
    'meth',
    'acid',
    'lsd',
    'dope'
]