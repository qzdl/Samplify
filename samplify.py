import argparse
from sample_finder import Samplify
from tools.options import Options

"""
CLI Frontend to Samplify
"""


if __name__ == '__main__':
    options = Options()
    parser = argparse.ArgumentParser()
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument(
        '-l',
        '--link',
        help='Click "Share" > "Copy Link"'
    )
    reference_group.add_argument(
        '-s',
        '--search',
        help='Search as you would in the app'
    )

    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument(
        '--album',
        action="store_const",
        const=options.ALBUM,
        dest='content_type'
    )
    content_group.add_argument(
        '--playlist',
        action="store_const",
        const=options.PLAYLIST,
        dest='content_type'
    )
    content_group.add_argument(
        '--song',
        action="store_const",
        const=options.SONG,
        dest='content_type'
    )
    # FIXME: current song can't work with '--search'
    content_group.add_argument(
        '--current-song',
        action="store_const",
        const=options.CURRENT_SONG,
        dest='content_type'
    )

    parser.add_argument("--direction")
    parser.add_argument("--output-name")
    parser.add_argument("--output-type")
    parser.add_argument("--username")

    debug_group = parser.add_mutually_exclusive_group(required=False)
    debug_group.add_argument(
        '-v',
        help='Include function detail',
        action="store_const",
        const=1,
        dest='verbosity'
    )
    debug_group.add_argument(
        '-vv',
        help='Multiline, include limited data',
        action="store_const",
        const=2,
        dest='verbosity'
    )
    debug_group.add_argument(
        '-vvv',
        help='Multiline, include full data',
        action="store_const",
        const=3,
        dest='verbosity'
    )
    args = parser.parse_args()

    samplify = Samplify(verbosity=args.verbosity or 0);
    result = None

    if args.search:
        result = samplify.from_search(
            search_term=args.search,
            direction=args.direction,
            content_type=args.content_type,
            output_name=args.output_name,
            output_type=args.output_type
        )
    elif options.type_is_playlist(args.content_type):
        result = samplify.playlist(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )
    elif  options.type_is_album(args.content_type):
        result = samplify.album(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type
        )
    elif options.type_is_song(args.content_type):
        result = samplify.song(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )
    elif options.type_is_current_song(args.content_type):
        result = samplify.current_song(
            reference=args.link,
            direction=args.direction,
            output_name=args.output_name,
            output_type=args.output_type,
            username=args.username
        )
