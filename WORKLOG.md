# Work Log

## Monday, March 24th, 2025
* Interview with Vittorio Cellucci; learned of LLM AI Agents, LangGraph and Ollama
* Followed up by reading on LLM AI Agents and LangChain
  * Developed appreciation for possibilities of the technology and how powerful it can be
  * Saw some similarities between LangChain and Kubernetes Operator projects
    * Tech different, but developing an app/agent, to "live" within a context and with agency to effect changes

## Tuesday, March 25th, 2025
* Started to look at docs in more detail; started following code; LangChain tutorials etc
* Started to try out tutorials
  * getting a sense of llms, loaders, splitters, chains, prompts

## Wednesday, March 26th, 2025
* Started to build out a prototype RAG Chain for this project: local-activities
* Explored various loaders to try to inform LLM about the activity schedule defined in an HTML table; not much success

## Thursday, March 27th, 2025
* Largely focused on learning and writing Python code to fetch and parse html pages manually instead of using the loaders
* Python syntax pretty decent and workable
* Wrote Python functions (`_parse_*`)

## Friday, March 28th, 2025
* Switched from Ollama to OpenAI LLM; with data being provided to LLM after being preprocessed and possibly switch from free/local to paid OpenAI LLM, LLM began to properly respond with a correct preschool swim time at Walter Baker
* Added an additional facility webpage to parse that follows the same template (Minto Barrhaven) and made some parsing updates to handle additional edge cases
  * Moved location field into being at same level as activity/timeslot as opposed to being at page level; I suspect LLM could instead be better instructed on the data schema as a better fix
* Added subsequent queries to test correct time slot responses for different facilities
* LangChain Prototyping phase completed

## Saturday, March 29th, 2025
* Started looking at LangGraph tutorials
* Exploring LangGraph Studio and the templates
* Started new project using base react template with tool extensions
* Integrated Ottawa Recreation Facility webpage scraper code as tool
* Validated workflows:
  * Memory ("hi, my name is nicholas", "what is my name?")
  * Search tool usage ("what was the score in the last Edmonton Oilers NHL hockey game?")
  * Ottawa Recreation Facility activity search ("when is the next preschool swim?")

## Sunday, March 30th, 2025
* Tried simple weather api; had a notion to have LLM first check weather, if sunny, then tool to return local parks, otherwise if rainy, then return indoor preschool swim. Added to the roadmap!

## Monday, March 31, 2025
* Added tests
* Focused on Documentation
