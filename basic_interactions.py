from naoqi import ALProxy
NAO_IP = "192.168.0.105"

print("NAO_IP: ", NAO_IP)

autonomousLife = ALProxy("ALAutonomousLife", NAO_IP, 9559)
autonomousLife.setState("disabled")
# solitary, interactive, safeguard, disabled

posture = ALProxy("ALRobotPosture", NAO_IP, 9559)
posture.goToPosture("Sit", 0.5)

basic_awareness = ALProxy("ALBasicAwareness", NAO_IP, 9559)
basic_awareness.setEnabled(True)
basic_awareness.getTrackingMode()

audio_device = ALProxy("ALAudioDevice", NAO_IP, 9559)
audio_device.setOutputVolume(40)

tts = ALProxy("ALTextToSpeech", NAO_IP, 9559)

print(tts.getAvailableLanguages())
print(tts.getAvailableVoices())
tts.setVoice("naofrf")

tts.say("Et pourquoi pas ?")

leds = ALProxy("ALLeds", NAO_IP, 9559)
leds.reset("AllLeds")