ECR_REPO=361851569610.dkr.ecr.us-east-1.amazonaws.com/chord-recognition


shell:
	python src/manage.py shell_plus

runserver:
	python src/manage.py runserver

build:
	`aws ecr get-login --no-include-email`
	docker build -t chord-recognition:${tag} -f Dockerfile .
	docker tag chord-recognition:${tag} $(ECR_REPO):${tag}
	docker push $(ECR_REPO):${tag}
