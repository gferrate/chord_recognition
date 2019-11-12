ECR_REPOSITORY=361851569610.dkr.ecr.us-east-1.amazonaws.com/chord-recognition

TAG=${1:-latest}
LOG_LEVEL=${2:-INFO}
docker stop chord-recognition
docker rm chord-recognition
`aws ecr get-login --no-include-email`
docker pull ${ECR_REPOSITORY}:${TAG}
docker run --net bridge -m 0b -p 5000:8000 \
        -v /chord-recognition/db:/app/src/db \
        -v /var/log/chord-recognition:/var/log/chord-recognition \
        -e BUCKET=chord-recognition-bucket \
        -d --name chord-recognition ${ECR_REPOSITORY}:${TAG} uwsgi
