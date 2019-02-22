import requests
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from script import Script
import json

VERIFY_TOKEN = None
ACCESS_TOKEN = None



class ManuView(generic.View):

    script = Script()
    last_messages_sent_categories = {}
    asked_categories = {}
    asked_neighborhood = {}

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    print("{sender[id]} says {message[text]}".format(**message))
                    fbid = message['sender']['id']
                    self.post_facebook_message(fbid, message['message']['text'])
                elif 'postback' in message:
                    fbid = message['sender']['id']
                    self.post_facebook_message(fbid, 'start')

        return HttpResponse()

    def post_facebook_message(self, fbid, recevied_message):
        print(fbid)
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ACCESS_TOKEN # noqa E501
        response_msg = self.script.generate_json_to_send(fbid, recevied_message)
        for msg in response_msg:
            print(msg)
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=msg) # noqa E501