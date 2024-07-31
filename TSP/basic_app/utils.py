import numpy as np
import pandas as pd
import openrouteservice
from openrouteservice.exceptions import ApiError
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

# Initialize the OpenRouteService client
client = openrouteservice.Client(key=API_KEY)

def parse_text_input_to_addresses(text_input):
    return text_input.splitlines()

def parse_csv_input_to_addresses(csv_file, sheet_name=None):
    if sheet_name:
        df = pd.read_excel(csv_file, sheet_name=sheet_name)
    else:
        df = pd.read_csv(csv_file)
    
    # Combine all columns into a single address string for each row
    addresses = df.apply(lambda row: ', '.join(row.values.astype(str)), axis=1).tolist()
    return addresses

def parse_text_file_to_addresses(text_file):
    addresses = text_file.read().decode('utf-8').splitlines()
    return addresses

def geocode_address(address):
    try:
        geocode_result = client.pelias_search(text=address)
        coordinates = geocode_result['features'][0]['geometry']['coordinates']
        return coordinates  # Return as (latitude, longitude)
    except (ApiError, IndexError) as e:
        print(f"Error geocoding {address}: {e}")
        # Fallback mechanism within a 1000m radius
        try:
            geocode_result = client.pelias_search(text=address, size=1, boundary_circle={'radius': 1000})
            coordinates = geocode_result['features'][0]['geometry']['coordinates']
            return coordinates  # Return as (latitude, longitude)
        except (ApiError, IndexError) as fallback_e:
            print(f"Fallback error geocoding {address}: {fallback_e}")
            return None


def create_distance_matrix(coordinates):
    try:
        matrix_result = client.distance_matrix(locations=coordinates, profile='driving-car', metrics=['distance'])
        distance_matrix = matrix_result['distances']  # Keep as list of lists
        return distance_matrix
    except ApiError as e:
        print(f"Error creating distance matrix: {e}")
        return np.inf

def process_input(input_type, input_data, sheet_name=None):
    if input_type == 'text':
        addresses = parse_text_input_to_addresses(input_data)
    elif input_type == 'file':
        if input_data.name.endswith('.csv'):
            addresses = parse_csv_input_to_addresses(input_data, sheet_name)
        elif input_data.name.endswith('.txt'):
            addresses = parse_text_file_to_addresses(input_data)
        else:
            raise ValueError("Unsupported file format")
    else:
        raise ValueError("Invalid input type")

    coordinates = [geocode_address(address) for address in addresses]
    coordinates = [coord for coord in coordinates if coord is not None]

    if len(coordinates) < 2:
        raise ValueError("Insufficient valid addresses for distance matrix creation")

    distance_matrix = create_distance_matrix(coordinates)
    return distance_matrix

class TravellingSalesmanProblem:
    def __init__(self, distance, start):
        self.distance_matrix = [[row[i] for row in distance] for i in range(len(distance[0]))]
        self.start_city = start
        self.total_cities = len(distance)

        self.end_state = (1 << self.total_cities) - 1
        self.memo = [[None for _col in range(1 << self.total_cities)] for _row in range(self.total_cities)]

        self.shortest_path = []
        self.min_path_cost = float('inf')

    def solve(self):
        self.__initialize_memo()

        for num_element in range(3, self.total_cities + 1):
            for subset in self.__initiate_combination(num_element):
                if self.__is_not_in_subset(self.start_city, subset):
                    continue

                for next_city in range(self.total_cities):
                    if next_city == self.start_city or self.__is_not_in_subset(next_city, subset):
                        continue

                    subset_without_next_city = subset ^ (1 << next_city)
                    min_distance = float('inf')

                    for last_city in range(self.total_cities):
                        if last_city == self.start_city or last_city == next_city or self.__is_not_in_subset(last_city, subset):
                            continue

                        new_distance = self.memo[last_city][subset_without_next_city] + self.distance_matrix[last_city][next_city]
                        if new_distance < min_distance:
                            min_distance = new_distance

                    self.memo[next_city][subset] = min_distance

        self.__calculate_min_cost()
        self.__find_shortest_path()

        self.shortest_path += [self.start_city]  # Use self.start_city
        self.shortest_path = self.shortest_path[::-1]

        self.min_path_cost += self.distance_matrix[self.shortest_path[1]][self.start_city]  # Use self.start_city

    def __calculate_min_cost(self):
        for i in range(self.total_cities):
            if i == self.start_city:
                continue

            path_cost = self.memo[i][self.end_state]
            if path_cost < self.min_path_cost:
                self.min_path_cost = path_cost

    def __find_shortest_path(self):
        state = self.end_state

        for i in range(1, self.total_cities):
            best_index = -1
            best_distance = float('inf')

            for j in range(self.total_cities):
                if j == self.start_city or self.__is_not_in_subset(j, state):
                    continue

                new_distance = self.memo[j][state]
                if new_distance <= best_distance:
                    best_index = j
                    best_distance = new_distance

            self.shortest_path.append(best_index)
            state = state ^ (1 << best_index)

        self.shortest_path.append(self.start_city)
        self.shortest_path.reverse()

    def __initialize_memo(self):
        for destination_city in range(self.total_cities):
            if destination_city == self.start_city:
                continue

            self.memo[destination_city][1 << self.start_city | 1 << destination_city] = self.distance_matrix[self.start_city][destination_city]

    def __initiate_combination(self, num_element):
        subset_list = []
        self.__initialize_combination(0, 0, num_element, self.total_cities, subset_list)
        return subset_list

    def __initialize_combination(self, subset, at, num_element, total_cities, subset_list):
        elements_left_to_pick = total_cities - at
        if elements_left_to_pick < num_element:
            return

        if num_element == 0:
            subset_list.append(subset)
        else:
            for i in range(at, total_cities):
                subset |= 1 << i
                self.__initialize_combination(subset, i + 1, num_element - 1, total_cities, subset_list)
                subset &= ~(1 << i)

    @staticmethod
    def __is_not_in_subset(element, subset):
        return ((1 << element) & subset) == 0




class NearestNeighbour:
    def __init__(self, distances, start_city=0):
        self.distances = distances
        self.start_city = start_city
        self.num_cities = len(distances)
        self.shortest_path = [start_city]
        self.min_path_cost = 0
        self.visited = [False] * self.num_cities
        self.visited[start_city] = True

    def run(self):
        current_city = self.start_city
        for _ in range(self.num_cities - 1):
            nearest_city = None
            nearest_distance = float('inf')
            for next_city in range(self.num_cities):
                if not self.visited[next_city] and 0 < self.distances[current_city][next_city] < nearest_distance:
                    nearest_city = next_city
                    nearest_distance = self.distances[current_city][next_city]
            self.shortest_path.append(nearest_city)
            self.min_path_cost += nearest_distance
            current_city = nearest_city
            self.visited[current_city] = True
        
        # Return to the starting city
        self.min_path_cost += self.distances[current_city][self.start_city]
        self.shortest_path.append(self.shortest_path[0])


    

