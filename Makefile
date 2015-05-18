.PHONY:	build apishell

build:
	docker build -t jimrybarski/raspberrypid-api -f Dockerfile.backend .; docker build -t jimrybarski/raspberrypid-site -f Dockerfile.frontend .;

shellback:	build
	docker run -it jimrybarski/raspberrypid-api bash

shellfront:
	docker run -it jimrybarski/raspberrypid-site bash
