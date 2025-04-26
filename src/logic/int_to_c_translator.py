import sys

def write_to_c(filename, outfile, output_box=None):
    """
    Reads an intermediate (.int) file and writes a translated C program to outfile,
    using your professor's conversion logic. Logs messages to output_box if provided.
    """
    def log(message):
        if output_box is not None:
            output_box.append(message)
        else:
            print(message)
    
    def add_to_list(lst, x):
        try:
            # Try converting to int or float to see if it is numerical.
            int(x)
            float(x)
            numerical = True
        except:
            numerical = False
        if x not in lst and not numerical:
            lst.append(x)
        return lst

    variables = []

    try:
        fout = open(outfile, 'w')
    except Exception as e:
        log(f"Error opening output file '{outfile}': {e}")
        return

    print("#include <stdio.h>", file=fout)
    print("\nint main()", file=fout)
    print("{", file=fout)

    # First pass: determine variable declarations.
    try:
        with open(filename, 'r') as file:
            for s in file:
                # Replace ':=' temporarily with '#' to avoid conflict with ':' splitting.
                s = s.replace(':=', "#").replace(":", ',')
                words = s.split(',')
                # Restore ':=' and also replace '@' with '$'
                for i, w in enumerate(words):
                    words[i] = w.strip().replace('#', ':=').replace('@', '$')
                if len(words) < 2:
                    continue
                if words[1] == ':=':
                    variables = add_to_list(variables, words[2])
                    if len(words) > 4:
                        variables = add_to_list(variables, words[4])
                if words[1] in ['+', '-', '*', '/']:
                    variables = add_to_list(variables, words[2])
                    if len(words) > 3:
                        variables = add_to_list(variables, words[3])
                    if len(words) > 4:
                        variables = add_to_list(variables, words[4])
                if words[1] in ['=', '<>', '<=', '>=', '>', '<']:
                    variables = add_to_list(variables, words[2])
                    if len(words) > 3:
                        variables = add_to_list(variables, words[3])
    except Exception as e:
        log(f"Error reading input file '{filename}' during variable declaration pass: {e}")
        fout.close()
        return

    for x in variables:
        print("int", x, ';', file=fout)
    print(file=fout)

    # Second pass: translate each line.
    try:
        with open(filename, 'r') as file:
            for s in file:
                s = s.replace(':=', "#").replace(":", ',')
                words = s.split(',')
                for i, w in enumerate(words):
                    words[i] = w.strip().replace('#', ':=').replace('@', '$')
                if len(words) < 2:
                    continue
                # Write the label.
                print('L' + words[0] + ': ', end='', file=fout)
                if words[1] == ':=':
                    if len(words) > 4:
                        print(words[4] + '=' + words[2] + ';', end='', file=fout)
                    else:
                        log(f"Error: Not enough fields in assignment line: {s.strip()}")
                        fout.close()
                        return
                elif words[1] == '+':
                    if len(words) > 3:
                        print(words[4] + '=' + words[2] + '+' + words[3] + ';', end='', file=fout)
                    else:
                        log(f"Error: Not enough fields in addition line: {s.strip()}")
                        fout.close()
                        return
                elif words[1] == '-':
                    if len(words) > 3:
                        print(words[4] + '=' + words[2] + '-' + words[3] + ';', end='', file=fout)
                    else:
                        log(f"Error: Not enough fields in subtraction line: {s.strip()}")
                        fout.close()
                        return
                elif words[1] == '*':
                    if len(words) > 3:
                        print(words[4] + '=' + words[2] + '*' + words[3] + ';', end='', file=fout)
                    else:
                        log(f"Error: Not enough fields in multiplication line: {s.strip()}")
                        fout.close()
                        return
                elif words[1] == '/':
                    if len(words) > 3:
                        print(words[4] + '=' + words[2] + '/' + words[3] + ';', end='', file=fout)
                    else:
                        log(f"Error: Not enough fields in division line: {s.strip()}")
                        fout.close()
                        return
                elif words[1] == 'jump':
                    print('goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '=':
                    print('if (' + words[2] + ' == ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '<>':
                    print('if (' + words[2] + ' != ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '<=':
                    print('if (' + words[2] + ' <= ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '>=':
                    print('if (' + words[2] + ' >= ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '>':
                    print('if (' + words[2] + ' > ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == '<':
                    print('if (' + words[2] + ' < ' + words[3] + ') goto L' + words[4] + ';', end='', file=fout)
                elif words[1] == 'out':
                    print('printf("%d\\n",' + words[2] + ');', end='', file=fout)
                elif words[1] == 'in':
                    print('scanf("%d",&' + words[2] + ');', end='', file=fout)
                elif words[1] in ['begin_block', 'end_block', 'halt']:
                    # These operations are ignored.
                    pass
                elif words[1] in ['par', 'call', 'retv', 'ret']:
                    log(f"Error: functions not supported: {words[1]}")
                    fout.close()
                    return
                else:
                    log(f"Error: unknown operator in line: {words}")
                    fout.close()
                    return
                print(file=fout)
    except Exception as e:
        log(f"Error processing input file '{filename}' during translation: {e}")
        fout.close()
        return

    print('}\n', file=fout)
    fout.close()
    log(f"Conversion complete. Generated C file saved as '{outfile}'.")

def extract_input_variables(filename):
    inputs = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().replace(':', ',').split(',')
                if len(parts) > 2 and parts[1].strip() == 'in':
                    var = parts[2].strip()
                    if var not in inputs:
                        inputs.append(var)
    except Exception as e:
        print(f"Error reading .int file to extract inputs: {e}")
    return inputs
