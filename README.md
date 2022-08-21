# DnD Inventory Tracker

## Setting Up Your Dev Environment
Create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Ensure you see the name of the virutal environment ("venv" in this example) preceding your shell prompt. Then install Python packages:

```
pip3 install -r requirements.txt
```

You can deactivate the Python virtual environment when you're finsihed working by running:

```
deactivate
```

I believe VSCode will autodetect the virtual environment for you, so no need to worry about the activating and deactivating steps
if you use the built-in terminal for VSCode. Make sure you do the package installation step, however.

## Connecting to the Server
```
ssh -L 5432:localhost:5432 -p 2222 <your username>@cs.silverknoll.net
```

You should now be able to connect to the database at `localhost` through the web server, pgAdmin, or `psql`.

Make sure this SSH connection is open or you will not be able to connect to the database.