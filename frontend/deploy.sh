export GIT_TAG=$(git describe --tags --dirty="+")
npm run build
surge public torah-reading.surge.sh
