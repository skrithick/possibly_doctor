# So basically, I've tried to make a simple medical healthcare rag
# I use 3 llm callings, for response, safety checking and previous chat summarizations
# I store previous 5 messages in memory, this number can be changed in config.py
# I did only 5 messages coz I didn't wanna fry my api keys :)
# I use voyageai (free tier) for embeddings and reranking, and chroma for vectorstore
# My main goal was to make the code a lot more modular as compared to the first task

# In the future I wanna implement a database which can store users, their messages, and preferences
# I also want to use a better model, right now I'm using gemini-3.1-flash-lite

import time
import os
import pandas as pd
from dotenv import load_dotenv

from langchain_community.document_loaders import DataFrameLoader, DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_chroma import Chroma
from langchain_voyageai import VoyageAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from voyageai import Client as VoyageClient

from lib.response_format import Response, CheckerResponse, SummaryResponse
from lib.prompt_template import template, summarizer_template, checker_template
from lib.config import embedding_model, rerank_model, llm_model, summarizer_model, checker_model, dangerous_words, memory

load_dotenv()
voyage_key = os.getenv('VOYAGE_API_KEY')

class PossiblyDoctor():
    def __init__(self):
        self.embeddings = VoyageAIEmbeddings(
            voyage_api_key=voyage_key,
            model=embedding_model
        )

        self.vo = VoyageClient(
            api_key=voyage_key
        )

        self.db = Chroma(
            persist_directory='vectorstore',
            embedding_function=self.embeddings
        )

        self.history = InMemoryChatMessageHistory()

        llm = ChatGoogleGenerativeAI(
            model=llm_model,
            temperature=0.2,
            max_retries=2
        ).with_structured_output(Response)

        summarizer_llm = ChatGoogleGenerativeAI(
            model=summarizer_model,
            temperature=0.0,
            max_retries=2
        ).with_structured_output(SummaryResponse)

        checker_llm = ChatGoogleGenerativeAI(
            model=checker_model,
            temperature=0.2,
            max_retries=2
        ).with_structured_output(CheckerResponse)

        llm_prompt = PromptTemplate(
            template=template,
            input_variables=['context', 'query'],
        )

        summarizer_prompt = PromptTemplate(
            template=summarizer_template,
            input_variables=['recent_messages', 'query']
        )

        checker_prompt = PromptTemplate(
            template=checker_template,
            input_variables=['query']
        )

        self.chunks = list()

        # I wanteed to combine all these into a single chain but I couldn't figure out how to integrate the memory within a single chain
        self.doctor = llm_prompt | llm
        self.summarizer = summarizer_prompt | summarizer_llm
        self.checker = checker_prompt | checker_llm
    
    def csv(self, src):
        df = pd.read_csv(src).dropna(
            subset=['question', 'answer']
        )

        df.fillna('Unknown', inplace=True)
        df['question_answer'] = 'Question: ' + df['question'] + '\nAnswer: ' + df['answer']
        
        src = src.split('/')[-1]
        df['src'] = f'{src} - ' + df['focus_area']

        csv_loader = DataFrameLoader(df, page_content_column='question_answer')
        docs = csv_loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
        print(f'Splitting CSV from {src}')
        chunks = splitter.split_documents(docs)
        self.chunks.extend(chunks)
    
    def md(self, src, glob='*.md'):
        loader = DirectoryLoader(
            src,
            glob=glob,
            loader_cls=UnstructuredMarkdownLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs = loader.load()

        for doc in docs:
            doc.metadata['src'] = f'{os.path.basename(doc.metadata['source'])} - General'
            doc.metadata['org'] = doc.metadata['source'].split('-')[0]
        
        # I was gonna use markdown splitter, but I learnt about this and wanted to try it
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN, 
            chunk_size=512, 
            chunk_overlap=50
        )
        print(f'Splitting Markdown from {src}')
        chunks = splitter.split_documents(docs)
        self.chunks.extend(chunks)
    
    def embed(self):
        print('Embedding\n')

        batch_size = 800
        print(f'{len(self.chunks)} Chunks')

        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i : i + batch_size]
            self.db.add_documents(batch)
            print(f'Ingested batch {i} to {i + len(batch)}')
            time.sleep(5)

        self.chunks = list()
    
    def forget(self):
        self.history = InMemoryChatMessageHistory()
    
    def dangerous(self, query):
        for word in query.split():
            if word.lower() in dangerous_words:
                return True
        res = self.checker.invoke({'query': query})
        print(res.reason)
        return res.danger

    def rerank(self, docs, query):
        results = self.vo.rerank(
            query,
            [doc.page_content for doc in docs],
            model=rerank_model, 
            top_k=3
        ).results

        return results
    
    def summarize(self, messages, query):
        parsed_messages = ''
        for msg in messages:
            parsed_messages += f'{msg.type}: {msg.content}\n'
        
        search_query = self.summarizer.invoke({
            'recent_messages': parsed_messages,
            'query': query
        }).summary

        return search_query

    def query(self, user_question):
        dangerous = self.dangerous(user_question)

        if dangerous:
            return {
                'urgency_level': 3,
                'confidence': 1.0,
                'overconfidence': 0.0,
                'response': 'This query may be dangerous. Please seek help from a professional.',
                'citations': ['No relevant sources found.']
            }

        self.history.messages = self.history.messages[-memory:]
        messages = self.history.messages

        search_query = user_question
        if messages:
            search_query = self.summarize(messages, user_question)

        docs = self.db.similarity_search(search_query, k=10)
        results = self.rerank(docs, search_query)
        
        math_confidence = round(results[0].relevance_score, 2)
        citations = set()
        contexts = []

        for r in results:
            if r.relevance_score < 0.55:
                continue
            doc = docs[r.index]
            citations.add(doc.metadata.get('src'))
            contexts.append(doc.page_content)
        
        if not citations:
            citations.add('No relevant sources found.')

        context = '\n-----\n'.join(contexts) if contexts else 'No relevant sources found.'
        
        print(search_query)
        res = self.doctor.invoke({
            'context': context,
            'query': search_query,
        })

        self.history.add_user_message(user_question)
        self.history.add_ai_message(res.response)

        return {
            'urgency_level': res.urgency_level,
            'confidence': math_confidence,
            'overconfidence': round(res.confidence - math_confidence, 2),
            'response': res.response,
            'citations': citations
        }