# Kypson RFQ Parser

This project was developed as part of an AI/ML assignment given by **Kypson Solutions Private Limited**.

I developed a lightweight, rule-based **RFQ (Request for Quotation) Parser** using Python. It converts unstructured packaging requirements from buyer messages into structured data.

The parser extracts six key fields:

- **Category** – Type of packaging product.
- **Quantity** – Required order quantity.
- **Unit** – Unit of measurement.
- **GSM** – Material weight specification.
- **Micron** – Material thickness.
- **Location** – Delivery destination, including Indian and international locations.

It uses regular expressions, text normalization, and GeoNamesCache for location recognition. Cached location matching improves processing speed without relying on external APIs or large language models.

## How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the parser evaluation:

```bash
python score.py my_tests.jsonl
```

## Evaluation Results

| Dataset | Accuracy | Runtime |
|---|---:|---:|
| Original (50 examples) | 100% | 0.71 seconds |
| Unseen (25 examples) | 100% | 0.70 seconds |

## Tech Stack

Python · Regular Expressions · GeoNamesCache

**Developed by:** Harsh Gangapurkar
