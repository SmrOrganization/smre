import sdl2
import sdl2.sdlmixer as mixer

from .. import log


class Sound:
    def __init__(self, chunk_ptr):
        self.chunk_ptr = chunk_ptr

    def play(self, loops=0, volume=1.0):
        mixer.Mix_VolumeChunk(self.chunk_ptr, int(max(0.0, min(1.0, volume)) * 128))
        return mixer.Mix_PlayChannel(-1, self.chunk_ptr, loops)

    def delete(self):
        if self.chunk_ptr:
            mixer.Mix_FreeChunk(self.chunk_ptr)
            self.chunk_ptr = None


class Music:
    def __init__(self, music_ptr):
        self.music_ptr = music_ptr

    def play(self, loops=-1, volume=1.0):
        mixer.Mix_VolumeMusic(int(max(0.0, min(1.0, volume)) * 128))
        mixer.Mix_PlayMusic(self.music_ptr, loops)

    def pause(self):
        mixer.Mix_PauseMusic()

    def resume(self):
        mixer.Mix_ResumeMusic()

    def stop(self):
        mixer.Mix_HaltMusic()

    def set_volume(self, volume):
        mixer.Mix_VolumeMusic(int(max(0.0, min(1.0, volume)) * 128))

    def delete(self):
        if self.music_ptr:
            mixer.Mix_FreeMusic(self.music_ptr)
            self.music_ptr = None


class AudioSystem:
    def __init__(self, frequency=44100, channels=2, chunk_size=2048):
        self.available = False
        if sdl2.SDL_WasInit(sdl2.SDL_INIT_AUDIO) == 0:
            sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO)
        result = mixer.Mix_OpenAudio(frequency, mixer.MIX_DEFAULT_FORMAT, channels, chunk_size)
        if result != 0:
            log.warning(f"Audio device unavailable, running without sound: {sdl2.SDL_GetError()}")
            return
        self.available = True

    def load_sound(self, path):
        if not self.available:
            return None
        chunk_ptr = mixer.Mix_LoadWAV(path.encode("utf-8"))
        if not chunk_ptr:
            log.error(f"Failed to load sound {path}: {sdl2.SDL_GetError()}")
            return None
        return Sound(chunk_ptr)

    def load_music(self, path):
        if not self.available:
            return None
        music_ptr = mixer.Mix_LoadMUS(path.encode("utf-8"))
        if not music_ptr:
            log.error(f"Failed to load music {path}: {sdl2.SDL_GetError()}")
            return None
        return Music(music_ptr)

    def set_master_volume(self, volume):
        if self.available:
            mixer.Mix_Volume(-1, int(max(0.0, min(1.0, volume)) * 128))

    def stop_all(self):
        if self.available:
            mixer.Mix_HaltChannel(-1)

    def shutdown(self):
        if self.available:
            mixer.Mix_CloseAudio()
            self.available = False
