check:
	git add '.'
	pre-commit run --all-files

prod:
	nohup uvicorn app.main:app --host 0.0.0.0 --port 3389 &

dev:
	ENV=dev uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-server:
	ENV=prod uvicorn app.main:app --host 0.0.0.0
