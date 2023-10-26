# AI-Choose-Your-Own-Adventure-Game
## Setup
1. Copy your Astra DB auth JSON file into this directory and rename `token.json`.
2. Copy your Astra DB secure connect bundle into this directory and rename `scb.zip`.
3. Within your Python env of choice, run
    ```Python
    pip install chainlit cassio cassandra-driver langchain  openai
    ```
4. To load the UI, run
    ```Python
    chainlit run tutorial.py
    ```