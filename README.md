# Coding Project: Chatbot with LLM and Tool Use

## Objective

Create a chatbot that utilizes a Large Language Model (LLM) of your choice and implements tools for enhanced functionality. The chatbot should handle user queries and leverage external tools or APIs to provide enriched responses.

As parents of an active toddler, my wife and I regularly raise the need to have a list of available activities to consider at a moment's notice. We have ideas in our head, lists in Google Keep etc, but we still find ourselves periodically checking the preschool swim times for a couple of local recreation facilities.

I had already thought through the design of: 1) a golang app that regularly scrapes the 2 webpages for the swim times, 2) persists the data and then 3) syncs the data to our Google Calendar using the calendar sdk.

The chatbot provides the functionality from 1) as a tool to enrich its output. Please find it within the [langgraphsample](langgraphsample/) directory.

## Requirements

### Develop a chatbot that interfaces with an LLM (e.g., OpenAI GPT, Anthropic Claude, Cohere, or an open-source alternative).

Started by using Ollama but eventually switched to using OpenAI GPT.

### Implement at least one tool or API integration that the chatbot can use to enhance its responses (e.g., weather API, search engine, database lookup, or calculator).

Tavily search came for free with the template. Added a custom `get_preschool_swim_times` tool. Essentially, it fetches the webpage for 2 facilities, parses the html and provides the relevant facility activities and times to the LLM. The implementation is a first pass and quite naive. Subsequent TODO items would be to formalize it as a Class and harden the data structure/better set metadata for the LLM to make the retrieval more precise.

### Design a structured way for the chatbot to decide when to use a tool versus relying on the LLM's response.

This seems to come setup with the template in the form of the prompt, tool comments and the `src/react_agent/graph.py#route_model_output` function. As I understand it, the prompt and tool comments are passed along to the LLM to help it decide when to use one tool over another. During my testing, when I asked for current events, the search tool was used whereas when I asked for preschool swim times, it used the custom preschool swim tool.

When researching RAG Chain vs Agent architectures, this seemed to be the notion. RAG Chain workflows were more scripted in terms of when to use one tool vs another, but with agents, that is left to the LLM to decide. Meaning the metadata attached to a tool and dataset is critical to properly inform the LLM.

