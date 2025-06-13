go:
	docker compose up -d --build
test:
	APP_MODE=test docker compose up --build --abort-on-container-exit;
	docker compose down 
logs:
	docker logs zlecenia-foldery -f
kill:
	docker kill zlecenia-foldery
	docker image rm zlecenia-foldery --force
