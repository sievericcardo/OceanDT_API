from typing import Union

from fastapi import FastAPI
from opendrift_runner import OpendriftRunner 
from ontology_query import OntologyQueryProcess

from pydantic import BaseModel
from typing import Optional

import threading

app = FastAPI()

class SimulationRequest(BaseModel):
    model_name: Optional[str] = "fjordos"
    latitude: Optional[float] = 59.9019
    longitude: Optional[float] = 10.7469
    deploy_time: Optional[str] = "2024-09-11-09-00"
    data_drifter: bool
    file: str
    total_time: int
    time_step: int
    time_step_output: int
    animation: Optional[bool] = False
    graph: Optional[bool] = False
    location: Optional[str] = None
    intime: Optional[str] = None


class QueryRequest(BaseModel):
    url: str
    temperature: Optional[float] = None
    salinity: Optional[float] = None
    oxygen: Optional[float] = None


class SpeciesParametersRequest(BaseModel):
    url: str
    individual: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def _run_rimulation(request: SimulationRequest):
    # Get the parameters passed in the post request
    model_name = request.model_name
    latitude = request.latitude
    longitude = request.longitude
    deploy_time = request.deploy_time
    data_drifter = request.data_drifter
    file = request.file
    total_time = request.total_time
    time_step = request.time_step
    time_step_output = request.time_step_output

    # Run the simulation
    opendrift_runner = OpendriftRunner(model_name)
    opendrift_runner.run(latitude, longitude, deploy_time, data_drifter, file, total_time, time_step, time_step_output)

    if request.animation:
        opendrift_runner.output_animation(request.location, request.intime)
    if request.graph:
        opendrift_runner.output_graph(request.location, request.intime)

    return {"status": "success"}


@app.post("/opendrift_runner")
def run_simulation_in_background(request: SimulationRequest):
    def target():
        result = _run_rimulation(request)
        # Ensure any UI updates are dispatched to the main thread
        # For example, using a GUI framework like Tkinter or PyQt
        # Here we just print the result
        print(result)

    thread = threading.Thread(target=target)
    thread.start()


@app.post("/species")
def query_species(request: QueryRequest):
    temperature = request.temperature
    salinity = request.salinity
    oxygen = request.oxygen
    url = request.url

    print(f"Querying species with temperature: {temperature}, salinity: {salinity}, oxygen: {oxygen}")

    # Query the ontology
    ontology_query = OntologyQueryProcess(url)
    response = ontology_query.query_species(temperature, salinity, oxygen)

    return {"status": "success", "data": ontology_query.extract_bindings(response)}


@app.post("/species_parameters")
def query_species_parameters(request: SpeciesParametersRequest):
    individual = request.individual
    url = request.url

    print(f"Querying species parameters for individual: {individual}")

    # Query the ontology
    ontology_query = OntologyQueryProcess(url)
    response = ontology_query.query_species_parameters(individual)

    return {"status": "success", "data": ontology_query.extract_bindings(response)}