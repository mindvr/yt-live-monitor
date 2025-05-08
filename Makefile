PYTHON := .venv/bin/python

get-id:
	$(PYTHON) -m src.main get-channel-id https://www.youtube.com/@DigitalFoundry

# Check Live (DF - probably not)
check-live-not:
	$(PYTHON) -m src.main check-live UC9PBzalIcEQCsiIkq36PyUA

# Check live (RCG - probably yes)
check-live-yes:
	$(PYTHON) -m src.main check-live UCj-Xm8j6WBgKY8OG7s9r2vQ

run-server:
	$(PYTHON) -m src.main serve

# build docker image latest and run a container

docker-build:
	docker build -t yt-live-checker:latest .

docker-run:
	docker run --name yt-live-checker -p 8080:8080 yt-live-checker:latest