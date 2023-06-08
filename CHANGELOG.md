# Change Log

Important changes to this project that affect users will be documented in this file.    
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Added a log rotate so WSGI logs get rotated.
- Added an example PBSWeb HTML page.
- Added nginx config files and ensure nginx starts.
- Fixed missing comparison in template for queue.
- Fixed print statements for Python 3.
- Fixed bug as cpu and mem ratios are strings.
- Fixed bug as in Python 3 dictionaries are no longer orderable.
- Moved code and templates to under src/

## 2.1.0 - 13 July 2022

2022-07-13: Tagged v2.1.0

- User no longer needs to configure Nginx themselves. The install script will do this.
- Web page will display a more detailed version number if not a tagged release.
- Fixed bug where a queue with no `max_run` set would raise an error.
- Fixed error where `pbsserver` was not specified in `pbsweb.py`.

## 2.0.0 - 14 June 2022

2022-06-14: Tagged v2.0.0

2022-06-08:

- Now uses Python 3.8 instead of Python 2.7.
- Improved install scripts.
- Lots of minor fixes.
- Improved documentation.

## 1.1.0 - 12 Nov 2020

2020-11-12: Tagged v1.1.0

2020-11-12: Corrected info on the sockets.

2020-11-10:

 - Updated `max_runs` to correct format.
 - Changed to make `exec_hosts` and `exec_vnodes` consistent.
 - Merge pull requests from Hendrik von Schöning.

2020-11-06:

 - Update pbsweb.ini
 - Changed socket in nginx configuration. 
 - Merge pull request from Hendrik von Schöning.

2020-11-04: Made it clearer to use Python version 2.7.

2020-10-28:

 - Changed socket in nginx configuration (Hendrik von Schöning).
 - Show all hosts used by a job if it is run on multiple nodes (Hendrik von Schöning).
 - More stable when no memory resources were allocated (Hendrik von Schöning).
    
2020-07-29: Updated `max_run` to correct syntax.

2020-07-21:

 - Remove daemonize & change socket location for Centos 8.
 - Changed hostname.
 - Changed python include.

2020-04-07: Added `_show_attr_name_remapping` debugging function.

2020-04-02: Removed whitespace.

2019-10-23: Updates from PBS version 14 to 18.

2019-08-01:
 
 - Attrib `resource_list_walltime` is always present.
 - Changed limit to requested.

2019-07-31:

 - Minor change to formatting.
 - Added path so pbs can be found.

2019-07-30:

 - Updated requirements.
 - Minor formatting, remove UTS specific hostnames and user ids.

2019-07-29: Remove absolute pathname.

2019-02-04: Moved install details to separate file.

2019-01-23:

 - Fix link to license.
 - Updated README & added screenshot.

## 1.0.0 - 23 Jan 2019

Initial git commit and public release.

## 0.1.0 - Prior to 2019

2018-11-28: Changed to use jinja2 templates.

2018-10-24: Changed to work with new PBS queue format.

2017-10-09: Removed login and auth stuff.

2014-12-12: Added queues.

2014-12-10: First version.

