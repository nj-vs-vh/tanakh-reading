export GIT_COMMIT_ID=$(git describe --always)
npm run build
rsync -azP public/ know:projects/tanakh-reading/frontend/public/
