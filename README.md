# Game Recommender Search Engine


## Quickstart Guide
### 1. Cloning the repository from Git
```bash
git clone https://github.com/studioghibli/cs4300sp2021-cj369-ec636-lfh32-ll692-mac568.git
```
### 2. Setting up your virtual environment

To learn more about virtualenv, go [here](https://virtualenv.pypa.io/en/stable/installation/) to install and for dead-simple usage go [here](https://virtualenv.pypa.io/en/stable/installation/)

```bash
# Create a new python3 virtualenv named venv.
virtualenv -p python3 venv

# Activate the environment
source venv/bin/activate # (or the equivalent in Windows)

# Install all requirements
pip install -r requirements.txt
```
(For Mac users, you may encounter an `ERROR: Failed building wheel for greenlet`. This can be fixed with `xcode-select --install`.)

An aside note: In the above example, we created a virtualenv for a python3 environment. You will have Python 3.7.6 installed by default.


### 3. Ensuring environment variables are present

We will be using environment variables to manage configurations for our application.
This is a good practice to hide settings you want to keep out of your public code like passwords or machine-specific configurations.
We will maintain all of our environment variables in a file, and we will populate our environment with these settings before running the app.
We have provided you with starter environment files but remember to add them to your `.gitignore` if you add sensitive information to them.

#### Unix - MacOSx, Linux, Git Bash on Windows
- Your environment variables are stored in a file called `.env`
- To set your environment:
``` bash
source .env
```

### 4. Check to see if app runs fine by running in localhost:
``` bash
python3 app.py
```

If you encounter a `KeyError: 'APP_SETTINGS'`, try running `source .env` (Mac) or `call env.bat` (Windows) again.
At this point the app should be running on [http://localhost:5000/](http://localhost:5000/). Navigate to that URL in your browser.
