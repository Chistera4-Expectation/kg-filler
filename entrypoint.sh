set -x
export OPENAI_API_KEY=$(cat $OPENAI_API_KEY_PATH 2> /dev/null)
export HUGGING_USERNAME=$(cat $HUGGING_USERNAME_PATH 2> /dev/null)
export HUGGING_PASSWORD=$(cat $HUGGING_PASSWORD_PATH 2> /dev/null)
pushd data
git checkout -b experiments/$(hostname)
popd
echo python -m kgfiller
cd data
gh auth login --with-token < $GH_TOKEN_PATH
git branch -v
git push origin experiments/$(hostname)
