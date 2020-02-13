import os
from pydub import AudioSegment


sound = list()

sound.append(AudioSegment.from_mp3("./static/uploads/music_source/blues_scale/1.mp3"))
sound.append(AudioSegment.from_mp3("./static/uploads/music_source/blues_scale/2.mp3"))
sound.append(AudioSegment.from_mp3("./static/uploads/music_source/blues_scale/3.mp3"))
sound.append(AudioSegment.from_mp3("./static/uploads/music_source/blues_scale/4.mp3"))
sound.append(AudioSegment.from_mp3("./static/uploads/music_source/blues_scale/5.mp3"))

for i in range(len(sound)):
    sound[i] = sound[i][:500]*2

music=sound[0]+sound[1]+sound[2]+sound[3]+sound[4]

music.export("./music.mp3", format="mp3")
