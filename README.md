# paper-add

A quick script for adding new arXiv papers to Notion.

## How to use

1. Set the environment variable `NOTION_TOKEN` to your Notion integration's secret (see [here](https://www.notion.so/help/create-integrations-with-the-notion-api) for instructions on how to set this up).
2. If they don't already exist, create 2 databases: one for your papers, and another for your Topics tags. Set their IDs as the environment variables `PAPER_ADD_PAPERS_ID` and `PAPER_ADD_TAGS_ID`, respectively. You can get those IDs from the database URLs.
3. Install dependencies listed in `requirements.txt`. A new virtual environment is recommended.
4. Edit the shebang line in `paper-add.py` and add this directory's path to your system PATH.

If you want to add new columns, you'll have to edit `paper-add.py` yourself.
