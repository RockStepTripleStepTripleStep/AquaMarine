from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

from utils.get_nearest import *
from utils.getlatlong import *
from utils.get_directions_link import *
from send_sms import *
from utils.getlocname import *
from update_status import *
from utils.exceptions import *


app = Flask(__name__)


@app.route("/sms", methods = ['GET', 'POST'])
def sms_reply():
	message = request.values.get('Body', None)
	phone_num = request.values.get('From', None)

	resp = MessagingResponse()


	# user match case
	if "match me at" in message.lower():
		location_phrase = " ".join(message.split(" ")[3:])
		print location_phrase
		try:
			loc = getlatlong(location_phrase)
			nearest,number = closest(loc)
			link = getdirectionslink([loc["lat"], loc["lng"]], [nearest["lat"], nearest["lng"]])
			resp.message("We found you a match, here is the google maps link: " + link)
			sendmsg(number,"Your help is on the way from "+getlocname([loc["lat"],loc["lng"]]))
			update_receive(0, number, None)
		except NoMatchException:
			resp.message("Thank you for your good will, but there is no one to help at the moment. Please check back later.")
		except NoPlaceException:
			resp.message("Couldn't recognize location please try with a different location.")

	# match receive case
	elif "receive at" in message.lower():
		location_phrase = " ".join(message.split(" ")[2:])
		try:
			loc = getlatlong(location_phrase)
			update_receive(1, phone_num, loc)
			resp.message("We will inform you once you get a match.")
		except:
			resp.message("Couldn't recognize location please try with a different location.")

	elif "BYE" == message: 
		update_receive(0, phone_num, None)
		resp.message("Thank you for using Serve-it!")

	else:
		resp.message("Type match me at <Location> to give help,  receive at <Location> to get help, or BYE to quit.")

	return str(resp)

if __name__== "__main__":
	app.run()

