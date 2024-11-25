# Notion Session Database

This tool allows you to manage and update the processing status of a dataset in Notion. It scans a directory containing data for different participants/subjects and their corresponding sessions and updates a Notion database with session statuses (e.g., "sessions to be preprocessed", "sessions to spike sort", etc.).

## Features
- Automatically determines session status based on directory contents.
- Updates a Notion database with session details and their processing status.
- Supports environment configuration via `.env` file for storing sensitive information like API keys and session paths.

## Requirements
- Python 3.9 or higher
- A Notion API integration token
- A Notion database to store session details

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ryanharvey1/notion_session_database.git
cd notion_session_database
```

### 2. Install Dependencies
You can use pip to install the required dependencies. First, ensure you have a conda environment or equivalent environment set up:

```bash
conda create -n notion_session_database python=3.9
conda activate notion_session_database
```

Then, install the dependencies:

```bash
pip install .
```

### 3. Create an .env File
In the root directory of the project, create a .env file to store your sensitive information:
    
```bash
touch .env
```

Add the following content to your .env file, replacing the placeholders with your own values:

```bash
NOTION_API_KEY=your_notion_api_key
ROOT_DIR=path_to_your_data_directory
DATABASE_ID=your_notion_database_id
```

* NOTION_API_KEY: Your Notion integration token (you can get it from [Notion Developers](https://developers.notion.com/docs/authorization)).
* ROOT_DIR: The root directory where your session data is stored (e.g., U:/data/my_project).
* DATABASE_ID: The ID of the Notion database where the session data will be stored.

### 4. Set Up Notion Database

Ensure that your Notion database is set up with the following properties:

* Animal ID (Type: Title)
* Session Name (Type: Rich Text)
* Status (Type: Select, with options "sessions to be preprocessed", "sessions to spike sort", "sessions to post-process", and "ready for analysis")
* Path (Type: URL)

You can find your database ID by opening your database in Notion and copying the part of the URL after the last /.

Example URL:
https://www.notion.so/24333fxca51080139509b5759d5776ec?v=5dec6d11v7f28999af283f5204cb6a4c

The database ID will be the numbers following the ?v=, for example:

Database ID: 24333fxca51080139509b5759d5776ec

### 5. Running the Script
Once your environment is set up and your .env file is configured, you can run the script to update the Notion database:

```bash
python database_update.py
```

The script will:

* Traverse the data directory (ROOT_DIR).
* Check the status of each session based on the contents of its folder.
* Create or update corresponding entries in your Notion database.

### Troubleshooting
If you encounter any issues, double-check the Notion database properties and ensure the .env file contains the correct information.
If you see duplicate entries, verify that your session directories are properly organized and that the script is correctly identifying the sessions.

### Notes
This tool is designed to work with a specific directory structure and session naming convention. You may need to modify the script to suit your specific data organization.
