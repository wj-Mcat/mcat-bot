version=$(cat VERSION)
docker build -t mcat-bot:${version} -t mcat-bot:latest .