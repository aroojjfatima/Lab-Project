import re
from IPython.display import HTML, display
import ipywidgets as widgets

def tokenize_and_validate(input_string):
    patterns = [
        (r'\s+', None),  # Ignore whitespaces
        (r'\+', 'Operator: +'),
        (r'-', 'Operator: -'),
        (r'\*', 'Operator: *'),
        (r'/', 'Operator: /'),
        (r'\^', 'Operator: ^'),
        (r'=', 'Assignment: ='),
        (r';', 'Delimiter: ;'),
        (r'\(', 'Left Paren: ('),
        (r'\)', 'Right Paren: )'),
        (r'\d+(\.\d+)?', 'Number:'),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', 'Var:')
    ]

    tokens = []
    input_string = input_string.strip()
    position = 0

    while position < len(input_string):
        match = False
        for pattern, token_type in patterns:
            regex = re.compile(pattern)
            regex_match = regex.match(input_string, position)
            if regex_match:
                match = True
                if token_type:  # Only add token if it's not None (whitespace is None)
                    tokens.append((token_type, regex_match.group(0)))
                position = regex_match.end()
                break

        if not match:  # No pattern matched
            return None, f"Syntax error: Unrecognized token starting at '{input_string[position:]}'"

    return tokens, validate_tokens(tokens)

def validate_tokens(tokens):
    if not tokens:
        return "Syntax error: No tokens found."

    if tokens[-1][1] != ';':
        return "Syntax error: Missing semicolon at the end."

    # Check for balanced parentheses
    error = check_balanced_parentheses(tokens)
    if error:
        return error
    
    # Check for operator and operand issues
    error = check_operators_and_operands(tokens)
    if error:
        return error

    return "No syntax errors found."

def check_balanced_parentheses(tokens):
    stack = []
    for _, token_value in tokens:
        if token_value == '(':
            stack.append(token_value)
        elif token_value == ')':
            if not stack or stack[-1] != '(':
                return "Syntax error: Unmatched parenthesis"
            stack.pop()
    if stack:
        return "Syntax error: Unbalanced parenthesis"
    return None

def check_operators_and_operands(tokens):
    previous_type = None
    for token_type, token_value in tokens:
        if 'Operator' in token_type or 'Assignment' in token_type:
            if previous_type is None or 'Operator' in previous_type:
                return "Syntax error: Operator without left operand."
            if 'Operator' in token_type:
                previous_type = token_type
        elif 'Var' in token_type or 'Number' in token_type:
            if previous_type == 'Var' or previous_type == 'Number':
                return "Syntax error: Missing operator between operands."
            previous_type = token_type
        else:
            previous_type = token_type
    return None

# Custom CSS to improve the appearance
style = """
<style>
    .widget-label { font-weight: bold; }
    .output_area {
        border: 1px solid #ddd;
        box-shadow: 5px 5px 20px #eee;
        padding: 10px;
        margin-top: 20px;
    }
</style>
"""
display(HTML(style))

# Create widgets
text_area = widgets.Textarea(
    value='',
    placeholder='Type your code here...',
    description='Code:',
    disabled=False,
    layout=widgets.Layout(width='100%', height='200px')
)
text_area.add_class('code-area')

check_button = widgets.Button(description="Check Syntax")
check_button.style.button_color = 'green'

output_area = widgets.Output()

def on_button_clicked(b):
    with output_area:
        output_area.clear_output()
        input_code = text_area.value
        tokens, message = tokenize_and_validate(input_code)
        if tokens is None or "Syntax error" in message:
            print(message)  # Print syntax error
        else:
            for token in tokens:
                print(token)  # Print each token as output

check_button.on_click(on_button_clicked)

display(widgets.VBox([text_area, check_button, output_area]))
