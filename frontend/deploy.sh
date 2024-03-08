export GIT_COMMIT_ID=$(git describe --always)
npm run build

echo "Publishing to Surge"
surge public torah-reading.surge.sh

echo "Publishing to my website"
rsync -azP public/ knor:tanakh-reading/frontend/public/
