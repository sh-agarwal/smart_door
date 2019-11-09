# MQTT Publish Demo
# Publish two messages, to two different topics

import paho.mqtt.publish as publish

publish.single("door/joystick", "Hello", hostname="85.119.83.194")
publish.single("CoreElectronics/topic", "World!", hostname="85.119.83.194")
print("Done")