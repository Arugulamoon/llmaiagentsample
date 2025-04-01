# Configuration
# TODO: Move secrets and config
LANGSMITH_API_KEY=""
OPENAI_API_KEY=""
OTT_REC_FACILITY_URLS = [
    "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/walter-baker-sports-centre",
    "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/minto-recreation-complex-barrhaven",
]

# Environment Setup
import os
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

###########
# Indexing
###########

# 1. Load
# Tried some document loaders (WebBaseLoader, UnstructuredLoader, UnstructuredHTMLLoader)
# Content needed from webpages is HTML table data;
# which appears to be difficult to properly chunk and index
# So, learned some python and beautifulsoup to parse the html instead
import requests
from bs4 import BeautifulSoup

# Data Extraction
# TODO: No need? only benefits human readers? then employ in logging/debug
# TODO: Write tests for all functions
def _clean(s: str) -> str:
    s = s.strip()
    s = s.replace("&nbsp;", " ")
    s = s.replace("\xa0", " ")
    s = s.replace("\n", "")
    s = s.replace("\t", "")
    return s

def _parse_page(page: BeautifulSoup, url: str) -> dict:
    location = page.find("h1").text.strip()
    # TODO: Handle Schedule Changes section
    # (eg Minto March 17 to April 6 The pool is closed for annual maintenance.)
    # How stitch into existing data structure? Or need to adjust for type of query...
    # ie give ai entry points to do either an activity query or a date query
    # - "What are available activities at location X for date Y?"
    # - "What are times for activity X at location Y?"
    categories = []
    for table in page.find_all("table"):
        # determine category (eg Swim) and time blocks (eg March 11 to May 2)
        parsedCaption = _parse_table_caption(table.find("caption"))

        # establish days of the week as defined by table columns
        days = _parse_table_columns(table.find("thead"))

        # determine activities (eg Preschool swim) and their schedule time slot
        activities = _parse_rows(table.find("tbody"), location, days)

        # save
        categories.append({
            "category": parsedCaption.get("category"),
            "time_block_start": parsedCaption.get("time_block_start"),
            "time_block_end": parsedCaption.get("time_block_end"),
            "activities": activities,
        })

    return { "location": location, "categories": categories, "url": url }

def _parse_table_caption(caption: BeautifulSoup) -> dict:
    splitted_caption = _clean(caption.text).split(" - ")
    # skip 0 index, is location (eg Walter Baker)
    match len(splitted_caption):
        case 2: # eg Walter Baker Sports Centre - Weight and cardio room
            category = splitted_caption[1]
            return { "category": category }
        case 3:
            splitted_time_period = splitted_caption[2].split(" to ")
            if len(splitted_time_period) == 1: # date range not present
                # eg Minto Recreation Complex - Barrhaven - Weight and cardio room
                category = splitted_caption[2]
                return { "category": category }
            else:
                # eg Walter Baker Sports Centre - swim and aquafit - January 28 to March 21
                category = splitted_caption[1]
                time_period = splitted_caption[2]
                start, end = time_period.split(" to ")
                return { "category": category, "time_block_start": start, "time_block_end": end }
        case 4: # eg Minto Recreation Complex - Barrhaven - sports - March 17 to June 22
            # TODO: Better handle location with dash in name
            category = splitted_caption[2]
            time_period = splitted_caption[3]
            start, end = time_period.split(" to ")
            return { "category": category, "time_block_start": start, "time_block_end": end }
        case _:
            return {}

def _parse_table_columns(thead: BeautifulSoup) -> list:
    days = [_clean(th.text) for th in thead.find("tr").find_all("th")]
    if len(days) == 8:
        days.remove("")
    return days

def _parse_rows(tbody: BeautifulSoup, location: str, days: list) -> list:
    activity_time_slots = []
    for tr in tbody.find_all("tr"):
        activity = _clean(tr.find("th").text)
        for i, td in enumerate(tr.find_all("td")):
            time_slots = _clean(td.text) # TODO: further split times?
            if time_slots != "n/a":
                activity_time_slots.append({
                    "location": location,
                    "activity": activity,
                    "day": days[i],
                    "time_slots": time_slots,
                })
    return activity_time_slots

# Data Structuring
data = []
for url in OTT_REC_FACILITY_URLS:
    # fetch webpage
    resp = requests.get(url)
    # parse html for activities
    soup = BeautifulSoup(resp.text, "html.parser")
    location_activities = _parse_page(soup, resp.url)
    # save
    data.append(location_activities)

# LangChain Integration
from langchain.schema import Document
docs = []
for d in data:
    docs.append(Document(
        page_content=str(d["categories"]),
        metadata={
            "title": d["location"], # TODO: Inform AI of title to have it better categorize docs?
        }
    ))

# 2. Split
# Tried HTMLSemanticPreservingSplitter (beta)
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
documents = splitter.split_documents(docs)

# 3. Store
# Vector Store and Embeddings model
# Tried Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
vector_store = InMemoryVectorStore(OpenAIEmbeddings())
_ = vector_store.add_documents(documents=documents)

###########################
# Retrieval and Generation
###########################

from langchain import hub
from langgraph.graph import START, StateGraph
from typing import List, TypedDict

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")

# Model/LLM
# Tried Ollama
from langchain_openai import OpenAI
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response}

# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# LLM response
response = graph.invoke({"question": "What can you tell me about LangGraph?"})
print(response["answer"])

# get answer
response = graph.invoke({"question": "What time is Preschool swim on Friday, March 29 at Walter Baker Sports Centre?"})
print(response["answer"])

# get different activity
response = graph.invoke({"question": "What time is Hot tub and steam room on Friday, March 29 at Walter Baker Sports Centre?"})
print(response["answer"])

# get answer from different rec center
response = graph.invoke({"question": "What time is Preschool swim on Friday, April 11 at Minto Recreation Complex - Barrhaven?"})
print(response["answer"])

response = graph.invoke({"question": "When and where are Preschool swims on Friday, April 11?"})
print(response["answer"])

# # get pool closed answer
# response = graph.invoke({"question": "What time is Preschool swim on Tuesday, April 1 at Minto Recreation Complex - Barrhaven?"})
# print(response["answer"])
