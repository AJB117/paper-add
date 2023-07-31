# shebang here

import os
import argparse
import pickle
import requests
import bs4

from typing import List, Tuple
from dataclasses import dataclass
from notion_client import Client, APIResponseError

notion = Client(auth=os.environ["NOTION_TOKEN"])
paper_db_id = os.environ["PAPER_ADD_PAPERS_ID"]
tags_db_id = os.environ["PAPER_ADD_TAGS_ID"]

@dataclass
class Args:
    arxiv_url: str
    topics: List[str]
    notes: str

def get_title_and_year(arxiv_url: str) -> Tuple[str, str]:
    soup = bs4.BeautifulSoup(requests.get(arxiv_url).text, features="html.parser")
    title = soup.find_all("h1", {
        "class": ["title", "mathjax"]
    })[0].contents[-1]

    date = soup.find_all("div", {
        "class": ["dateline"]
    })[0].contents[-1].split("Submitted on")[-1][-5:-1]

    return title, date

def get_or_create_rel_id(rel_name: str) -> str:
    rel = notion.databases.query(tags_db_id, **{
        "filter": {
            "property": "Name",
            "title": {
                "equals": rel_name
            }
        }
    })
    if not rel["results"]:
        try:
            print(f"Creating new relation \"{rel_name}\"...")
            notion.pages.create(
                **{
                    "parent": {
                        "database_id": tags_db_id,
                    },
                    "properties": {
                        "Name": [
                            {
                                "text": {
                                    "content": rel_name
                                }
                            }
                        ]
                    }
                }
            )
        except Exception as e:
            print(f"Could not create new relation \"{rel_name}\":")
            print(e)

    return rel["results"][0]["id"]

def get_rel_ids(rel_names: List[str]) -> List[str]:
    rels = [get_or_create_rel_id(rel_name) for rel_name in rel_names]
    return rels

def main(args: Args) -> None:
    arxiv_url = args.arxiv_url
    topics = args.topics
    notes = args.notes

    try:
        rel_list = pickle.load(open("request.pkl", "rb"))
    except Exception:
        rel_list = [{"id": rel_id} for rel_id in get_rel_ids(topics)]
        pickle.dump(rel_list, open("request.pkl", "wb"))

    try:
        title, year = get_title_and_year(arxiv_url)
        obj = {"parent": {
                    "database_id": paper_db_id
                },
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    },
                    "Year": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": year
                                }
                            }
                        ]
                    },
                    "Link": {
                        "url": arxiv_url
                    },
                    "Notes": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": notes
                                }
                            }
                        ]
                    },
                    "Read": {
                            "checkbox": False
                    },
                    "Topics": {
                        "relation": rel_list
                    },
                }
            }
        notion.pages.create(
            **obj
        )

    except APIResponseError as error:
        print(error)
        exit()

    print("Success!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arxiv_url", type=str, required=True, help="URL of the arXiv paper")
    parser.add_argument("--topics", nargs="+", required=True, help="List of topics to put the paper under")
    parser.add_argument("--notes", type=str, required=True, help="Any miscellaneous notes to add")

    main(Args(**vars(parser.parse_args())))