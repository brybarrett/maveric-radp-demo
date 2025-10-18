# Maveric - RIC Algorithm Development Platform (RADP)

## Overview

Maveric is the **RIC Algorithm Development Platform (RADP)** - a developer platform that enables the development and evaluation of dynamic control policies for optimizing cellular network operations before deployment.

It leverages AI/ML approaches to provide realistic cellular network representations (Digital Twins) and demonstrates the Radio Intelligent Controller (RIC) paradigm through example algorithms.

---

## Core Workflow

The Maveric platform follows a straightforward workflow:

1. **Train a Digital Twin** - Create an AI model that simulates RF propagation
2. **Generate or Provide UE Tracks** - Define user equipment movement patterns
3. **Run RF Prediction** - Simulate signal strength across the network
4. **Orchestrate Jobs** - Manage simulation execution
5. **Consume Results** - Analyze simulation output

---

## Getting Started

### Prerequisites

- Docker installed and running
- Python 3.8+ (but less than 3.11)

### Quick Start

1. Clone the repository
2. Build the Docker image:
```bash
   docker build -t radp radp
```

3. Start RADP in production mode:
```bash
   docker compose -f dc.yml -f dc-prod.yml up -d --build
```

4. Install Python client dependencies:
```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r radp/client/requirements.txt
```

5. Run the example application:
```bash
   python3 apps/example/example_app.py
```

---

## Digital Twin Training

### What is a Digital Twin?

A Digital Twin is an AI model trained to predict RF (Radio Frequency) signal propagation in a cellular network. It learns from historical data to simulate how signals travel from cell towers to user devices.

### Train API

The Train API allows you to train a new RF Digital Twin model.

**Python Example:**
```python
radp_client.train(
    model_id="my_digital_twin_1",
    params={
        "maxiter": 100,
        "lr": 0.05,
        "stopping_threshold": 0.0001
    },
    ue_training_data="ue_training_data.csv",
    topology="topology.csv"
)
```

**Parameters:**
- `model_id` (required) - Unique identifier for this model
- `params` (required) - Training parameters:
  - `maxiter` - Maximum training iterations (default: 100)
  - `lr` - Learning rate (default: 0.05)
  - `stopping_threshold` - Training stops when improvement is below this threshold
- `ue_training_data` (required) - CSV file or pandas DataFrame with training data
- `topology` (required) - CSV file or pandas DataFrame with cell tower configuration

### UE Training Data Format

The training data must be a CSV file with these columns:

| Column | Type | Description |
|--------|------|-------------|
| cell_id | string | Cell tower identifier |
| avg_rsrp | float | Average signal strength (RSRP) for this location |
| lon | float | Longitude coordinate |
| lat | float | Latitude coordinate |
| cell_el_deg | float | Electrical antenna tilt in degrees |

**Example:**
```csv
cell_id,avg_rsrp,lon,lat,cell_el_deg
cell_1,-80,139.699058,35.644327,0
cell_1,-70,139.707889,35.647814,3
cell_1,-75,139.700024,35.643857,6
```

### Topology File Format

The topology file defines cell tower locations and configurations:

| Column | Type | Description |
|--------|------|-------------|
| cell_id | string | Cell tower identifier |
| cell_name | string | Human-readable name (optional) |
| cell_lat | float | Tower latitude |
| cell_lon | float | Tower longitude |
| cell_az_deg | int | Azimuth angle (direction tower faces) |
| cell_carrier_freq_mhz | int | Carrier frequency in MHz |

**Example:**
```csv
cell_id,cell_name,cell_lat,cell_lon,cell_az_deg,cell_carrier_freq_mhz
cell_1,Cell1,35.690556,139.691944,0,2100
cell_2,Cell2,35.690556,139.691944,120,2100
cell_3,Cell3,35.690556,139.691944,240,2100
```

### Training Process

1. The Digital Twin loads your training data and topology
2. It creates engineered features for each cell tower
3. The model trains using gradient descent to minimize prediction error
4. Training stops when max iterations is reached or improvement falls below threshold
5. The trained model is saved with your specified `model_id`

**Training typically takes a few minutes to several hours depending on data size and parameters.**

---

## UE Tracks (User Equipment Movement)

UE Tracks represent the movement patterns of mobile devices (phones, tablets) in your simulation.

### Option 1: Provide Your Own UE Data

