#views.py
from django.shortcuts import render
from django.http import HttpResponse
from .utils import *
from .forms import TSPForm
import pandas as pd
import openrouteservice
from openrouteservice.directions import directions
import folium
import polyline
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

# Initialize the OpenRouteService client
Client = openrouteservice.Client(key=API_KEY)

def home_view(request):
    return render(request, 'basic_app/home.html')

def dp_approach_view(request):
    if request.method == 'POST':
        form = TSPForm(request.POST, request.FILES)
        if form.is_valid():
            input_type = form.cleaned_data['input_type']
            
            try:
                if input_type == 'text':
                    input_data = form.cleaned_data['text_input']
                    addresses = parse_text_input_to_addresses(input_data)
                elif input_type == 'file':
                    input_data = request.FILES['csv_file']
                    sheet_name = form.cleaned_data.get('sheet_name')
                    if input_data.name.endswith('.csv'):
                        addresses = parse_csv_input_to_addresses(input_data, sheet_name)
                    elif input_data.name.endswith('.txt'):
                        addresses = parse_text_file_to_addresses(input_data)
                    else:
                        raise ValueError("Unsupported file format")
                else:
                    raise ValueError("Invalid input type")

                # Filter out empty addresses
                addresses = [address for address in addresses if address.strip()]
                if not addresses:
                    raise ValueError("No valid addresses provided")

                coordinates = []
                for address in addresses:
                    coord = geocode_address(address)
                    if coord is None:
                        print(f"Failed to geocode address: {address}")
                    else:
                        coordinates.append((coord, address))

                if len(coordinates) < 2:
                    raise ValueError("Insufficient valid addresses for distance matrix creation")

                distance_matrix = create_distance_matrix([coord[0] for coord in coordinates])

                min_distance = None
                min_path = None

                num_cities = len(distance_matrix)
                shortest_distance = float('inf')
                best_path = None

                for city in range(num_cities):
                    tsp_solver = TravellingSalesmanProblem(distance_matrix, city)
                    tsp_solver.solve()
                    if tsp_solver.min_path_cost < shortest_distance:
                        shortest_distance = tsp_solver.min_path_cost
                        best_path = tsp_solver.shortest_path

                min_distance = shortest_distance
                min_path = best_path

                if min_path is None:
                    raise ValueError("No valid path found")

                # Rearrange coordinates based on the optimal path
                reordered_coordinates = [coordinates[i] for i in min_path]
                reordered_coords_only = [coord[0] for coord in reordered_coordinates]
                route = directions(Client, reordered_coords_only)

                # Decode the polyline to get a list of (latitude, longitude) tuples
                encoded_polyline = route['routes'][0]['geometry']
                decoded_points = polyline.decode(encoded_polyline)

                # Create a map centered around the first point in the polyline
                map_center = decoded_points[0]
                route_map = folium.Map(location=map_center, zoom_start=13)

                # Add the route to the map
                folium.PolyLine(decoded_points, color='blue', weight=5, opacity=0.7).add_to(route_map)

                # Add markers for each coordinate with popups
                for coord, address in reordered_coordinates:
                    folium.Marker(location=coord[::-1], popup=address).add_to(route_map)

                # Save the map as an HTML file
                map_html = route_map._repr_html_()

                context = {
                    'min_distance': min_distance / 1000,
                    'min_path': min_path,
                    'map_html': map_html
                }
                return render(request, 'basic_app/dp_approach.html', context)
            except Exception as e:
                return HttpResponse(f"An error occurred: {e}")
    else:
        form = TSPForm()
    return render(request, 'basic_app/dp_approach.html', {'form': form})


def nn_approach_view(request):
    if request.method == 'POST':
        form = TSPForm(request.POST, request.FILES)
        if form.is_valid():
            input_type = form.cleaned_data['input_type']
            
            try:
                if input_type == 'text':
                    input_data = form.cleaned_data['text_input']
                    addresses = parse_text_input_to_addresses(input_data)
                elif input_type == 'file':
                    input_data = request.FILES['csv_file']
                    sheet_name = form.cleaned_data.get('sheet_name')
                    if input_data.name.endswith('.csv'):
                        addresses = parse_csv_input_to_addresses(input_data, sheet_name)
                    elif input_data.name.endswith('.txt'):
                        addresses = parse_text_file_to_addresses(input_data)
                    else:
                        raise ValueError("Unsupported file format")
                else:
                    raise ValueError("Invalid input type")

                # Filter out empty addresses
                addresses = [address for address in addresses if address.strip()]
                if not addresses:
                    raise ValueError("No valid addresses provided")

                coordinates = []
                for address in addresses:
                    coord = geocode_address(address)
                    if coord is None:
                        print(f"Failed to geocode address: {address}")
                    else:
                        coordinates.append((coord, address))

                if len(coordinates) < 2:
                    raise ValueError("Insufficient valid addresses for distance matrix creation")

                distance_matrix = create_distance_matrix([coord[0] for coord in coordinates])

                min_distance = None
                min_path = None

                num_cities = len(distance_matrix)
                shortest_distance = float('inf')
                best_path = None

                for city in range(num_cities):
                    tsp_solver = NearestNeighbour(distance_matrix, city)
                    tsp_solver.run()
                    if tsp_solver.min_path_cost < shortest_distance:
                        shortest_distance = tsp_solver.min_path_cost
                        best_path = tsp_solver.shortest_path

                min_distance = shortest_distance
                min_path = best_path

                if min_path is None:
                    raise ValueError("No valid path found")

                # Rearrange coordinates based on the optimal path
                reordered_coordinates = [coordinates[i] for i in min_path]
                reordered_coords_only = [coord[0] for coord in reordered_coordinates]
                route = directions(Client, reordered_coords_only)

                # Decode the polyline to get a list of (latitude, longitude) tuples
                encoded_polyline = route['routes'][0]['geometry']
                decoded_points = polyline.decode(encoded_polyline)

                # Create a map centered around the first point in the polyline
                map_center = decoded_points[0]
                route_map = folium.Map(location=map_center, zoom_start=13)

                # Add the route to the map
                folium.PolyLine(decoded_points, color='blue', weight=5, opacity=0.7).add_to(route_map)

                # Add markers for each coordinate with popups
                for coord, address in reordered_coordinates:
                    folium.Marker(location=coord[::-1], popup=address).add_to(route_map)

                # Save the map as an HTML file
                map_html = route_map._repr_html_()

                context = {
                    'min_distance': min_distance / 1000,
                    'min_path': min_path,
                    'map_html': map_html
                }
                return render(request, 'basic_app/nn_approach.html', context)
            except Exception as e:
                return HttpResponse(f"An error occurred: {e}")
    else:
        form = TSPForm()
    return render(request, 'basic_app/nn_approach.html', {'form': form})
