from backend.config import DATA_DIR
from backend.simulation.generator import generate_all
if __name__ == '__main__':
    print(generate_all(DATA_DIR))
