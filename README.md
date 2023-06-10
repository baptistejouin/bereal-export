# BeReal export tool, for memories

This tool has been designed to export your bereal memories outside the app (from a json source file) in photo format (10cm x 15cm). Each photo contains 2 Bereals, which can then be cut out after printing.

## How to use

### 1. Install dependencies

- Python 3.6+ / Pip
- [Pillow library](https://pillow.readthedocs.io/en/latest/installation.html) 
- Requests library
- Certifi library

### 2. Get a bearer token

Not implemented yet, but you can get one by sniffing the app's traffic. (you check [mitmproxy](https://mitmproxy.org/)).

Or you can use this nice python project, [BeFake](https://github.com/notmarek/BeFake/).

### 3. Get your memories JSON file

Not implemented yet, but you can hit the API endpoint `https://mobile.bereal.com/api/feeds/memories` with your bearer token and `AlexisBarreyat.BeReal/0.23.2 iPhone/16.0 hw/iPhone13_2` as user-agent.

### 4. Run the script

```bash
# Clone the repo
git clone git@github.com:baptistejouin/bereal-export-py.git

# Run the script
python bereal-export-py/app.py --json <path to your json file> --output <path to your output folder>
```
