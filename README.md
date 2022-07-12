# README

## Introduction

This small web application provides a simple web view of the nodes, queues and jobs 
on a High Performance Computer Cluster running the PBS batch scheduling system.
It was developed using PBS Professional but should also work with the open source PBS.
General information on PBS can be found at its Wikipedia entry 
[Portable Batch System](https://en.wikipedia.org/wiki/Portable_Batch_System) and the 
[PBS Professional Open Source Project](https://www.pbspro.org) homepage.
This project is hosted at the eResearch site at Github <https://github.com/UTS-eResearch/pbsweb>
and my personal site at <https://github.com/speleolinux/pbsweb>.

![Screenshot showing PBSWeb](pbsweb_screenshot.png)  
Screenshot showing the web application.

## Software Required

See INSTALL.md

## License

Copyright 2019 Mike Lake & University of Technology Sydney

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this software. If not, see https://www.gnu.org/licenses/.

## References

Information on the "Batch Interface Library" can be found in the 
"PBS Professional® Programmer's Guide". See the section "Batch Interface Library". 
This is the primary API to communicate with the PBS MoM. 

Bottle Python Web Framework: <https://bottlepy.org/docs/0.12/>

SWIG Tutorial: <https://www.swig.org/tutorial.html>

