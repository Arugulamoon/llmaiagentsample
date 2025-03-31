"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

import requests
from typing import Any, Callable, List, Optional, Annotated, cast
from bs4 import BeautifulSoup

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools import tool
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import hub

from react_agent.configuration import Configuration


# TODO: Receiving Tavily ClientConnectorCertificateError from async
# Fix and reimplement async
def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = wrapped.invoke({"query": query})
    return cast(list[dict[str, Any]], result)

OTT_REC_FACILITY_URLS = [
    "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/walter-baker-sports-centre",
    "https://ottawa.ca/en/recreation-and-parks/facilities/place-listing/minto-recreation-complex-barrhaven",
]

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
    time_blocks = []
    for table in page.find_all("table"):
        # determine category (eg Swim) and time blocks (eg March 11 to May 2)
        parsedCaption = _parse_table_caption(table.find("caption"))

        # establish days of the week as defined by table columns
        days = _parse_table_columns(table.find("thead"))

        # determine activities (eg Preschool swim) and their schedule time slot
        activities = _parse_rows(table.find("tbody"), location, days)

        # save
        time_blocks.append({
            "category": parsedCaption.get("category"),
            "time_block_start": parsedCaption.get("time_block_start"),
            "time_block_end": parsedCaption.get("time_block_end"),
            "activities": activities,
        })

    return { "location": location, "time_blocks": time_blocks, "url": url }

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
    tr = thead.find("tr")
    if tr == None:
        return []
    days = [_clean(th.text) for th in thead.find("tr").find_all("th")]
    if len(days) == 8: # TODO: Make more robust
        days.remove("")
    return days

def _parse_rows(tbody: BeautifulSoup, location: str, days: list) -> list:
    activity_time_slots = []
    for tr in tbody.find_all("tr"):
        th = tr.find("th")
        if th != None:
            activity = _clean(th.text)
            for i, td in enumerate(tr.find_all("td")):
                time_slots = _clean(td.text) # TODO: further split times?
                if time_slots != "n/a":
                    activity_time_slots.append({
                        "location": location,
                        "activity": activity,
                        "day": days[i],
                        "time_slots": time_slots.replace("Noon", "12pm"),
                    })
    return activity_time_slots

@tool
async def get_preschool_swim_times(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Get preschool swim times.

    This function accesses websites for Recreation Centers and returns
    time slots for activities for a particular day.
    """
    # configuration = Configuration.from_runnable_config(config)
    # TODO: implement PreschoolSwimResults(max_results=configuration.max_search_results)
    # wrapped = TavilySearchResults(max_results=configuration.max_search_results)

    data = []
    for url in OTT_REC_FACILITY_URLS:
        # fetch webpage
        resp = requests.get(url)
        # parse html for activities
        soup = BeautifulSoup(resp.text, "html.parser")
        location_activities = _parse_page(soup, resp.url)
        # save
        data.append(location_activities)

    docs = []
    for d in data:
        docs.append(Document(
            page_content=str(d["time_blocks"]),
            metadata={
                "title": d["location"], # TODO: Inform AI of title to have it better categorize docs?
            }
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    documents = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vector_store = InMemoryVectorStore(embeddings)
    _ = vector_store.add_documents(documents=documents)

    retrieved_docs = vector_store.similarity_search(query)
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # TODO: Customize prompt
    # ref: https://python.langchain.com/v0.1/docs/use_cases/question_answering/quickstart/#customizing-the-prompt
    prompt = hub.pull("rlm/rag-prompt")
    result = await prompt.ainvoke({"question": query, "context": docs_content})
    return cast(list[dict[str, Any]], result)

TOOLS: List[Callable[..., Any]] = [search, get_preschool_swim_times]