As it is, a subsequent TODO item is to research [LangGraph Tutorial: Common Workflows](https://langchain-ai.github.io/langgraph/tutorials/workflows/) and see if more can be done to better inform the LLM for making decisions.

### Ensure a seamless interaction between the user, LLM, and tool integrations.

This also seemed to come setup with the template. Rather, LangGraph bootstraps these. Creating tools and binding them to the LLM ensures the LLM can decide when to use a tool. Setting up the edges on the graph ensures the LLM knows how to properly flow through the workflow. Having appropriate prompts helps the LLM to know what reasoning it should be applying.

### Include automated tests covering key functionality.

Unit tests were implemented around the custom html parsing code. Subsequent TODO items would be to explore how to validate when the LLM uses one tool vs another.

## Expectations

### Well-structured, maintainable, and readable code.

LangGraph looks to be a good next step with LangChain, in terms of better structuring an LLM AI Agent project (ie separate files for `config`, `graph`, `prompts`, `state` and `tools`). Much of the material I followed before encountering the LangGraph Templates spoke of these components, but merged them into one file. Workable code to showcase things functioning, but not particularly effective in being well-structured and maintainable long-term.

I spent more time kicking the tires on LangChain elements and building out a proof-of-concept, that by the time I got to looking at code structure, I appreciated seeing it addressed within the LangGraph Template. I can see the need to break custom tools out into independent packages, but otherwise, the separate files is good enough for now.

### List of resources used in the construction of your solution. E.g., articles, tutorials, tools, references, etc.

* Initially read [Mastering LLM AI Agents: Building and Using AI Agents in Python with Real-World Use Cases](https://medium.com/@jagadeesan.ganesh/mastering-llm-ai-agents-building-and-using-ai-agents-in-python-with-real-world-use-cases-c578eb640e35) to start understanding what they are and what can be done with them.
* First tutorial I followed was [Build an Agent](https://python.langchain.com/docs/tutorials/agents/) from the LangChain tutorial section.
* At this point, I started to explore Retrieval Augmentation Generation (RAG) Chains by reading [Using langchain for Question Answering on Own Data](https://medium.com/@onkarmishra/using-langchain-for-question-answering-on-own-data-3af0a82789ed) and then following the tutorials: [Build a Retrieval Augmented Generation (RAG) App: Part 1](https://python.langchain.com/docs/tutorials/rag/) and [Build a Retrieval Augmented Generation (RAG) App: Part 2](https://python.langchain.com/docs/tutorials/qa_chat_history/)
* Spent some time researching different loaders and splitters and trying them out, trying to get them to properly serve the html table data within them to the LLM. Lots of tutorials on scraping simple html but none really effective with html tables. The [HTMLSemanticPreservingSplitter](https://python.langchain.com/api_reference/text_splitters/html/langchain_text_splitters.html.HTMLSemanticPreservingSplitter.html) looked compelling, but couldn't get it working easily enough and it is in beta, so moved on.
* Then I found [How to Load HTML Documents in LangChain: A Step-by-Step Guide](https://medium.com/towards-agi/how-to-load-html-documents-in-langchain-a-step-by-step-guide-fd538dfc53ac). I followed it to create the [local-activities](local-activities/) app where I built out the custom preschool swim html parsing code (which eventually went into the tool). This also involved some time learning enough Python to get it working. The app could respond with preschool swim times, so I finally had some sense of the end-to-end flow, but it didn't have a clear way to add more tools or be able to decide on when to use.
* LangGraph finally came into the picture and in checking the [Tutorials](https://langchain-ai.github.io/langgraph/tutorials/), I was happy to find [Build a Customer Support Bot](https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/)... which also made me sad to think that my, and I will quote my toddler son here "I have a great ideeeeea!" project... could be distilled down to the Excursions: `search_trip_recommendations` tool :/ I started to take this tutorial and strip out all the other tools to get down to my use case but during that process, I landed on the...
* LangGraph [Template Applications](https://langchain-ai.github.io/langgraph/concepts/template_applications/) and so I went the other direction, bootstrapping a new ReAct Agent with the description "A simple agent that can be flexibly extended to many tools."
* Read [How to call tools using ToolNode](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/) which showed how to designate a python function as a formal Tool and wire it into the call flow for the app. And how it informs the LLM on which tool to call, when. Also [Tool calling](https://python.langchain.com/docs/concepts/tool_calling/).

### Proper documentation explaining the design decisions, setup, and usage.

See [langgraphsample README](langgraphsample/README.md) for setup and usage.

The design decisions start with the usage of a LangGraph Template to bootstrap the project. My exploration began with LangChain, which helped with getting into the content and getting started coding. The content and tutorials were more plentiful and LangGraph is built on it anyways. As mentioned above, LangGraph looks to be a good iteration from LangChain for building LLM AI Agents.

### A README file with instructions on how to run and test the project.

See [langgraphsample README](langgraphsample/README.md). Certainly not the best name, just happened to be my test run of the `langgraph` CLI create project from template command. And as prototypes are want to become... it became the flagship app!

The README includes a bunch of bootstrapped content along with additional sections. The updates are viewable in the commit history.

### Meaningful commit history if a Git repository is used.

I am a proponent of helpful and verbose commit messages. A commit history should be able to be clear and concise. And it should be able to tell a story of how the application grew, if one were to follow it. Things like, adding a new tool to this project, would be nicely packaged up in a Pull/Merge Request, such that it could be referenced when adding another.

I was a release manager once upon a time and needed the commit logs to properly ascertain what was in a new release... a good commit history was critical.

And then of course debugging some new bug that showed up in a release... I have always found checking recent commits to be critical in finding where to look in the code.

The git repo used here is an umbrella project for the various experimental projects I made along the way while I kicked the tires on both LLM AI Agents/ChatBots and Python.

## Bonus Points

### Implement a simple frontend or chat interface for user interactions.

At first, hardcoded queries into program execution. Eventually used LangGraph Studio to send queries along in real-time. Subsequent TODO item to reference [How to test a LangGraph app locally](https://langchain-ai.github.io/langgraph/cloud/deployment/test_locally/) on ideas to create a frontend interface (at least a CLI).

### Add support for multiple tool integrations.

The LangGraph template comes with a good tools entrypoint for adding multiple. Subsequent TODO item to move preschool swim tool to its own package (perhaps a tools package) and better enable more tools to be added via independent packages instead of all going into `src/react_agent/tools.py`.

### Allow users to configure or extend the chatbot with additional tools.

This was an intriguing idea that I did not have a chance to pursue. Is this runtime tool extension by a user while in conversation with the chatbot?

### Implement logging or analytics to track chatbot interactions.

Made use of LangSmith integrated into LangGraph Studio to track chatbot interactions during development. Also made use of printing out to terminal from serverside, so moving those prints to logs would be the next move.

### Provide a Dockerfile and/or deployment instructions.

Did not explore specific python/chatbot deployment during this project, but have worked closely with deployments for Kubernetes operators and Spring Boot apps (so, Docker, K8s, Maven, Jenkins, Concourse CI, GitLab Pipelines etc)
