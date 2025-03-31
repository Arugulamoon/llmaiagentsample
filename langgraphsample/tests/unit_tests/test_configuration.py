from react_agent.configuration import Configuration
from react_agent import prompts


def test_configuration_empty():
    Configuration.from_runnable_config({})

def test_configuration_defaults():
    cfg = Configuration.from_runnable_config({})
    assert cfg.system_prompt == prompts.SYSTEM_PROMPT
    assert cfg.model == "openai/gpt-4-turbo-preview"
    assert cfg.max_search_results == 10

def test_configuration_configurable():
    cfg = Configuration.from_runnable_config({
        "configurable": {"max_search_results": 2}
    })
    assert cfg.max_search_results == 2
