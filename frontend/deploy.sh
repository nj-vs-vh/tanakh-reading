export GIT_COMMIT_ID=$(git describe --always)
npm run build
surge public torah-reading.surge.sh
