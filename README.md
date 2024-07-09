# [IFE](https://www.ife.org.uk) Contact List by distance (unofficial)

This script downloads an [Excel file from the Institution of Fire Engineers (IFE) website](https://www.ife.org.uk/Find-a-UK-Fire-Engineer), geocodes the addresses in the file using [OpenCage Data](https://opencagedata.com), calculates the distance from a target postcode, and then outputs the sorted data to a JSON file and an Excel file.

## Requirements

### OpenCage Data API for Geocoding

You will need an API key from your [OpenCage Data Dashboard](https://opencagedata.com/dashboard) to geocode the addresses. It is free and instant to create a trial account which will work for this script.


### Required packages

You will either need the following packages or you can use Docker instead (see below).

- [python 3](https://www.python.org)
- [diskcache](http://www.grantjenks.com/docs/diskcache/)
- [geopy](https://geopy.readthedocs.io/en/stable/)
- [pandas](https://pandas.pydata.org)
- [requests](https://requests.readthedocs.io/en/master/)

## Setup environment variables

First, copy .env.example to .env and add your OPEN_CAGE_API_KEY.

You can also set the `TARGET_POSTCODE` environment variable which is overriden by the command line argument.

```bash
cp .env.example .env
```

## Usage

First, install the required packages:

```bash
pip install -r requirements.txt
```

Then run the script with the target postcode as an argument (overrides the `TARGET_POSTCODE` environment variable if set):

```bash
source .env
python ife_contact_list.py <postcode>
```

The script will download the Excel file from the IFE website, geocode the addresses, calculate the distances, and output the sorted data to a JSON file and an Excel file.

## Usage (with Docker)

Build the Docker image:

```bash
docker build -t ife_contact_list .
```

Then you can either run the Docker container with the target postcode as an argument (overrides the `TARGET_POSTCODE` environment variable if set):

```bash
docker run --env-file .env -v $(pwd)/data:/data ife_contact_list <postcode>
```

or you can set `TARGET_POSTCODE` in the .env file to run the Docker container without arguments:

```bash
docker run --env-file .env -v $(pwd)/data:/data ife_contact_list
```

## License

UNLICENSE (Public Domain) - see [LICENSE](LICENSE) for more information.
