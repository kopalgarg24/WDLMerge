task Task1 {
    input {
        String input1
    }
    command {
        echo "Running Task1 with input: ${input1}"
    }
    output {
        String output1 = read_string(stdout())
    }
}

workflow Workflow1 {
    input {
        String workflow_input1
    }
    output {
        String workflow_output1 = Task1.output1
    }
    call Task1 {
        input:
            input1 = workflow_input1
    }
}
