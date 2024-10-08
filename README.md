# NAVER 1784 Kitchen SLACK BOT

Using NAVER BAND API, get menu posts from NAVER BAND and send them to the Slack channel.

## Environment setup
```
pip install requirements.txt

# or
pip install slack_sdk python-dotenv
```

You should set your personal tokens in the `.env` file like below:
```
SLACK_TOKEN={your_slack_app_token}
BAND_ACCESS_TOKEN={your_band_access_token}
```
![slack_app_token](figures/Slack_app_token.png)
![band_access_token](figures/BAND_access_token.png)

## Run
```
python bot.py
```