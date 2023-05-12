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
