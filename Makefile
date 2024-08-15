YELLOW=\033[33m
RESET=\033[0m

start:
	@echo 'BOT_TOKEN=""' > .env
	@printf "$(YELLOW)Добавили .env файл, не забудь добавить токен бота туда$(RESET)\n"