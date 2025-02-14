# stark-challange
This repository contains the code for the Stark Challange.

Its a simple webhook that creates invoices in Stark Bank and receives the invoice data from Stark Bank and publishes it to a queue for further processing.

## Getting Started

1. Clone the repository
2. Install the dependencies
3. Run the server
4. Test the webhook

## Starting dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Preparing the local environment

```bash
make docker-build
make docker-run
``` 

## Running the commands
Run the scrip to start up 8 to 12 invoices. 
```bash
make run-invoice-scheduler
``` 

Run the script to start up the queue worker
```bash
make run-queue-worker
```


