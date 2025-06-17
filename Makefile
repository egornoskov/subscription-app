DC = docker compose
STORAGES_FILE = docker_compose/storages.yaml
EXEC = docker exec -it
DB_CONTAINER = subscriptions_db
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = subscriptions_main_app
MANAGEPY = python manage.py
BOT_FILE = docker_compose/tg_bot.yaml
BOT_CONTAINER = subscriptions_telegram_bot

NETWORK_NAME = network_for_subscriptions

.PHONY: network
network:
	@docker network inspect ${NETWORK_NAME} >/dev/null 2>&1 || docker network create ${NETWORK_NAME}


.PHONY: clean-network
clean-network:
	-docker network rm ${NETWORK_NAME}	||	true


.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} ${ENV} up -d

.PHONY: storages-logs
storages-logs:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGES_FILE} down

.PHONY: database
database:
	${EXEC} ${DB_CONTAINER} psql -U postgres -d mydatabase

.PHONY: app
app:
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} ${ENV}  up --build -d

.PHONY: logs
logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} ash

.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} migrate

.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} makemigrations

.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} createsuperuser

.PHONY: collectstatic
collectstatic:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} collectstatic

.PHONY: show
show:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} showmigrations

.PHONY: reload
reload:
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} down
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} ${ENV} up --build -d
	${DC} -f ${BOT_FILE} down
	${DC} -f ${BOT_FILE} ${ENV} up --build -d

.PHONY: bot
bot:
	${DC} -f ${BOT_FILE} ${ENV} up --build -d

.PHONY: bot-down
bot-down:
	${DC} -f ${BOT_FILE} down

.PHONY: bot-shell
bot-shell:
	${EXEC} ${BOT_CONTAINER} bash

.PHONY: bot-logs
bot-logs:
	${LOGS} ${BOT_CONTAINER} -f

.PHONY: all
all: network
	@echo "Starting all services (App, Storages, Bot)..."
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} -f ${BOT_FILE} ${ENV} up --build -d

.PHONY: down-all
down-all:
	@echo "Stopping all services (App, Storages, Bot)..."
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} -f ${BOT_FILE} down

.PHONY: restart-all
restart-all: down-all up-all
	@echo "Restarting all services (App, Storages, Bot)..."

.PHONY: logs-all
logs-all:
	@echo "Showing combined logs for all services..."
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} -f ${BOT_FILE} logs -f