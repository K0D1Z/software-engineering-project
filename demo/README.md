# Mini-bank: database

## Start / stop

    docker-compose up -d   # start       
    docker-compose down    # stop (-v cleans database)

## psql schell

    docker-compose exec db psql -U minibank -d minibank    # enter the schell

## demo run

    uv sync
    uv run src/demo_simple.py
    uv run src/demo_concurrency.py   # simultaneous transfers (threads)
