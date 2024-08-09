.PHONY: build up down deploy clean logs

build:
	docker compose build
up:
	docker compose up -d
down:
	docker compose down
restart:
	docker compose down && sleep 2 && docker compose up
clean:
	docker compose down -v --rmi all
logs:
	docker compose logs -f

deploy:	build up

reset: clean deploy
