#!/usr/bin/python3
import trakt
import trakt.tv
import trakt.movies
import os.path
import argparse
import re
from string import capwords
import textwrap
import pprint

# Login to trakt.tv
trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH
if not os.path.isfile(os.path.expanduser('~/.pytrakt.json')):
    username=input("Trakt.py Username: ")
    trakt.init(
        "$username",
        client_id="CLIENT_ID",
        client_secret="CLIENT_SECRET",
        store=True)
    print('Initialization done.')
    exit()

# Load or setup corrections dictionary 
correctionsfile=os.path.expanduser('~/.pytrakt-corrections.txt')
if os.path.isfile(correctionsfile):
    with open(correctionsfile,'r') as f:
        corrections=eval(f.read())
else:
    corrections={"title1": "corrected title1", "title2": "corrected title2"}
    with open(correctionsfile,'w') as f:
        f.write(pprint.pformat(corrections, indent=4, sort_dicts=False))

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Mark a TV Show or Movie as watched on Trakt.tv.')
parser.add_argument('--title','-t')
parser.add_argument('--year','-y', type=int)
parser.add_argument('--season','-s', type=int)
parser.add_argument('--episode','-e', type=int)
parser.add_argument(
    '--info', '-i', action='store_true',
    help="Just show trakt.tv info for file (don't mark anything). "
    "Will provide a summary with TRAKT.TV and IMDB.COM urls if available.")
parser.add_argument(
    '--correction', '-c', action='store_true',
    help="Add a correction for given FILENAME or TITLE. ")
parser.add_argument(
    'filename', nargs='?',
    help='If given, format should be '
    '"TITLE sSEASONeEPISODE.mp4" for TV, or '
    '"TITLE YEAR.mp4" for Movie. '
    'Eg. "lost s01e01.mp4" or "the lost boys 1987.mp4"',
    default=None)
opts=parser.parse_args()

if opts.filename:
    fname=os.path.basename(opts.filename)
    fname=os.path.splitext(fname)[0]
    trtable=fname.maketrans("_.-", "   ", ")(")
    fname=fname.translate(trtable)
    p=re.compile(r'(.+) s(\d+)e(\d+)', re.I)
    m=p.match(fname)
    if m:
        opts.title=m.group(1)
        opts.season=m.group(2)
        opts.episode=m.group(3)
    else:
        p=re.compile(r'(.+) (\d\d\d\d)', re.I)
        m=p.match(fname)
        if m:
            opts.title=m.group(1)
            opts.year=m.group(2)
        else:
            parser.print_help()
            exit()

origtitle=''
if opts.title:
    opts.title=opts.title.lower()
    if opts.title in corrections:
        origtitle=opts.title
        print('Found correction: '+opts.title+
              ' > '+corrections[opts.title])
        opts.title=corrections[opts.title]
    opts.title=capwords(opts.title)
else:
    parser.print_help()
    exit()

# Display the options passed nicely
print()
for k,v in vars(opts).items():
    if v and (k != "filename") and (k != "correction"):
        print('{:>9}: {}'.format(k.capitalize(),v))
print()

def add_correction(title):
    if origtitle:
        print('Exisiting correction: '+origtitle+' > '+title)
        title=origtitle
    else:
        title=title.lower()
    print('Current title: '+title)
    ctitle=input('Corrected tile (Empty to cancel): ')
    if ctitle != "":
        corrections[title]=ctitle
        with open(correctionsfile, 'w') as f:
            f.write(pprint.pformat(corrections, indent=4, sort_dicts=False))
            print('Saved: '+opts.title+' > '+ctitle)
            print('To '+ correctionsfile)
    else:
        print('Canceled.')
    input('\nDone.  Press enter')
    exit()

if opts.title and opts.correction:
    add_correction(opts.title)

if opts.episode and opts.season and opts.title:
    istv=True
    showtype="TV Show"
    showstr=' {title} s{season}e{episode}'
    if opts.year:
        opts.title=opts.title+'-'+str(opts.year)
elif opts.year and opts.title:
    istv=False
    showtype="Movie"
    showstr='  {title} {year}'
else:
    parser.print_help()
    exit()

showvars=vars(opts)    
print('Contacting Trakt.tv...\n')
try:
    if istv:
        show=trakt.tv.TVEpisode(opts.title, opts.season, opts.episode)
        print('Found: {} s{:02d}e{:02d} ({})'.format(show.show, show.season,
                                                     show.episode,
                                                     show.first_aired))
    else:
        show=trakt.movies.Movie(opts.title, opts.year)
        print('Found: {} ({})'.format(show.title, show.year))
    if opts.info:
        print('\n'+textwrap.fill(show.overview, 70)+'\n')
        print('IMDB: http://imdb.com/title/{}'.format(show.imdb))
        print('TRAKT: http://trakt.tv/{}'.format(show.ext))
        input('\nDone.  Press enter')
        exit()
    ans=input('Mark as seen (y/N)? ')
    if ans == "y": 
        show.mark_as_seen()
        print(showtype, 'marked as seen:')
        print(opts.filename)
        ans=input('\nDelete file (y/N)? ')
        if ans == 'y':
            os.remove(opts.filename)
            print('Deleted '+opts.filename)
    else:
        print("Ignored, show not marked.")
        ans=input('\nAdd a correction (y/N)? ')
        if ans == "y":
            add_correction(opts.title)
        else:
            print('Canceled.')
except trakt.errors.NotFoundException:
    if istv:
        search=trakt.tv.TVShow.search(opts.title)
    else:
        search=trakt.movies.Movie.search(opts.title)
    print('Error,', showtype, 'not found on trakt.tv:')
    print(showstr.format_map(showvars))
    print('Check http://trakt.tv for exact show title used.')
    if search:
        print('\nHere are some quick search results to try:\n')
        for show in search:
            # pretty list of available show variables
            # print(pprint.pformat(vars(show), indent=4, sort_dicts=False))
            if '_slug' in vars(show):
                print('  {title} {year}, \tSLUG: {_slug}'.format_map(vars(show)))
            elif 'slug' in vars(show):
                print('  {title} {year}, \tSLUG: {slug}'.format_map(vars(show)))
            else:
                print('  {title} {year}'.format_map(vars(show)))
    ans=input('\nAdd a correction (y/N)? ')
    if ans == "y":
        add_correction(opts.title)
    else:
        print('Canceled.')
except trakt.errors.OAuthException:
    ans=input('Error Authorizing, remove saved credentials (y/N)? ')
    if ans == "y":
        os.remove(os.path.expanduser('~/.pytrakt.json'))
        print('Credentials removed, run again to reinitialize.')
    else:
        print('Canceled.')
except Exception as e:
    print('Error contacting trakt:\n', repr(e))

input('\nDone.  Press enter')


