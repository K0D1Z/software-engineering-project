# Mini-bank: database

## Start / stop

    docker compose up -d   #start       
    docker compose down    #stop (z -v czyści bazę)

## psql schell

    docker compose exec db psql -U minibank -d minibank    #wejście do schella

## demo run

    uv sync
    uv run python src/demo_transfer.py
