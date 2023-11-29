# Knowledge-Graph Filler

Prerequisites:
- sub-directory `data/` should be a Git submodule
- sub-directory `data/` should contain an OWL file named `ontology.owl`
- the user should have an API key from <https://platform.openai.com/account/api-keys>
- the environment variable `OPENAI_API_KEY` should be set and assigned to the user's API key above
- Python `3.11.x`
- Restoring dependencies with `pip install -r requirements.txt`

## Functioning

By running `python -m kgfiller` the script in `kgfiller/__main__.py` is run.
The script's goal is to fill the ontology file in `data/ontology.owl` with instances and relations among them.
To do so, the script may query OpenAI's LLMs multiple times (hence consuming the user's credit!).

Queries to OpenAI are cached into the `data/` folder, as `.yml` files.
In this way, from the second time on the same query is performed, the cached is reused (hence saving the user's credit!).
The script would also perform commits into the `data/` repository, after each update to the ontology.
Cache files are committed as well.
In this way, users may inspect the list of automatic additions to the ontology, by simply reading the commit lists in `data/`.

## Workflows

> __Insight__: each "filling process" should have its own Git branch on the `data/` repository!

### Bootstrapping a new filling process on a virgin ontology

1. Move into the `data/` directory
    ```bash
    cd data
    ```

2. Restore the state of the repository to the "classes only" state
    ```bash
    git checkout begin
    ```
    (`begin` is a tag to the initial commit were the ontology only contains classes but no instances, nor relations)

3. Start a new branch for your filling process (say, `my-branch`)
    ```bash
    git checkout -b my-branch
    ```

4. [Optional] Restore cache files from another branch (say, `other-branch`)
    ```bash
    git checkout other-branch -- '*.yml'
    ```
    This may be useful if one wants to reuse the cache file from some other thread of work

5. Reset the Git stage to avoid committing all edits in a single commit
    ```bash
    git reset .
    ```

6. Move back to the `kg-filler` project directory
    ```bash
    cd ..
    ```

7. Spawn the filling process
    ```bash
    python -m kgfiller
    ```

## Simplified workflow with Docker

1. Ensure you have Docker and Docker Compose installed on your machine

2. Create a `secrets.yml` file in the root of the project, with the following content:
    ```yml
    git:
        user: Your name
        email: Your email
    github:
        user: Your GitHub username
        token: Your GitHub personal access token (with `repo` scope, at least)
        data_repo: Chistera4-Expectation/kg-filler
    hugging:
        username: Your HuggingFace username
        password: Your HuggingFace password
    openai:
        api_key: Your OpenAI API key
    ```
   
3. Run the following command to start experiments
   ```bash
   docker-compose up [--build] [EXPERIMENT_NAME]
   ```
   
   where:
   - `--build` is optional, and forces the Docker image to be rebuilt
   - `EXPERIMENT_NAME` is optional, and specifies the name of the experiment to run
     (experiments names are the names of the services in the `docker-compose.yml` file)

4. Experiments will be performed in parallel, and eventually pushed on the `github.data_repo` repository specified in `secrets.yml`.
   Each experiment will be pushed onto a new branch, namely `experiment/EXPERIMENT_HASH`
