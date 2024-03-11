from naoqi import ALProxy, ALBroker
from nao_ip import NAO_IP
from SoundReceiverModule import SoundReceiverModule
from NaoAssistant import NaoAssistant
import logging

if __name__ == "__main__":

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       NAO_IP,      # parent broker IP
       9559)        # parent broker port

    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = SoundReceiverModule(
        "SoundReceiver",
        NAO_IP,
        one_sentence=True,
        sentence_timeout=1.5,
        live_wav_each=10,
        wav_dir="py_com\\py27_audio.wav",
        save_csv=False,
    )

    nao = NaoAssistant(SoundReceiver)
    nao.start()

    nao.__del__()

    myBroker.shutdown()