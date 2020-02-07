from samplify.tools import direction as direct
import samplify.config as config

class Options:
    def __init__(self):
       # source types
       self.PLAYLIST = 'playlist'
       self.ALBUM = 'album'
       self.ARTIST = 'artist'
       self.SONG = 'song'
       self.CURRENT_SONG = 'current_song'

       # output types
       self.CREATE_ONLY = 'w'
       self.APPEND_ONLY = 'a'
       self.APPEND_OR_CREATE = 'a+'

    def type_is_playlist(self, content_type):
        return content_type == self.PLAYLIST

    def type_is_album(self, content_type):
        return content_type == self.ALBUM

    def type_is_artist(self, content_type):
        return content_type == self.ALBUM

    def type_is_song(self, content_type):
        return content_type == self.SONG

    def type_is_current_song(self, content_type):
        return content_type == self.CURRENT_SONG

    def generate(self, reference, direction=None, content_type=None, scope=None,
                 output_name=None, output_type=None, username=None):
        """Request-wise options object
        direction:
            specify (sampled_by|samples)
        reference:
            link to identify the content. e.g. spotify:playlist:23sdf098y23kj
        reference_type:
            the type of the reference given, e.g. uri
        content_type:
            specify (album|song|current_song|playlist)
        output_name:
            name of output playlist
        output_type:
            (play|append_only|create_only|append_or_create)
            default=create_only
        """
        self.reference = reference
        self.direction = direction if direction else [direct.contains_sample_of]
        if content_type:
            self.content_type = content_type
        else:
            pass # TODO parse content_type
        self.output_name = output_name
        self.output_type = output_type if output_type else self.CREATE_ONLY
        self.scope = scope
        self.username = username if username else config.username
