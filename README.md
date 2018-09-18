# INGRESS ALIGNMENTS TOOL

## Preface

This python script will help you find good alignments you maybe haven't think of will looking at the ingress intel map.

## Requirements

You need:
- python >=3.7
- scipy
- geopy
- Your GDPR "game_log.tsv" file in the same directory

## How to use it ?

Open the python script file, and set your settings accordinly to your preferences at the top of the script. Don't modify after the first function if you don't know what you're doing.

| settings | meaning | Good values |
| --- | --- | --- |
| angle_max | The angle max in degrees between the 3 points (see how it works) | > 0.1 (perfect alignments) to 15 |
| points_aligned | Minimum number of aligned points to be added to the output. | > 5 to 25 |
| lookup_nearest | Number of portals around the one selected to look for alignments | > 25 to 200 (higher will be more precise, but computing intensive |
| max_dist | Set restriction on the maximum distance between a portal and the alignment origin | **True** or False |
| max_dist_val | if *max_dist* set on **True**, the maximum distance in km | 0.5 to 10 |
| limit | Do we limit the range of searching ? | **True** or False |
| limit_range | The number of km to look for alignements starting from *limit_origin | 10 to 50 |
| limit_origin | The origin coordinates | valid coordinates |

When you're done, run the script and wait for the results to come. It can take a long time . When it's done computing, go to [hamstermap](http://www.hamstermap.com/quickmap.php) to get a preview of the alignments found.
## How does it works ?

The script will parse your game_log.tsv to find every portals location. It will then iterate on all the portals, setting each portal successively as the *origin*. It will then find the *lookup_nearest* number of nearest portals to the origin, and iterate over them. Each of them will successively be marked as the reference point, and the game can begin. The script will iterate a second time over those portals. If the angle between the origin, the reference and the considered portal is low enough, it is added to a temporary list of aligned portals. For the next portal, the angle between the origin, the reference and the considered is checked, but also the angle between the last, the one before the last and the considered as well, to avoid circles or curves  and steps. If the temporary list is long enough, it is added to the output list.

## Known bugs
- Portals may not be perfectly aligned and can form two lines of aligned portals
- There is sometimes a "satellite" small cluster far from the alignment found in low density areas

## TODO
- Automaticly sending the coos.geo created from the game_log.tsv containing only coordinates to a server to create a portal database
- Remove config in the script and add command line options
- Improve alignment finding algorithm
- Test if the threading model is appropriate
- Export to a format readable by the ingress map
- Find a way to remove removed portals from the list
- Improve the coos.geo merging
