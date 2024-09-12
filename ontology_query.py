import requests
import json

class OntologyQueryProcess:
    def __init__(self, ontology_url):
        self.ontology_url = ontology_url

    
    def _build_query(self, temperature=None, salinity=None, oxygen=None):
        prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX torsk: <http://www.marinehabitatweb.org/torsk#>
"""

        select_clause = "SELECT ?individual ?name"
        where_clause = "WHERE { ?individual torsk:has_name ?name ;"
        filters = []

        if temperature is not None:
            select_clause += " ?maxTemp ?minTemp"
            where_clause += " torsk:has_pref_max_temp ?maxTemp ; torsk:has_pref_min_temp ?minTemp ;"
            filters.append(f"{temperature} > ?minTemp && {temperature} < ?maxTemp")

        if salinity is not None:
            select_clause += " ?maxSalinity ?minSalinity"
            where_clause += " torsk:has_pref_max_salinity ?maxSalinity ; torsk:has_pref_min_salinity ?minSalinity ;"
            filters.append(f"{salinity} > ?minSalinity && {salinity} < ?maxSalinity")

        if oxygen is not None:
            select_clause += " ?maxOxy ?minOxy"
            where_clause += " torsk:has_pref_max_oxy ?maxOxy ; torsk:has_pref_min_oxy ?minOxy ;"
            filters.append(f"{oxygen} > ?minOxy && {oxygen} < ?maxOxy")

        # Remove the trailing semicolon and add the closing brace
        where_clause = where_clause.rstrip(";") + " ."

        # Add the filters
        if filters:
            where_clause += " FILTER (" + " && ".join(filters) + ") ."

        where_clause += " }"

        query = prefixes + select_clause + " " + where_clause
        return query


    def query_species(self, temperature=None, salinity=None, oxygen=None):
        query = self._build_query(temperature, salinity, oxygen)
        response = requests.post(self.ontology_url, data={'query': query})
        return response.json()
    

    def query_species_parameters(self, individual):
        query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX torsk: <http://www.marinehabitatweb.org/torsk#>

SELECT ?individual ?maxTemp ?minTemp ?maxSalinity ?minSalinity ?maxOxy ?minOxy
WHERE {{
    ?individual torsk:has_name "{individual}" ;
                torsk:has_pref_max_temp ?maxTemp ;
                torsk:has_pref_min_temp ?minTemp ;
                torsk:has_pref_max_salinity ?maxSalinity ;
                torsk:has_pref_min_salinity ?minSalinity ;
                torsk:has_pref_max_oxy ?maxOxy ;
                torsk:has_pref_min_oxy ?minOxy .
}}
"""
        response = requests.post(self.ontology_url, data={'query': query})
        return response.json()
    

    def extract_bindings(self, response):
        if isinstance(response, str):
            response_data = json.loads(response)
        else:
            response_data = response
        
        # Extract the bindings
        bindings = response_data.get("results", {}).get("bindings", [])
        
        return bindings
