# Travelling Salesman Problem Solver

This project provides a solution to the Travelling Salesman Problem (TSP) using two different approaches: Dynamic Programming and Nearest Neighbour. It leverages Python, Django, HTML, CSS, and JavaScript, along with various libraries and APIs to provide an interactive solution.

## Tech Stack

- **Python**
- **Django** (web framework)
- **HTML**, **CSS**, **JavaScript** (frontend)
- **OpenRouteService (ORS) API** (geocoding, distance matrix, and directions)
- **Folium** (map visualization)
- **Polyline** (route encoding/decoding)
- **Pandas** (data manipulation)

## Problem Solved

The project addresses the Travelling Salesman Problem (TSP), which aims to find the shortest possible route that visits a set of locations exactly once and returns to the origin.

## Methods Used

1. **Dynamic Programming**: A method that solves the problem by breaking it down into simpler subproblems and storing the solutions of subproblems.
2. **Nearest Neighbour**: A heuristic approach that builds the route by iteratively visiting the nearest unvisited location.

## Features

- **Address Input**: Supports input via text, CSV file, or text file.
- **Geocoding**: Addresses are converted into geographic coordinates using the ORS API.
- **Distance Matrix**: Calculates distances between all pairs of coordinates.
- **TSP Solution**: Utilizes Dynamic Programming and Nearest Neighbour methods to find the optimal route.
- **Directions Visualization**: Displays the optimal route on an interactive map using Folium and Polyline.

## Requirements

To run this project, you need the following Python packages:

- asgiref==3.8.1
- branca==0.7.2
- certifi==2024.7.4
- charset-normalizer==3.3.2
- Django==5.0.7
- folium==0.17.0
- idna==3.7
- Jinja2==3.1.4
- MarkupSafe==2.1.5
- numpy==2.0.1
- openrouteservice==2.3.3
- pandas==2.2.2
- polyline==2.0.2
- python-dateutil==2.9.0.post0
- python-dotenv==1.0.1
- pytz==2024.1
- requests==2.32.3
- six==1.16.0
- sqlparse==0.5.1
- tzdata==2024.1
- urllib3==2.2.2
- xyzservices==2024.6.0


You can install these packages using the following command:

```sh
pip install asgiref==3.8.1 branca==0.7.2 certifi==2024.7.4 charset-normalizer==3.3.2 Django==5.0.7 folium==0.17.0 idna==3.7 Jinja2==3.1.4 MarkupSafe==2.1.5 numpy==2.0.1 openrouteservice==2.3.3 pandas==2.2.2 polyline==2.0.2 python-dateutil==2.9.0.post0 python-dotenv==1.0.1 pytz==2024.1 requests==2.32.3 six==1.16.0 sqlparse==0.5.1 tzdata==2024.1 urllib3==2.2.2 xyzservices==2024.6.0
```
## Setting up Environment Variables

- Create a .env file in the root directory and add your ORS API key:

- OPENROUTESERVICE_API_KEY=your_api_key_here

