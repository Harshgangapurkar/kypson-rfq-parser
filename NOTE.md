# RFQ Parser — Approach and Evaluation

## 1. Approach

I built a lightweight, rule-based RFQ parser using Python. The parser uses regular expressions and text normalization to extract six key fields: product category, quantity, unit, GSM, micron, and delivery location. It supports seven packaging categories, common product synonyms, Indian number formats, and location aliases. For location identification, I used GeoNamesCache. To improve performance, I implemented a cached combined regular-expression matcher. I chose a rule-based approach instead of using a large language model to keep the parser fast, transparent, and free from external API dependencies.

## 2. Score on `my_tests.jsonl`

- Total examples: 50
- Correct predictions: 50
- Incorrect predictions: 0
- Exact-match accuracy: **100%**
- Execution time: **0.71 seconds**

## 3. Three Messages the Parser Gets Wrong, and Why

1. **"We are looking to procure fifty thousand laminated polypropylene sacks for delivery to Nagpur."**

   The parser may fail to extract the quantity because it is written in words rather than digits. The product description is also vague because it does not clearly match a supported category.

2. **"Require pachaas hazaar BOPP bags in Pune."**

   The parser does not recognize Hindi number expressions such as "pachaas hazaar", so it cannot reliably extract the quantity.

3. **"Need 50000 polypropylene laminated sacks in Mumbai."**

   The parser might not identify the product category because the description omits terms like BOPP or other recognized category names. It avoids making guesses when the classification is uncertain.

## 4. What I Would Do Differently With 1,000 Real Labelled Examples

With 1,000 labelled examples, I would first analyse the messages to identify patterns in product descriptions, regional terms, spelling variations, and quantity formats. I would divide the data into training, validation, and testing sets. Then, I would refine the extraction rules and evaluate whether lightweight NLP or machine-learning methods could improve the handling of ambiguous product categories and multilingual quantity inputs. I would also perform field-wise error analysis to identify areas that need the most improvement.

## 5. How I Would Know It Is Working With Real Buyers

I would track field-wise accuracy, exact-match accuracy, missing-field rates, and incorrect predictions using real buyer messages verified by humans. I would collect corrections from buyers or reviewers, look for recurring issues, and regularly test the parser on new messages. This would help me understand whether the parser is reliable and adapting to the way real buyers communicate.

## 6. Tools Used

Python, regular expressions, GeoNamesCache, and Cursor were used for building and improving the parser.  
ChatGPT helped with understanding requirements, debugging, code review, and designing test cases.
