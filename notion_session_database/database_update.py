import os
from dotenv import load_dotenv
from typing import Dict, List
from notion_client import Client

# Load environment variables from .env file
load_dotenv()

# Initialize Notion client with the API key from .env
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # Notion API key
ROOT_DIR = os.getenv("ROOT_DIR")  # Root directory of your data
DATABASE_ID = os.getenv("DATABASE_ID")  # Notion database ID

# Initialize Notion client
notion = Client(auth=NOTION_API_KEY)


def get_kilosort_folder(session_path: str) -> str:
    """Find the Kilosort folder in a session directory."""
    for item in os.listdir(session_path):
        if os.path.isdir(os.path.join(session_path, item)) and item.startswith(
            "Kilosort"
        ):
            return os.path.join(session_path, item)
    return None


def get_session_status(session_path: str, session_name: str) -> str:
    """Determine the processing status of a session and identify missing files."""
    kilosort_path = get_kilosort_folder(session_path)
    if not kilosort_path:
        return "sessions to be preprocessed"

    phy_path = os.path.join(kilosort_path, ".phy")
    if not os.path.exists(phy_path):
        return "sessions to spike sort"

    required_files = [
        f"{session_name}.animal.behavior.mat",
        "anatomical_map.csv",
        f"{session_name}.cell_metrics.cellinfo.mat",
        f"{session_name}.ripples.events.mat",
        f"{session_name}.spikes.cellinfo.mat",
    ]
    all_files = os.listdir(session_path)

    # Identify missing files
    missing_files = [file for file in required_files if file not in all_files]

    if not missing_files:
        return "ready for analysis"

    # Add comment for missing files
    return f"sessions to post-process: missing {', '.join(missing_files)}"


def get_sessions_in_project(root_dir: str) -> List[Dict]:
    """Traverse the folder structure and locate session folders."""

    # List of animal IDs to exclude
    exclude_animal_ids = ["radial_maze_behavior", "HP02"]

    sessions = []
    for animal_id in os.listdir(root_dir):
        animal_path = os.path.join(root_dir, animal_id)

        # Skip non-directory items or excluded animal IDs
        if not os.path.isdir(animal_path) or animal_id in exclude_animal_ids:
            continue
        # Only process folders directly under `animal_path`
        for session_name in os.listdir(animal_path):
            session_path = os.path.join(animal_path, session_name)
            if os.path.isdir(session_path):  # Ensure it's a directory
                status = get_session_status(session_path, session_name)
                comment = status.split(": missing ")[1] if "missing" in status else ""
                sessions.append(
                    {
                        "animal_id": animal_id,
                        "session_name": session_name,
                        "status": status.split(":")[0],  # Status without the comment
                        "path": session_path,
                        "comment": comment,  # Add the comment for missing files
                    }
                )
    return sessions


def get_existing_entry(animal_id: str, session_name: str) -> dict:
    """Check if a session entry already exists in the database."""
    query = {"filter": {"property": "Animal ID", "title": {"equals": animal_id}}}

    # Query the database for existing pages with the same Animal ID and Session Name
    existing_entries = notion.databases.query(database_id=DATABASE_ID, **query).get(
        "results", []
    )

    # Check if any entry matches both the Animal ID and Session Name
    for entry in existing_entries:
        properties = entry["properties"]
        existing_session_name = properties["Session Name"]["rich_text"][0]["text"][
            "content"
        ]
        if existing_session_name == session_name:
            return entry  # Found an existing entry

    return None  # No matching entry found


def create_or_update_database_entry(session: Dict):
    """Create or update a database entry in Notion."""

    # Check if this session already exists in the database
    existing_entry = get_existing_entry(session["animal_id"], session["session_name"])

    # Get session status and missing files
    missing_files_comment = session.get(
        "comment", ""
    )  # Optional field for missing files

    if existing_entry:
        # Update the existing entry
        page_id = existing_entry["id"]
        notion.pages.update(
            page_id=page_id,
            parent={"database_id": DATABASE_ID},
            properties={
                "Animal ID": {"title": [{"text": {"content": session["animal_id"]}}]},
                "Session Name": {
                    "rich_text": [{"text": {"content": session["session_name"]}}]
                },
                "Status": {"select": {"name": session["status"]}},
                "Path": {"url": session["path"]},
                "Notes": {"rich_text": [{"text": {"content": missing_files_comment}}]},
            },
        )
    else:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Animal ID": {"title": [{"text": {"content": session["animal_id"]}}]},
                "Session Name": {
                    "rich_text": [{"text": {"content": session["session_name"]}}]
                },
                "Status": {"select": {"name": session["status"]}},
                "Path": {"url": session["path"]},
                "Notes": {"rich_text": [{"text": {"content": missing_files_comment}}]},
            },
        )


def get_database_properties(database_id: str):
    """Retrieve and print properties of a Notion database."""
    response = notion.databases.retrieve(database_id=database_id)
    properties = response.get("properties", {})
    for prop_name, prop_details in properties.items():
        print(f"Property Name: {prop_name}")
        print(f"Type: {prop_details['type']}")
        print("-" * 30)
    return properties


def main():
    """Main function to update the Notion database."""
    # Run the function
    sessions = get_sessions_in_project(ROOT_DIR)
    for session in sessions:
        create_or_update_database_entry(session)


if __name__ == "__main__":
    main()
