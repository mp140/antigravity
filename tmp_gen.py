import re

with open('backend/constants.py', 'r', encoding='utf-8') as f:
    content = f.read()

base_platforms = []
for i in range(21, 101):
    api = str(i % 2 == 0)
    rating = str(round(4.0 + (i % 10) / 10, 1))
    base_platforms.append(f'    {{"rank": {i}, "name": "Platform_{i}", "type": "Generic Broker", "fees": "Variable", "assets": "Stocks, Crypto", "rating": {rating}, "api": {api}, "min_deposit": "$50"}},')

addition = '\n'.join(base_platforms)

# Regex to safely replace ] of the PLATFORMS dict, assuming it is the last list in the file.
new_content = content.replace('    {"rank": 20', addition + '\n    {"rank": 20')
# Wait, replacing 20 is easier:

# Let's just find the last occurence of `]` and replace it. But this file might have other lists.
# Instead, target the specific list ending.

replacement = '    {"rank": 20, "name": "Capital.com", "type": "CFD Broker", "fees": "Spread-based", "assets": "CFDs, Crypto, Forex", "rating": 4.2, "api": True, "min_deposit": "$20"},\n' + addition + '\n]'

new_content = content.replace('    {"rank": 20, "name": "Capital.com", "type": "CFD Broker", "fees": "Spread-based", "assets": "CFDs, Crypto, Forex", "rating": 4.2, "api": True, "min_deposit": "$20"},\n]', replacement)

with open('backend/constants.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
