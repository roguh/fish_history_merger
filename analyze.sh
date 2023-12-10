#!/bin/sh
# the fish_history file always stores the cmd: on a single line
# therefore, we can safely regex for cmd: .*$ and replace it if it has any unusual characters
set -x
ag -A1 'cmd: .' --only-matching ./fish_history | ag 'when: .|cmd: .' --only-matching | sort | uniq -c | sort -k2
