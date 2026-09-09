import os

from .. import log
from ..graphics.font import Font
from ..graphics.shader import Shader
from ..graphics.texture import Texture2D


class ResourceManager:
    def __init__(self, audio_system=None, root_dir="."):
        self.root_dir = root_dir
        self.audio_system = audio_system
        self._textures = {}
        self._shaders = {}
        self._fonts = {}
        self._sounds = {}
        self._music = {}

    def _resolve(self, path):
        if os.path.isabs(path):
            return path
        return os.path.join(self.root_dir, path)

    def load_texture(self, path, nearest=False, key=None):
        cache_key = key or path
        if cache_key in self._textures:
            return self._textures[cache_key]
        texture = Texture2D.from_path(self._resolve(path), nearest=nearest)
        self._textures[cache_key] = texture
        log.debug(f"Loaded texture {path}")
        return texture

    def load_shader(self, name, vertex_path, fragment_path):
        if name in self._shaders:
            return self._shaders[name]
        shader = Shader.from_files(self._resolve(vertex_path), self._resolve(fragment_path))
        self._shaders[name] = shader
        log.debug(f"Loaded shader {name}")
        return shader

    def load_font(self, path=None, size=18, key=None):
        cache_key = key or (path, size)
        if cache_key in self._fonts:
            return self._fonts[cache_key]
        resolved = self._resolve(path) if path else None
        font = Font.from_file(resolved, size=size)
        self._fonts[cache_key] = font
        log.debug(f"Loaded font {path or 'default'} @ {size}px")
        return font

    def load_sound(self, path, key=None):
        if self.audio_system is None:
            raise RuntimeError("ResourceManager has no AudioSystem attached")
        cache_key = key or path
        if cache_key in self._sounds:
            return self._sounds[cache_key]
        sound = self.audio_system.load_sound(self._resolve(path))
        self._sounds[cache_key] = sound
        return sound

    def load_music(self, path, key=None):
        if self.audio_system is None:
            raise RuntimeError("ResourceManager has no AudioSystem attached")
        cache_key = key or path
        if cache_key in self._music:
            return self._music[cache_key]
        music = self.audio_system.load_music(self._resolve(path))
        self._music[cache_key] = music
        return music

    def unload_all(self):
        for texture in self._textures.values():
            texture.delete()
        for shader in self._shaders.values():
            shader.delete()
        for font in self._fonts.values():
            font.delete()
        for sound in self._sounds.values():
            if sound:
                sound.delete()
        for music in self._music.values():
            if music:
                music.delete()
        self._textures.clear()
        self._shaders.clear()
        self._fonts.clear()
        self._sounds.clear()
        self._music.clear()
