"""
COMMENTS:
- covered / remixed didn't bring back any occurances for ~ 50 songs searched
  across a variety of generes.
  - if you find a song with > 5 remixes | covers, then raise an issue on github
    with the detail and it will be implemented
"""

was_covered_in = 'Was covered in'
was_remixed_in = 'Was remixed in'
was_sampled_in = 'Was sampled in'
contains_sample_of = 'Contains samples of'
all_directions = [contains_sample_of, was_sampled_in, was_remixed_in, was_covered_in]

def get_paged_content_by_direction(direction):
    if direction == was_covered_in:
        raise NotImplementedError('NO occurances of this endpoint have been found in testing. Refer to comment in direction.py for more detail')
    if direction == was_remixed_in:
        raise NotImplementedError('NO occurances of this endpoint have been found in testing. Refer to comment in direction.py for more detail')
    if direction == was_sampled_in:
        return 'sampled'
    if direction == contains_sample_of:
        return 'samples'

def get_originator_from_direction(direction, breakdown_ids):
    """ normalise 'dest' / 'source' relationship as 'originator' / 'sample',
        where the originator is the subject of the initial request
        - this assumes the return from whosampled.get_videos_from_breakdown
          is [DEST, SOURCE]
    """
    if direction == contains_sample_of:
        return breakdown_ids[0], breakdown_ids[1] # originator is dest

    if direction == was_sampled_in or \
       direction == was_remixed_in or \
       direction == was_covered_in:
        return breakdown_ids[1], breakdown_ids[0] # originator is source

    raise Exception(f'Invalid direction: {direction}')
