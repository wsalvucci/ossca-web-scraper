# OSSCA Web Scraper

This is a python web scraper for the OSSCA website, gathering all soccer games from 2003.

Currently, the program takes a long time to run due to OSSCA's website being very slow in returning requests for data. The hope is this process can be sped up some other way so that the program doesn't take *hours* to complete.

The program defaults to gathering Boys' games but this can be switched to Girls' games by changing the `&B_G=B` query paramater to `&B_G=G`
