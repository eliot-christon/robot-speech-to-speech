# robot-speech-to-speech 🤖🗣️
Pacte Novation Internship Project - 2024

## Data - live ⚡
Contains the data used for the live part of the project highly dynamic and often modified during the execution of the project.

This folder contains only temporary files that are erased after the execution of the project. for safety reasons, the data is not stored in the repository. 🚫

Here is a description table of the files in this folder:

| File | Description |
| --- | --- |
| [images](images/)                                     | unused for now |
| [action_selected.txt](action_selected.txt)            | the action selected by the assistant in response to the user's request |
| [audio_generated.wav](audio_generated.wav)            | the audio generated by the assistant, this is the vocal answer that will be played by the robot |
| [audio_recorded.raw](audio_recorded.raw)              | the audio recorded by the robot, bytes format |
| [audio_recorded.wav](audio_recorded.wav)              | the audio recorded by the robot, wav format converted from the raw format |
| [documents_context.csv](documents_context.csv)        | the similitude matrix of the documents in the context when the assistant needs to retrieve information from the documents |
| [documents_context.txt](documents_context.txt)        | the contexts from the relevant documents when the assistant needs to retrieve information from the documents |
| [led_rgb.txt](led_rgb.txt)                            | the color of the led of the robot, in RGB format |
| [person_recognized.txt](person_recognized.txt)        | the person recognized by the program, vocal recognition for now |
| [text_generated.txt](text_generated.txt)              | the text generated by the assistant |
| [text_prompt.txt](text_prompt.txt)                    | the entire text prompt for the LLM to generate its answer |
| [text_to_say.txt](text_to_say.txt)                    | the text to say from the generated text, this is the final text that will be said by the robot |
| [text_transcribed.txt](text_transcribed.txt)          | the text transcribed from the audio recorded by the robot |
| [time_speech_detected.txt](time_speech_detected.txt)  | the last time the program detected speech |