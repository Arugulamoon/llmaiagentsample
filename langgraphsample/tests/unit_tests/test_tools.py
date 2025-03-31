from bs4 import BeautifulSoup
from react_agent import tools

DAYS_OF_THE_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Clean
def test_clean():
  assert tools._clean("") == ""
  assert tools._clean("foo") == "foo"
  assert tools._clean("  foo  ") == "foo"
  assert tools._clean("foo&nbsp;bar") == "foo bar"
  assert tools._clean("foo\xa0bar") == "foo bar"
  assert tools._clean("foo\n") == "foo"
  assert tools._clean("\tfoo") == "foo"

# Parse Table Caption
# Golang-style table driven test
def test_parse_table_caption():
  tests = [
    {
      "input": "<caption></caption>",
      "want": {},
    },
    {
      "input": "<caption>Walter Baker Sports Centre - Weight and cardio room</caption>",
      "want": {"category": "Weight and cardio room"},
    },
    {
      "input": "<caption>Minto Recreation Complex - Barrhaven - Weight and cardio room</caption>",
      "want": {"category": "Weight and cardio room"},
    },
    {
      "input": "<caption>Walter Baker Sports Centre - swim and aquafit - January 28 to March 21</caption>",
      "want": {
        "category": "swim and aquafit",
        "time_block_start": "January 28",
        "time_block_end": "March 21",
      },
    },
    {
      "input": "<caption>Minto Recreation Complex - Barrhaven - sports - March 17 to June 22</caption>",
      "want": {
        "category": "sports",
        "time_block_start": "March 17",
        "time_block_end": "June 22",
      },
    },
    {
      "input": "<caption>too - many - dashes - return - empty</caption>",
      "want": {},
    },
  ]
  for test in tests:
    assert tools._parse_table_caption(BeautifulSoup(
      markup=test["input"],
      features="html.parser",
    )) == test["want"]

# Parse Table Columns
def test_parse_table_columns_empty():
  assert tools._parse_table_columns(BeautifulSoup(
    markup="<thead></thead>",
    features="html.parser",
  )) == []
  assert tools._parse_table_columns(BeautifulSoup(
    markup="<thead><tr></tr></thead>",
    features="html.parser",
  )) == []
  assert tools._parse_table_columns(BeautifulSoup(
    markup="<thead><tr><th></th></tr></thead>",
    features="html.parser",
  )) == [""]

def test_parse_table_columns_no_blank_first_col():
  thead = BeautifulSoup(
    markup="<thead><tr><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th><th>Sunday</th></tr></thead>",
    features="html.parser",
  )
  assert tools._parse_table_columns(thead) == DAYS_OF_THE_WEEK

def test_parse_table_columns_blank_first_col():
  thead = BeautifulSoup(
    markup="<thead><tr><th></th><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th><th>Sunday</th></tr></thead>",
    features="html.parser",
  )
  assert tools._parse_table_columns(thead) == DAYS_OF_THE_WEEK

# Parse Rows
def test_parse_rows():
  tests = [
    {
      "input": "<tbody></tbody>",
      "want": [],
    },
    {
      "input": "<tbody><tr></tr></tbody>",
      "want": [],
    },
    {
      "input": "<tbody><tr><th></th></tr></tbody>",
      "want": [],
    },
    {
      "input": "<tbody><tr><th>Preschool swim</th></tr></tbody>",
      "want": [],
    },
    {
      "input": "<tbody><tr><th>Preschool swim</th><td>n/a</td></tr></tbody>",
      "want": [],
    },
    {
      "input": "<tbody><tr><th>Preschool swim</th><td>10 - 11am</td></tr></tbody>",
      "want": [
        {
          "location": "mylocation",
          "activity": "Preschool swim",
          "day": "Monday",
          "time_slots": "10 - 11am",
        },
      ],
    },
    {
      "input": "<tbody><tr><th>Preschool swim</th><td>n/a</td><td>10 - 11am</td><td>n/a</td><td>n/a</td><td>n/a</td><td>n/a</td><td>Noon - 2pm</td></tr></tbody>",
      "want": [
        {
          "location": "mylocation",
          "activity": "Preschool swim",
          "day": "Tuesday",
          "time_slots": "10 - 11am",
        },
        {
          "location": "mylocation",
          "activity": "Preschool swim",
          "day": "Sunday",
          "time_slots": "12pm - 2pm",
        },
      ],
    },
  ]
  for test in tests:
    assert tools._parse_rows(BeautifulSoup(
      markup=test["input"],
      features="html.parser",
    ), "mylocation", DAYS_OF_THE_WEEK) == test["want"]

# Parse Page
def test_parse_page():
  page = """
  <!DOCTYPE html>
  <html>
  <h1>Walter Baker Sports Centre</h1>
  <table>
    <caption>Walter Baker Sports Centre - swim and aquafit - January 28 to March 21</caption>
    <thead>
      <tr>
        <th></th>
        <th>Monday</th>
        <th>Tuesday</th>
        <th>Wednesday</th>
        <th>Thursday</th>
        <th>Friday</th>
        <th>Saturday</th>
        <th>Sunday</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>Preschool swim</th>
        <td>n/a</td>
        <td>10 - 11am</td>
        <td>n/a</td>
        <td>n/a</td>
        <td>n/a</td>
        <td>n/a</td>
        <td>Noon - 2pm</td>
      </tr>
    </tbody>
  </table>
  <table>
    <caption>Walter Baker Sports Centre - swim and aquafit - March 22 to June 22</caption>
    <thead>
      <tr>
        <th></th>
        <th>Monday</th>
        <th>Tuesday</th>
        <th>Wednesday</th>
        <th>Thursday</th>
        <th>Friday</th>
        <th>Saturday</th>
        <th>Sunday</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>Preschool swim</th>
        <td>8 - 9am</td>
        <td>8 - 9am</td>
        <td>8 - 9am</td>
        <td>8 - 9am</td>
        <td>8 - 9am</td>
        <td>n/a</td>
        <td>n/a</td>
      </tr>
    </tbody>
  </table>
  </html>
  """
  parsedPage = tools._parse_page(BeautifulSoup(
    markup=page,
    features="html.parser",
  ), "myurl")
  assert parsedPage["location"] == "Walter Baker Sports Centre"
  assert len(parsedPage["time_blocks"]) == 2
  # TODO: Create Helper assert functions for time_block and activity
  assert len(parsedPage["time_blocks"][0]["activities"]) == 2
  assert len(parsedPage["time_blocks"][1]["activities"]) == 5
