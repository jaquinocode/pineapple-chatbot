from Chatbot.simple_chatbot import SimpleChatBot
import time
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from io import BytesIO
import simplejson
import boto3
import pprint
import sys

bot = SimpleChatBot("Chad", user="root", password="root", database="tester3")

model_client = boto3.client("lex-models")
runtime_client = boto3.client("lex-runtime")

class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        self.respond()

    def do_POST(self):
        """ self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()

        data = simplejson.loads(self.data_string)
        with open("chatbotconversation.json", "w") as outfile:
            simplejson.dump(data, outfile) """

        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()

        input_dictionary = simplejson.loads(self.data_string)

        #str(bot.get_response(input_dictionary["input"]))
        lex_response = runtime_client.post_text(
                            botName='PineappleBotTwo',
                            botAlias='Prod',
                            userId='01',
                            inputText=str(input_dictionary["input"])
                        )

        #pprint.pprint(lex_response)

        dialogState = str(lex_response.get('dialogState', 'Could not get dialogState from lex response json'))

        if dialogState == 'ReadyForFulfillment':
            intent = str(lex_response.get('intentName','Could not get intent.'))
            entity = str(lex_response.get('slots','Could not get slot.').get('Name','Could not get slot data.'))
            
            print('\n\n\n--\nYour intent is to: ' + intent)
            print('Your entity is: ' + entity + '\n--\n')

            bot_response = str(bot.get_response(input_dictionary["input"], intent, entity))
            print(bot_response)

        else:   
            bot_response = str(bot.get_link(input_dictionary["input"]))
            
        self.wfile.write(bytes(bot_response, "utf8"))
        
        return bytes(bot_response, "utf8")

    def handle_http(self, status, content_type):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        return bytes("Hello world", "UTF-8")

    def respond(self):
        content = self.handle_http(200, 'text/html')
        self.wfile.write(content)


HOST_NAME = 'localhost'
PORT_NUMBER = 3000

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))
