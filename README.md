RenrenCommonFriends
===================

A GUI-tools to help you to find common friends of your two or more friends

*   require [Python](http://www.python.org) (Python 3 is not supported)
    -   require [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/intro)    `apt-get install python-qt4`
    -   require [BeautifualSoup4](http://www.crummy.com/software/BeautifulSoup/) `apt-get install python-bs4` or `pip install beatuifulsoup4`
    -   require [requests](http://docs.python-requests.org/en/latest/) `apt-get install python-requests`  or `pip install requests`

Cautions and Notes:
1.  All opeartions use simulated login and fetching pages.
2.  Under the situation that this tools  DO NOT have renren api,it could be very slow because fetching pages needs lots of time.
3.  If the interface have not react ,please wait patiently.
4.  Need current directory write premission because it needs to write cookie to current directory
5.  It's just a practice for learning Python , Qt and Basic Http Knowledge.

Usage:
`python r-refactory.py`