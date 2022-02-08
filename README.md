# trakt-mark-watched.py

Python script that will mark shows as watched on trakt.tv when given a nicely formatted filename.

Uses [pytrakt](https://github.com/moogar0880/PyTrakt) python trakt module. Install with: `pip install trakt`

The filename given should be either formatted like `tv show title s01e01.mp4` or `movie title 1999.mp4`.

If no match is found on trakt.tv you may be given a list of possible matches (maybe a year is needed to clarify a tv show).

A corrections file can be used for automatic name substitution (eg. "fool us" to "penn teller fool us").

When first run the script will need to initialize. Give your trakt.tv username (email address) and you'll be given a trakt.tv url to get your access code from. Copy that code back into the terminal. If successful the credentials will be stored for future use, but if for some reason the creditials expire just erase the $HOME/.pytrakt.json file and reinitialize.
 
```
usage: trakt-mark-watched.py [-h] [--title TITLE] [--year YEAR] [--season SEASON]
                             [--episode EPISODE] [--info] [--correction]
                             [filename]

Mark a TV Show or Movie as watched on Trakt.tv.

positional arguments:
  filename              If given, format should be "TITLE sSEASONeEPISODE.mp4" for TV, or
                        "TITLE YEAR.mp4" for Movie. Eg. "lost s01e01.mp4" or "the lost boys
                        1987.mp4"

optional arguments:
  -h, --help            show this help message and exit
  --title TITLE, -t TITLE
  --year YEAR, -y YEAR
  --season SEASON, -s SEASON
  --episode EPISODE, -e EPISODE
  --info, -i            Just show trakt.tv info for file (don't mark anything). Will
                        provide a summary with TRAKT.TV and IMDB.COM urls if available.
  --correction, -c      Add a correction for given FILENAME or TITLE.
```
