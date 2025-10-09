# Nome do serviço web no docker-compose
WEB=web
DOCKER= docker compose exec $(WEB)
.PHONY: up migrate createsuperuser shell test down


install:
	docker compose exec web poetry install --no-root
# Sobe containers
up:
	docker compose up --build -d

# Para containers
down:
	docker compose down

# Aplica migrations
migrate:
	docker compose exec $(WEB) python manage.py migrate

# Cria superusuário
createsuperuser:
	docker compose exec $(WEB) python manage.py createsuperuser

# Abre shell Django
shell:
	docker compose exec $(WEB) python manage.py shell

# Roda servidor em modo dev (não recomendado para produção)
run:
	docker compose exec $(WEB) python manage.py runserver 0.0.0.0:8000

# Cria as migrações automaticamente (não aplica ainda)
makemigrations:
	docker compose exec $(WEB) python manage.py makemigrations

# Roda testes
test:
	docker compose exec $(WEB) python manage.py test

build:
	docker compose up --build

# Uso: make add pkg=colorama
add:
ifeq ($(strip $(PKG)),)
	$(error Você precisa passar um pacote. Ex: make add PKG=colorama)
endif
	docker compose exec web poetry add $(PKG)