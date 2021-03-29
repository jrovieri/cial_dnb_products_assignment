# About
The crawler was developed using Scrapy Framework and deployed in a Docker container.

# Instructions
No need to clone this repository. The docker image is published on DockerHub.
```bash
  cat websites.txt | docker run -i jrovieri/cial_dnb_products_assignment
```

To run the app outside the Docker container.
```bash
  unzip cial_dnb_products_assignment
  cd cial_dnb_products_assignment
```

Create an environment and activate
```bash
  python3 -m venv .env
  source ./env/bin/activate
```

Install dependencies
```bash
  pip install -r requirements.txt
```

Execute the app
```bash
  cat websites.txt | python main.py
```