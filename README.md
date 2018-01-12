# Collection comparing and diff for BGG

This script uses the boardgamegeek API that an be installed using 'pip
install boardgamegeek'. It is intended to create a large list of multiple
user's collections, find games that aren't on a user's list, and to filter
base vs expansion, etc.

Usage instructions can be found by running "bgg_comp.py -h"

Note that the "diff" action can take a significant amount of time as we
don't want bad requests from BGG. This means that we need to be careful
either throttle the requests to a slow rate, or instead do error management
on the requests.
