import re
import argparse


def process_vtt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    output_lines = []
    counter = 0
    buffer = []  # Temporary buffer to hold lines before joining

    for line in lines:
        if '-->' in line:
            counter += 1
            if counter % 30 == 1:  # Keep every 30th occurrence
                # Write the buffered lines (if any) to output
                if buffer:
                    output_lines.append(''.join(buffer).strip() + '\n')
                    buffer = []
                # Add a blank line before the 30th timestamp (if not the first)
                if counter > 1:
                    output_lines.append('\n')
                output_lines.append(line)
            else:
                # Skip this timestamp line
                continue
        else:
            # Add non-timestamp lines to the buffer
            if line.strip():  # Skip blank lines
                buffer.append(line.strip() + ' ')

    # Write any remaining buffered lines to output
    if buffer:
        output_lines.append(''.join(buffer).strip() + '\n')

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(output_lines)

def process_file_case(input_file, output_file, exceptions):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Define punctuation marks that indicate the end of a sentence
    sentence_end_punctuation = ['. ', '! ', '? ']

    # Process each line
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in lines:
            # Skip WebVTT metadata lines (e.g., "WEBVTT", timestamps, etc.)
            if line.strip() == '' or line.strip().startswith('WEBVTT') or re.match(r'^\d{2}:\d{2}:\d{2}', line.strip()):
                file.write(line)
                continue

            # Split the line into words
            words = re.findall(r'\S+|\s+', line)  # Preserve spaces and punctuation

            # Iterate through the words
            for i, word in enumerate(words):
                # Check if the word is the beginning of a paragraph or after punctuation
                is_paragraph_start = (i == 0 and line.strip() != '')
                is_after_punctuation = (i > 0 and any(words[i-1].endswith(p) for p in sentence_end_punctuation))

                # Check if the word is in the exceptions list
                is_exception = word.strip().strip('.,!?') in exceptions

                # If the word is not an exception and not at the start of a paragraph or sentence, uncapitalize it
                if not is_exception and not is_paragraph_start and not is_after_punctuation:
                    words[i] = word.lower() if word[0].isupper() else word

            # Reconstruct the line and write it to the output file
            file.write(''.join(words))



# Set up argument parsing
parser = argparse.ArgumentParser(description="Process VTT files.")
parser.add_argument('input_vtt', type=str, help='Path to the input VTT file')
parser.add_argument('output_vtt', type=str, help='Path to the output VTT file')

# Parse the arguments
args = parser.parse_args()

# Use the arguments
input_vtt = args.input_vtt
output_vtt = args.output_vtt

process_vtt(input_vtt, output_vtt)

exceptions = ["Android", "iOS", "Google", "Apple"]
process_file_case(output_vtt, output_vtt + "_case_fixed.vtt", exceptions)
