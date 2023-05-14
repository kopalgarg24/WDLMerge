version 1.0
    workflow w {
        call sum as sum1 {
            input: x = 1, y = 2
        }
        Int twice = 2*sum1.z
        call sum as sum2 {
            input: x = sum1.z, y = twice
        }
    }
    task sum {
        input {
            Int x
            Int y
        }
        command {
            echo $(( ~{x} + ~{y} ))
        }
        output {
            Int z = read_int(stdout())
        }
    }