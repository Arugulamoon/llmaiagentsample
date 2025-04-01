# LangGraph Sample

This LLM AI Agent responds to queries from a user. It includes tools for 1) performing a web search (for current news etc) and 2) determining times when specific activities are available at a couple of South Ottawa recreation facilities.

This project was bootstrapped using the [LangGraph ReAct Agent Template](https://github.com/langchain-ai/react-agent).

The template showcases a [ReAct agent](https://arxiv.org/abs/2210.03629) implemented using [LangGraph](https://github.com/langchain-ai/langgraph), designed for [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio). ReAct agents are uncomplicated, prototypical agents that can be flexibly extended to many tools.

![Graph view in LangGraph studio UI](./static/studio_ui.png)

The core logic, defined in `src/react_agent/graph.py`, demonstrates a flexible ReAct agent that iteratively reasons about user queries and executes actions, showcasing the power of this approach for complex problem-solving tasks.

## What it does

The ReAct agent:

1. Takes a user **query** as input
2. Reasons about the query and decides on an action
3. Executes the chosen action using available tools
4. Observes the result of the action
5. Repeats steps 2-4 until it can provide a final answer

By default, it's set up with a basic set of tools, but can be easily extended with custom tools to suit various use cases.

### Provided Tool: Tavily Search

This tool came pre-built into the template.

### Custom Tool: Ottawa Recreation Facility Activity (Preschool Swim) Search

Fetches the webpage for 2 facilities (Walter Baker and Minto Barrhaven), parses the html and provides the relevant facility activities and times to the LLM. The implementation is a first pass and quite naive. Subsequent TODO items would be to formalize it as a Class and harden the data structure/better set metadata for the LLM to make the retrieval more precise.

## Getting Started

Assuming you have already [installed LangGraph Studio](https://github.com/langchain-ai/langgraph-studio?tab=readme-ov-file#download), to set up:

1. Create a `.env` file.

```bash
cp .env.example .env
```

2. Define required API keys in your `.env` file.

The primary [search tool](./src/react_agent/tools.py) [^1] used is [Tavily](https://tavily.com/). Create an API key [here](https://app.tavily.com/sign-in).

### Setup Model

The defaults values for `model` are shown below:

```yaml
model: openai/gpt-4-turbo-preview
```

Follow the instructions below to get set up, or pick one of the additional options.

#### OpenAI

To use OpenAI's chat models:

1. Sign up for an [OpenAI API key](https://platform.openai.com/signup).
2. Once you have your API key, add it to your `.env` file:

```
OPENAI_API_KEY=your-api-key
```

#### Anthropic

To use Anthropic's chat models:

1. Sign up for an [Anthropic API key](https://console.anthropic.com/).
2. Once you have your API key, add it to your `.env` file:

```
ANTHROPIC_API_KEY=your-api-key
```

3. Customize whatever you'd like in the code.
4. Open the folder LangGraph Studio!

## Install dependencies

```bash
python -m pip install .
```

## Running tests

```bash
make test
```

## Running the application

```bash
# Start langgraph server to run and interact with
langgraph dev
# will load the web client into the browser
```

## Usage

From the web client, in the bottom left, type in the following messages to see the use cases:
  * Memory ("hi, my name is nicholas" and then "what is my name?")
  * Search tool usage ("what was the score in the last Edmonton Oilers NHL hockey game?")
  * Ottawa Recreation Facility activity search ("when is the next preschool swim?")

## How to customize

1. **Add new tools**: Extend the agent's capabilities by adding new tools in [tools.py](./src/react_agent/tools.py). These can be any Python functions that perform specific tasks.
2. **Select a different model**: You can select a compatible chat model using `provider/model-name` via configuration. Example: `openai/gpt-4-turbo-preview`.
3. **Customize the prompt**: We provide a default system prompt in [prompts.py](./src/react_agent/prompts.py). You can easily update this via configuration in the studio.

You can also quickly extend this template by:

- Modifying the agent's reasoning process in [graph.py](./src/react_agent/graph.py).
- Adjusting the ReAct loop or adding additional steps to the agent's decision-making process.

## Development

While iterating on your graph, you can edit past state and rerun your app from past states to debug specific nodes. Local changes will be automatically applied via hot reload. Try adding an interrupt before the agent calls tools, updating the default system message in `src/react_agent/configuration.py` to take on a persona, or adding additional nodes and edges!

Follow up requests will be appended to the same thread. You can create an entirely new thread, clearing previous history, using the `+` button in the top right.

You can find the latest (under construction) docs on [LangGraph](https://github.com/langchain-ai/langgraph) here, including examples and other references. Using those guides can help you pick the right patterns to adapt here for your use case.

LangGraph Studio also integrates with [LangSmith](https://smith.langchain.com/) for more in-depth tracing and collaboration with teammates.

[^1]: https://python.langchain.com/docs/concepts/#tools
