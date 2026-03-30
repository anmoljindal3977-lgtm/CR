import json
from agents.data_validator import validate_application

def main():
    with open("data/sample_input.json") as f:
        data = json.load(f)

    result = validate_application(data)
    print("\nValidation Result:")
    print(result)

if __name__ == "__main__":
    main()