Upload a CSV file with user equipment positions over time.

**Python Example:**
```python
simulation_event = {
    "ue_tracks": {
        "ue_data_id": "my_ue_data_1"
    }
}

radp_client.simulation(
    simulation_event=simulation_event,
    ue_data="ue_data.csv"
)
```

**UE Data Format:**

| Column | Type | Description |
|--------|------|-------------|
| mock_ue_id | string | Unique device identifier |
| lon | float | Longitude |
| lat | float | Latitude |
| tick | int | Time step (each tick = simulation_time_interval_seconds) |
| cell_id | string | Associated cell tower (optional) |

**Example:**
```csv
mock_ue_id,lon,lat,tick,cell_id
1,139.699058,35.644327,0,cell_1
1,139.699061,35.644322,1,cell_1
2,139.707889,35.647814,0,cell_2
2,139.707899,35.647813,1,cell_2
```

### Option 2: Generate UE Tracks Automatically

Maveric can generate realistic movement patterns using a Gaussian Markov mobility model.

**Python Example:**
```python
simulation_event = {
    "ue_tracks": {
        "ue_tracks_generation": {
            "ue_class_distribution": {
                "pedestrian": {
                    "count": 10,
                    "velocity": 1.4,  # meters/second
                    "velocity_variance": 0.3
                },
                "car": {
                    "count": 5,
                    "velocity": 10,  # meters/second
                    "velocity_variance": 2
                }
            },
            "lat_lon_boundaries": {
                "min_lat": 35.64,
                "max_lat": 35.70,
                "min_lon": 139.69,
                "max_lon": 139.72
            },
            "gauss_markov_params": {
                "alpha": 0.75,  # Randomness (0=random, 1=linear)
                "variance": 1.0,
                "rng_seed": 42  # For reproducibility
            }
        }
    }
}
```

**UE Classes:**
- `stationary` - Devices that don't move
- `pedestrian` - Walking speed (~1.4 m/s)
- `cyclist` - Bike speed (~5 m/s)
- `car` - Vehicle speed (~10-15 m/s)

---

## RF Prediction

RF Prediction uses your trained Digital Twin to simulate signal strength throughout the network.

### How It Works

1. Takes UE Track positions as input
2. Uses the trained Digital Twin model
3. Predicts RSRP (signal strength) for each position from each cell tower
4. Outputs predicted signal strength data

**Python Example:**
```python
simulation_event = {
    "simulation_time_interval_seconds": 0.01,  # 10ms between ticks
    "ue_tracks": {
        "ue_data_id": "my_ue_data"
    },
    "rf_prediction": {
        "model_id": "my_trained_digital_twin_1"
    }
}

radp_client.simulation(
    simulation_event=simulation_event,
    ue_data="ue_data.csv",
    config="cell_config.csv"
)
```

### Cell Configuration

You can adjust cell tower settings (like antenna tilt) for the simulation:

**Cell Config Format:**
```csv
cell_id,cell_el_deg
cell_1,10
cell_2,10
cell_3,12
```

**Common Use Cases:**
- "What if we change antenna tilt from 10° to 15°?"
- "How does signal coverage change with different tower configurations?"
- "What's the optimal antenna setup for this area?"

### RF Prediction Output

The output is a pandas DataFrame with predicted signal strength:

| Column | Description |
|--------|-------------|
| cell_id | Which cell tower |
| rxpower_dbm | Predicted signal strength in dBm |
| mock_ue_id | Which device |
| lon | Device longitude |
| lat | Device latitude |
| tick | Time step |

**Example Output:**
```
cell_id   rxpower_dbm  mock_ue_id  lon          lat         tick
cell_1    -73.58       0           -22.647      59.781      0
cell_1    -75.42       1           119.780      54.867      0
cell_1    -68.91       0           -23.176      59.498      1
```

---

## Simulation API

The Simulation API orchestrates the entire workflow: UE Tracks + RF Prediction.

