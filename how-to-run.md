### How to run

This project is a customer simulation using the Mesa framework. Follow these steps to set up and run the project:

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (to clone the repository)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd meama-simulation
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows:**

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Generate Required Data Files

The project requires customer data to run. You have two options:

**Option A: Use the existing customer data (if available)**

- Ensure `data/customers.json` exists in the project

### 6. Run the Simulation

Finally, run the main simulation:

```bash
python -m src.mesa.run
```
