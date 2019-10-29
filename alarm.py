import os
import json
from google.cloud import pubsub_v1

from gpiozero import DistanceSensor, LED
from time import sleep

#Insert your project id below
project_id = "YOUR-PROJECT-ID"

system_online = True #on by default
house_boundary = 15 # how close can you get before alarm is tripped, in cm
#challenge, how to set house_boundary via pubsub

#declaring gpio pin connections
sensor = DistanceSensor(echo = 19, trigger = 26)
alarm_triggered_led = LED(13) #red LED
system_status_led = LED(6) #blue LED

# initialize device state
# at the beginning, alarm is not triggered, system is online
system_status_led.on()
alarm_triggered_led.off()

# 1. create a Pub/Sub publisher client and declare alarm topic to post message on when alarm is tripped
publisher = pubsub_v1.PublisherClient()
alarm_topic_id = "alarm"
telemetry_topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=alarm_topic_id,
)

# 2. trigger_alarm is called when alarm is triggered
# should not be triggered successively
def trigger_alarm():
    publisher.publish(telemetry_topic_name, b'{"alarm", "on"}')

# 3. reset is called to turn off alarm
def reset():
    publisher.publish(telemetry_topic_name, b'{"alarm", "off"}')
    alarm_triggered_led.off()

# 4. Create a Pub/Sub subscriber client. Subscribes to config topic to receive configuration changes
# Supports two config/commands:
#    system_online : bool - turns on/off system
#    reset : bool - if True, resets the alarm
config_topic_id = "config"
config_subscriber_id = "configSub"

subscriber = pubsub_v1.SubscriberClient()
config_topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=project_id,
    topic=config_topic_id,
)
config_subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=project_id,
    sub=config_subscriber_id, 
)

# 5. Called when received new configuration from configSub
def process_new_config(message):
    new_config = json.loads(message.data)
    global system_online
    system_online = new_config ["system_online"]
    if system_online:
        system_status_led.on()
    else :
        system_status_led.off()
        alarm_triggered_led.off()
    if new_config["reset"]:
        reset()
    message.ack()

# 6. Subscribes to config
subscriber.subscribe(config_subscription_name, process_new_config)

# 7. Takes information for DistanceSensor and decides whether
while True:
    distance = sensor.distance * 100
    print('Distance: ', distance)
    if system_online and distance < house_boundary:
        if not alarm_triggered_led.is_lit:
            alarm_triggered_led.on()
            trigger_alarm()

    sleep(1)

#todo insert qos
