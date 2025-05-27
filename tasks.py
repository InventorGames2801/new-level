from invoke import task


@task
def dev(c):
    c.run("uvicorn app.main:app --host 0.0.0.0 --port 8000")


@task
def prod(c):
    c.run("docker compose up -d")
