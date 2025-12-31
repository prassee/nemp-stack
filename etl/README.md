## How to run 

### Get new credentials
docker-compose logs polaris | grep "root principal credentials"

### Update setup_polaris.py and main.py with new credentials
### Then run:
cd etl && uv run setup_polaris.py && uv run main.py