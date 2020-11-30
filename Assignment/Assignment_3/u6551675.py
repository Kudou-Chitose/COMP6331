from __future__ import division
import numpy as np
import random
import paho.mqtt.client as mqtt
import time

flag = 0
msg_list = []
timestamp_list = []

def on_connect(client, userdata, flags, rc):
	print("Connected with result code: " + str(rc))

def on_message(client, userdata, msg):
	msg_list.append(str(msg.payload))
	timestamp_list.append(str(msg.timestamp))
	print(msg.topic + " " + str(msg.payload))

# The average rate of messages you receive across the period [messages/second]
def message_rate(msgList, sec):
	recv = len(msgList) / sec
	return recv

# The rate of message loss you see [percentage]
def message_loss(msgList):
	int_msg_list = []
	for element in msgList:
		if element != "close":
			int_msg_list.append(int(element))
	if int_msg_list[-1] == max(int_msg_list):
		loss = 1 - len(msgList) / (int_msg_list[-1] - int_msg_list[0] + 2)
	else:
		loss = 1 - len(msgList) / (max(int_msg_list) - int_msg_list[0] + int_msg_list[-1] + 3)
	return loss

# The rate of duplicated messages you see over any 10 seconds [percentage]
def dup_message_rate(msgList):
	test_list = []
	randIndex = int(random.uniform(0,len(msgList) - 10))
	for i in range(randIndex, randIndex + 9):
		test_list.append(msgList[i])
	non_dup_msg_list = list(set(test_list))
	dupe = 1 - len(non_dup_msg_list) / len(test_list)
	return dupe

# The rate of out-of-order messages you see [percentage]
def out_of_order_message_rate(msgList):
	ooo_msg = 0
	int_msg_list = []
	for element in msgList:
		if element != "close":
			int_msg_list.append(int(element))
	for i in range(1, len(int_msg_list)):
		if int_msg_list[i] < int_msg_list[i-1]:
			if int_msg_list[i-1] != max(int_msg_list):
				ooo_msg = ooo_msg + 1
	ooo = ooo_msg / len(int_msg_list)
	return ooo

def inter_message_gap(msgList, timestampList):
	flag = 0
	gap_list = []
	int_msg_list = []

	for element in msgList:
		if element == "close":
			flag = 1
		else:
			int_msg_list.append(int(element))

	gap_list.append(float(timestampList[1]) - float(timestampList[0]))

	for i in range(1, len(int_msg_list)):
		if flag == 1:
			if int_msg_list[i] - int_msg_list[i - 1] == 1:
				gap_list.append(float(timestampList[i + 1]) - float(timestampList[i]))
			elif msgList[i - 1] == max(int_msg_list):
				gap_list.append(float(timestampList[i + 1]) - float(timestampList[i]))
		else:
			if int_msg_list[i] - int_msg_list[i - 1] == 1:
				gap_list.append(float(timestampList[i]) - float(timestampList[i - 1]))
			elif msgList[i - 1] == max(int_msg_list):
				gap_list.append(float(timestampList[i]) - float(timestampList[i - 1]))

		gap = np.mean(gap_list) * 1000

	return gap
 
def inter_message_gap_variation(msgList, timestampList):
	flag = 0
	gap_list = []
	int_msg_list = []

	for element in msgList:
		if element == "close":
			flag = 1
		else:
			int_msg_list.append(int(element))

	gap_list.append(float(timestampList[1]) - float(timestampList[0]))

	for i in range(1, len(int_msg_list)):
		if flag == 1:
			if int_msg_list[i] - int_msg_list[i - 1] == 1:
				gap_list.append(float(timestampList[i + 1]) - float(timestampList[i]))
			elif msgList[i - 1] == max(int_msg_list):
				gap_list.append(float(timestampList[i + 1]) - float(timestampList[i]))
		else:
			if int_msg_list[i] - int_msg_list[i - 1] == 1:
				gap_list.append(float(timestampList[i]) - float(timestampList[i - 1]))
			elif msgList[i - 1] == max(int_msg_list):
				gap_list.append(float(timestampList[i]) - float(timestampList[i - 1]))

		gvar = np.std(gap_list) * 1000
	return gvar

def report(msgList, timestampList, timer):
	recv = message_rate(msgList, timer)
	loss = message_loss(msgList)
	dupe = dup_message_rate(msgList)
	ooo = out_of_order_message_rate(msgList)
	gap = inter_message_gap(msgList, timestampList)
	gvar = inter_message_gap_variation(msgList, timestampList)

	print("The average rate of messages you receive across the period [messages/second] is: " + str(recv))
	print("The rate of message loss you see [percentage] is: " + str(loss))
	print("The rate of duplicated messages you see over any 10 seconds [percentage] is: " + str(dupe))
	print("The rate of out-of-order messages you see [percentage] is: " + str(ooo))
	print("The mean inter-message-gap [milliseconds] is: " + str(gap))
	print("The inter-message-gap variation [milliseconds] is: " + str(gvar))


timer = 300
# set client_id
client_sub = mqtt.Client(client_id="3310-<u6551675>")

# authentication
client_sub.username_pw_set(username="students", password="33106331")

client_sub.on_connect = on_connect
client_sub.on_message = on_message

client_sub.connect('comp3310.ddns.net', 1883, 300)

'''
Subscribe to the three 6 channel counters (QoS 0,1,2)
Need to manually switch to different channel counters
'''
client_sub.subscribe("counter/slow/q0", qos=0)
# client_sub.subscribe("counter/slow/q1", qos=1)
# client_sub.subscribe("counter/slow/q2", qos=2)
# client_sub.subscribe("counter/fast/q0", qos=0)
# client_sub.subscribe("counter/fast/q1", qos=1)
# client_sub.subscribe("counter/fast/q2", qos=2)
# client_sub.subscribe("$SYS/broker/load/messages/received/5min")
# client_sub.subscribe("$SYS/broker/load/messages/sent/5min")
# client_sub.subscribe("$SYS/broker/load/publish/recieved/5min")
# client_sub.subscribe("$SYS/broker/load/publish/sent/5min")
# client_sub.subscribe("$SYS/broker/heap/current size")
# client_sub.subscribe("$SYS/broker/heap/maxium size")
# client_sub.subscribe("$SYS/broker/clients/connected")

client_sub.loop_start()
time.sleep(timer)
client_sub.loop_stop()
client_sub.disconnect()
report(msg_list, timestamp_list, timer)

#Q4

# set client_id
client_pub = mqtt.Client(client_id="3310-<u6551675>")

# authentication
client_pub.username_pw_set(username="students", password="33106331")
client_pub.connect('comp3310.ddns.net', 1883, 300)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/recv","0.997",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/loss","0.003",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/gap","1001",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/0/gvar","546",qos=2,retain=True)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/recv","0.997",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/loss","0.003",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/gap","1003",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/1/gvar","318",qos=2,retain=True)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/recv","0.997",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/loss","0.003",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/gap","1004",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/slow/2/gvar","428",qos=2,retain=True)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/recv","92.483",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/loss","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/gap","11",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/0/gvar","92",qos=2,retain=True)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/recv","31.567",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/loss","0.657",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/gap","11",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/1/gvar","58",qos=2,retain=True)

client_pub.publish("studentreport/u6551675/language","python",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/network","wifi",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/recv","16.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/loss","0.824",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/dupe","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/ooo","0.0",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/gap","18",qos=2,retain=True)
client_pub.publish("studentreport/u6551675/fast/2/gvar","74",qos=2,retain=True)
client_pub.loop_forever()