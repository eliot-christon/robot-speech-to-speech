# robot-speech-to-speech 🤖🗣️
Pacte Novation Internship Project - 2024

## Data - stored - people 👥
The data about the people involved in the project as users.
Each user has a profile with a name, (also folder name), some information contained in the ```info.txt``` file, a voice recording of approximately 15 seconds ```voices/*.wav```, a potential picture ```faces/*.png``` and a level of duty in the ```level_of_duty.txt``` file.

```plaintext
--firstname_lastname
  |--info.txt
  |--level_of_duty.txt
  |--faces
  |  |--face.png
  |--voices
     |--voice.wav
```

### Levels of Duty

1. **Guest**
2. **Intern (Stagiaire)**
3. **Apprentice (Alternant)**
4. **Employee (Employé)**
5. **HR and Works Council (CE et RH)**
6. **Management and Administration (Direction et Admin)**