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
