<h1>SquatchMap</h1>

This Leaflet project is meant as a fun way to explore the BFRO's collection of bigfoot sightings, and maybe improve their data through community updates of bad locations. 

<a href='http://www.bfro.net/REF/aboutbfr.asp'>Learn more about the BFRO</a>.

The site is based on a python script, PythonServer/UpdatePointsJSON.py, which I have scheduled to run weekly on my PC. It downloads the most recent KML of bigfoot sightings from the BFRO, converts it to a geoJSON and publishes to this repo. 

Also, there is a google form accessible from the site which users can use to update bad locations. The script also downloads the form responses and updates points based on them. 

<h2>About the data</h2>
The data that this map uses was created and is owned by the BFRO. It comes from a subset of the <a href="http://www.bfro.net/GDB/classify.asp">BFRO Comprehensive Sightings Database</a>, which contains thousands more reports which do not have attached coordinates. 

For a number of reasons, many of the locations displayed on this map do not reflect the actual location of the incident. For this reason, the BFRO discontinued making the spatial component to their database public in 2019. This map's author decided that this information is interesting, despite its errors, and that the approximate locations provide an engaging way to explore the BFRO's vast database of credible sightings. However, this map remains unaffiliated with the BFRO website. Hopefully, through community updates the data can be improved.

You are free to download the JSON from this repository to use for your own <i>non-commercial</i> uses. This file is a version of the BFRO data updated by this site's community, which should have more accurate locations. 

<h3>Licence</h3>
Data from the BFRO, contained in BFRO_Points.json, is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa]. 

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