**Python Example:**
```python
simulation_event = {
    "simulation_time_interval_seconds": 0.01,
    "ue_tracks": {
        "ue_tracks_generation": {
            "ue_class_distribution": {
                "pedestrian": {"count": 5, "velocity": 1.4, "velocity_variance": 0.3}
            },
            "lat_lon_boundaries": {
                "min_lat": 35.64, "max_lat": 35.70,
                "min_lon": 139.69, "max_lon": 139.72
            },
            "gauss_markov_params": {"alpha": 0.75, "variance": 1.0, "rng_seed": 42}
        }
    },
    "rf_prediction": {
        "model_id": "my_digital_twin_1"
    }
}

# Run simulation
response = radp_client.simulation(
    simulation_event=simulation_event,
    config="cell_config.csv"
)

simulation_id = response["simulation_id"]
```

### Simulation Response

The API returns a `simulation_id` that you use to track and retrieve results.

---

## Describe APIs

### Describe Model

Check the training status of a Digital Twin:
```python
status = radp_client.describe_model("my_digital_twin_1")
```

Returns information about whether the model has finished training and is ready for use.

### Describe Simulation

Check the status of a running simulation:
```python
status = radp_client.describe_simulation(simulation_id)
```

Returns whether the simulation has completed and results are ready.

---

## Consuming Simulation Output

Once a simulation completes, retrieve the results:
```python
results = radp_client.consume_simulation_output(simulation_id)
```

Returns a pandas DataFrame with all prediction data that you can analyze, visualize, or export.

---

## Job Orchestration

Maveric uses a job orchestration system to manage training and simulation tasks:

- Jobs are queued and executed asynchronously
- Multiple workers process jobs in parallel
- Kafka handles job messaging and coordination
- Each job has timeout limits (training: 12 hours, simulation stages: 15 minutes)

**What happens during a simulation:**
1. Job created and added to queue
2. Worker picks up job
3. UE Tracks stage executes (generates or loads movement data)
4. RF Prediction stage executes (runs Digital Twin predictions)
5. Results are stored and made available via consume API

---

## System Limitations

**Timeout Thresholds:**
- Training jobs: 12 hours maximum
- Simulation stages: 15 minutes per stage

**Python Version:**
- Requires Python >= 3.8.x and < 3.11.x
- Python 3.11 support blocked by PyTorch dependency

**GPU Support:**
- Optional Nvidia GPU acceleration available
- Requires Nvidia drivers and Container Toolkit
- Use `dc-cuda.yml` compose file for GPU support

---

## Common Workflows

### Workflow 1: Train and Test a Digital Twin

1. Prepare training data (UE RSRP measurements + topology)
2. Train the model using Train API
3. Check training status with Describe Model API
4. Run a test simulation with known UE paths
5. Compare predictions to actual measurements
6. Iterate on training parameters if needed

### Workflow 2: Coverage Optimization

1. Train a Digital Twin on current network data
2. Run simulations with different antenna tilt configurations
3. Compare signal coverage across configurations
4. Identify optimal settings
5. Deploy changes to real network

### Workflow 3: Network Planning

1. Train Digital Twin on existing towers
2. Simulate adding new towers at candidate locations
3. Generate realistic UE movement patterns
4. Evaluate coverage improvements
5. Prioritize tower deployments based on impact

---

## Example Applications

Maveric includes example applications:

**Basic Example:**
```bash
python3 apps/example/example_app.py
```

**Coverage and Capacity Optimization (CCO):**
```bash
python3 apps/coverage_capacity_optimization/cco_example_app.py
```

Runs in ~2 minutes and demonstrates antenna tilt optimization.

---

## Troubleshooting

**Simulation fails with timeout:**
- Reduce the amount of UE data
- Simplify the simulation (fewer UE devices)
- Check logs in Docker output

**Training doesn't converge:**
- Increase `maxiter` parameter
- Adjust learning rate (`lr`)
- Ensure training data quality (sufficient samples, correct format)

**Docker issues:**
- Run `docker container prune` to clean stopped containers
- Run `docker volume prune` to reset data (⚠️ removes all simulation data)

---

## Getting Help

- Check Docker logs: Look at terminal output from `docker compose up`
- Review example scripts in `apps/` directory
- Verify CSV file formats match specifications
- Ensure all required columns are present in data files

---

## Key Concepts Summary

- **Digital Twin**: AI model that simulates RF signal propagation
- **UE Tracks**: Movement patterns of mobile devices over time
- **RF Prediction**: Using Digital Twin to predict signal strength
- **RSRP**: Reference Signal Received Power (signal strength measurement)
- **Orchestration**: Job management system coordinating training and simulation
- **RIC**: Radio Intelligent Controller paradigm for network optimization