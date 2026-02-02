.PHONY: install migrate run shell test

install:
	uv sync

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

shell:
	python manage.py shell

test:
	python manage.py test

superuser:
	python manage.py createsuperuser

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete