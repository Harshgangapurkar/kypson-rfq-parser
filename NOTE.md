# RFQ Parser — Approach and Evaluation

## 1. Approach

I developed a lightweight, rule-based RFQ parser using Python. The parser uses regular expressions and text normalization to identify product categories, quantities, units, GSM, micron specifications, and delivery locations. It supports Indian numerical formats such as lakh, lac, hazaar, and k, along with common product synonyms and location aliases.

I chose a deterministic, offline approach instead of an LLM to keep the parser fast, explainable, reproducible, and free from external API dependencies. The implementation also prioritizes distinguishing order quantities from individual bag capacity or weight.

## 2. Evaluation

- Test dataset: `my_tests.jsonl`
- Total labelled examples: 50
- Correct predictions: 50
- Incorrect predictions: 0
- Exact-match accuracy: **100%**

This score represents performance on my self-created development dataset and should not be interpreted as real-world accuracy.

## 3. Known Limitations and Failure Examples

The following examples illustrate input variations that the current parser does not fully support:

1. **"We are looking to procure fifty thousand laminated polypropylene sacks for delivery to Nagpur."**  
   The parser identifies Nagpur but cannot extract the quantity because it is written in words. It also returns no category because BOPP is not explicitly specified.

2. **"Require pachaas hazaar BOPP bags in Pune."**  
   Hindi number words are not supported by the current numerical extraction logic, so the quantity cannot be reliably extracted.

3. **"Need 50000 polypropylene laminated sacks in Mumbai."**  
   The parser may return no category because this description does not explicitly identify BOPP or another supported product category. More product context is needed to classify it reliably.

These examples highlight limitations in number-word recognition and product terminology. The parser intentionally avoids guessing ambiguous categories.

## 4. What I Would Do With 1,000 Real Labelled Examples

I would first analyse the dataset to identify common buyer expressions, synonyms, regional terminology, and formatting variations. I would divide the examples into training, validation, and independent test sets. I would use the data to improve extraction rules and evaluate whether a lightweight NLP or machine-learning approach offers a measurable improvement over the rule-based baseline.

I would also perform field-wise error analysis to identify which extraction fields need the most improvement.

## 5. Measuring Performance With Real Buyers

I would monitor field-wise accuracy, exact-match accuracy, missing-field rates, and incorrect predictions using real buyer messages and human-verified labels. I would collect user corrections, investigate recurring errors, and periodically evaluate the parser on a separate set of recent messages. This would help measure reliability and identify changes in buyer language over time.

## 6. Tools Used

Python, regular expressions, VS Code, and GeonamesCache were used for implementation and location recognition.  
ChatGPT was used as an AI development assistant for understanding requirements, debugging, code review, and test-case design; the implementation and testing were reviewed and executed locally.