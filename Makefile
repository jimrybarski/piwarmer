.PHONY:	build apishell

build:
	docker build -t jimrybarski/raspberrypid-backend -f Dockerfile.backend .; docker build -t jimrybarski/raspberrypid-site -f Dockerfile.frontend .;

shellback:	build
	docker run -it jimrybarski/raspberrypid-backend bash

shellfront:	build
	docker run -it jimrybarski/raspberrypid-site bash

front:
	docker run -p 80:80 --net="host" --rm -it jimrybarski/raspberrypid-site

back:
	docker run --net="host" --rm -it jimrybarski/raspberrypid-backend python2.7 backendmain.py

api:
	docker run -p 8089:8089 --net="host" --rm -it jimrybarski/raspberrypid-backend python2.7 apimain.py
