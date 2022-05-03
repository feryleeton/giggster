from slack import WebClient
import os


# Create the CoinBot Class
class Bot:
    # Create a constant that contains the default text for the message
    REPORT_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Test report\n\n"
            ),
        },
    }

    # The constructor for the class. It takes the channel name as the a
    # parameter and then sets it as an instance variable
    def __init__(self):
        # self.channel = channel
        self.slack_web_client = WebClient("xoxb-2964443867201-2959738034498-V0xqi07GRzj12PrN6RmuY6l2")
        # self.bot = Bot("#giggsterbot")

    def send_report(self, filename: str, diff):

        if diff:
            response = self.slack_web_client.files_upload(

                channels="#giggsterbot",

                file="/home/automatic_scraping_engine/reports/" + str(filename) + ".csv",

                title="Differential report for " + str(filename) + ' web site',

                filetype="CSV"
            )
        else:
            response = self.slack_web_client.files_upload(

                channels="#for_testing",

                file="/home/automatic_scraping_engine/reports/" + str(filename) + ".csv",

                title="Report for " + str(filename) + ' web site',

                filetype="CSV"
            )

    def send_message(self, _text):
        self.slack_web_client.chat_postMessage(text=_text, channel="#for_testing")

    def get_report(self):
        text = 'This is the test message from bot'

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}},

    # Craft and return the entire message payload as a dictionary.
    def get_message_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self.REPORT_BLOCK,
                *self.get_report(),
            ],
        }
