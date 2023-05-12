import openai

# Set up OpenAI API credentials
openai.api_key = 'key'

# List of input WDL files
input_wdls = [
    """
    # WDL 1
    
    task task1 {
        input {
            File input_file
            String param1
        }
        command {
            echo "Running task1 with input file: ${input_file} and param1: ${param1}"
        }
        output {
            File output_file = "output.txt"
        }
    }
    """,
    """
    # WDL 2
    
    task task2 {
        input {
            String input_string
        }
        command {
            echo "Running task2 with input string: ${input_string}"
        }
        output {
            File output_file = "output.txt"
        }
    }
    """
]

# Perform initial merging with GPT
def initial_merge_with_gpt(input_wdls):
    # Concatenate the input WDL files
    input_text = "\n".join(input_wdls)
    
    # Generate an initial guess for merging using GPT
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=input_text,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None
    )
    
    merged_wdl = response.choices[0].text.strip()
    return merged_wdl

# Example usage
merged_wdl = initial_merge_with_gpt(input_wdls)

# Print the initial merged WDL
print(merged_wdl)
