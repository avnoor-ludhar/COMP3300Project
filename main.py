import json
import sys

if __name__ == "__main__":
    input_file = sys.argv[1]

    with open(input_file) as f:
        data = json.load(f)
    
    print(data)

    result = []

    print(json.dumps(result, indent=2))
