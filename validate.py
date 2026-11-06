
import json
from parse import parse_rfq


def validate_tests():
    total = 0
    passed = 0
    failed = 0

    # Open the JSONL test dataset
    with open("my_tests.jsonl", "r", encoding="utf-8") as file:

        # Read each line separately
        for line_number, line in enumerate(file, start=1):

            # Ignore blank lines between batches
            if not line.strip():
                continue

            total += 1

            try:
                # Convert the JSON line into a Python dictionary
                test_case = json.loads(line)

                # Get the input message and expected output
                text = test_case["text"]
                expected = test_case["expected"]

                # Run our RFQ parser
                actual = parse_rfq(text)

                # Compare actual output with expected output
                if actual == expected:
                    passed += 1
                    print(f"PASS - Line {line_number}: {text}")

                else:
                    failed += 1
                    print(f"\nFAIL - Line {line_number}: {text}")
                    print("Expected:", expected)
                    print("Actual:  ", actual)
                    print("-" * 60)

            except Exception as error:
                failed += 1
                print(f"\nERROR - Line {line_number}: {error}")

    # Display the final results
    print("\n" + "=" * 50)
    print("          RFQ PARSER TEST RESULTS")
    print("=" * 50)
    print(f"Total tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    if total > 0:
        accuracy = (passed / total) * 100
        print(f"Accuracy    : {accuracy:.2f}%")

    print("=" * 50)


if __name__ == "__main__":
    validate_tests()
