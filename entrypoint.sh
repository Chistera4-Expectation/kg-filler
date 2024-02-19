set -x

function get_secret() {
    yq -r .$1 $SECRETS_PATH
}

function restore_all_caches() {
    git fetch --all
    for BRANCH in $(git branch -r | tail -n +2 | cut -c 3-); do
        git checkout $BRANCH -- '*.yml'
        git reset *.yml
    done
}

# configure git user locally
git config --global user.name $(get_secret git.user)
git config --global user.email $(get_secret git.email)

# configure git to look for credentials in $HOME/.git-credentials
git config --global credential.helper store

# set up environment variables for kg-filler
export OPENAI_API_KEY=$(get_secret openai.api_key)
export HUGGING_USERNAME=$(get_secret hugging.username)
export HUGGING_PASSWORD=$(get_secret hugging.password)

# set up local variables for working with git
GH_TOKEN=$(get_secret github.token)
GH_USER=$(get_secret github.user)
GH_REPO=$(get_secret github.data_repo)
GH_URL="https://$GH_USER:$GH_TOKEN@github.com/$GH_REPO"
BRANCH=experiments/$(hostname)

if [[ "$POST_MORTEM" = "true" ]]; then
    /usr/bin/bash 
else
    # set up git credentials from secrets
    echo $GH_URL >> $HOME/.git-credentials

    # clone the data repository in ./data/
    git clone $GH_URL data

    # focusing on the data repository...
    pushd data
    # put on begin commit
    git checkout begin
    # create a new branch for this experiment
    git checkout -b $BRANCH
    # restore all the yaml files from all branches
    if [[ "$RESTORE_ALL_CACHES" = "true" ]]; then
        restore_all_caches
    fi
    popd

    # run the kg-filler
    python -m kgfiller

    # push the experiment branch on github
    cd data
    git push origin $BRANCH
fi
