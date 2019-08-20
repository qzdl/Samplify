"""
COMMENTS:
- covered / remixed didn't bring back any occurances for ~ 50 songs searched
  across a variety of generes.
  - if you find a song with > 5 remixes | covers, then raise an issue on github
    with the detail and it will be implemented
"""

was_covered_in = 'Was covered in '
was_remixed_in = 'Was remixed in '
was_sampled_in = 'Was sampled in '
contains_sample_of = 'Contains samples of '

def get_paged_content_by_direction(direction):
    if direction == was_covered_in:
        raise NotImplementedError('NO occurances of this endpoint have been found in testing. Refer to comment in direction.py for more detail')
    if direction == was_remixed_in:
        raise NotImplementedError('NO occurances of this endpoint have been found in testing. Refer to comment in direction.py for more detail')
    if direction == was_sampled_in:
        return 'sampled'
    if direction == was_covered_in:
        return 'samples'
