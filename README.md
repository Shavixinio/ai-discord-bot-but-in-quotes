# ai-discord-bot-but-in-quotes
Originally called ***shame 2.0 but stupider*** as a reference to [emilia's old AI bot](https://github.com/CurrentlyEmilia) named shame.

Credit to [nothavoc](https://github.com/NotHavocc) for the original idea.

Basically what this does is it take messages from the specified channels and then does some fancy sorting with markov chains and nltk.
# how do i use this amazing bot??
Firstly, you need 3 / 2 things from pip depending on your Python version.

If on Python 13 or above:
```
pip install audioop-lts discord nltk python-dotenv
```

If on Python 12 or below:
```
pip install discord nltk python-dotenv
```

Then go into `app.py` and add your

- Channel IDs for the following:
  - Channels to collect messages from
  - Channel to send the formed sentences to
- Your token for thy awesome bot!!!!

Then just launch `app.py` and it'll do it for you.
