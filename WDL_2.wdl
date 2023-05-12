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
