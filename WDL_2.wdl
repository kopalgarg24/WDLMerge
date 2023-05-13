version 1.0

task greet {
  input {
    String name
  }
  
  command {
    echo "Hello, ${name}!"
  }
  
  output {
    String greeting = read_string(stdout())
  }
}

workflow myWorkflow {
  input {
    String person
  }
  
  call greet {
    input:
      name = person
  }
  
  output {
    String finalGreeting = greet.greeting
  }
}
