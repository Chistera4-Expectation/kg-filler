set -x

function get_secret() {
    yq -r .$1 $SECRETS_PATH
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
BRANCH=experiments/$(hostname)

# set up git credentials from secrets
echo "https://$GH_USER:$GH_TOKEN@github.com/$GH_REPO" >> $HOME/.git-credentials

# focusing on the data repository...
pushd data
# enforce https authentication for github
git remote set-url origin "https://github.com/$GH_REPO"
# create a new branch for this experiment
git checkout -b $BRANCH
popd

# run the kg-filler
python -m kgfiller

# push the experiment branch on github
cd data
git push origin $BRANCH
