#!/usr/bin/env python3
import os
import WDL
import subprocess
import csv
def reconstruct_wdl(tasks, workflows):
    wdl_code = ""

    # Reconstruct tasks
    for task_name, task_info in tasks.items():
        task_code = f"task {task_name} {{\n"
        if task_info['inputs']:
            task_code += "    input {\n"
            for input_var in task_info['inputs']:
                task_code += f"        {input_var}\n"
            task_code += "    }\n"
        task_code += f"    command {{\n        {task_info['command']}\n    }}\n"
        if task_info['outputs']:
            task_code += "    output {\n"
            for output_var in task_info['outputs']:
                task_code += f"        {output_var}\n"
            task_code += "    }\n"
        task_code += "}\n\n"
        if task_info['runtime']:
            task_code += "    runtime {\n"
            for key, value in task_info['runtime'].items():
                task_code += f"        {key} = {value}\n"
            task_code += "    }\n"
        task_code += "}\n\n"

        wdl_code += task_code

    # Combine workflows
    if workflows:
        combined_workflow = workflows[0]
        combined_workflow_name = "CombinedWorkflow"
        combined_workflow_inputs = []
        combined_workflow_outputs = []
        combined_workflow_body = []

        for workflow in workflows:
            combined_workflow_inputs.extend(workflow['inputs'])
            combined_workflow_outputs.extend(workflow['outputs'])
            combined_workflow_body.extend(workflow['body'])

        wdl_code += f"workflow {combined_workflow_name} {{\n"
        if combined_workflow_inputs:
            wdl_code += "    input {\n"
            for input_var in combined_workflow_inputs:
                wdl_code += f"        {input_var}\n"
            wdl_code += "    }\n"
        if combined_workflow_outputs:
            wdl_code += "    output {\n"
            for output_var in combined_workflow_outputs:
                wdl_code += f"        {output_var}\n"
            wdl_code += "    }\n"
        
        added_calls = set()
        for element in combined_workflow_body:
            if isinstance(element, WDL.Tree.Call):
                call_id = element.callee_id
                if call_id not in added_calls:
                    input_mappings = []
                    for input_mapping in element.inputs:
                        input_name = input_mapping.name
                        input_expr = input_mapping.value
                        input_mappings.append(f"{input_name} = {input_expr}")

                    wdl_code += f"    call {call_id} {{\n"
                    if input_mappings:
                        wdl_code += "        input:\n"
                        for input_mapping in input_mappings:
                            wdl_code += f"            {input_mapping}\n"
                    wdl_code += "    }\n"
                    added_calls.add(call_id)

        wdl_code += "}\n"

    return wdl_code



def upgrade_wdl(wdl_file_path):
    womtool_jar = 'womtool-85.jar'

    # Check if womtool JAR file exists
    if not os.path.exists(womtool_jar):
        # Download womtool
        subprocess.run(['wget', 'https://github.com/broadinstitute/cromwell/releases/download/85/' + womtool_jar])

    # Upgrade WDL file
    upgrade = subprocess.run(['java', '-jar', womtool_jar, 'upgrade', wdl_file_path, '-r', '1.0'])
    upgrade_output = upgrade.stdout
    upgrade_errors = upgrade.stderr
    print(upgrade_output)
    print(upgrade_errors)

def validate_wdl(wdl_file_path):
    womtool_jar = 'womtool-85.jar'

    # Check if womtool JAR file exists
    if not os.path.exists(womtool_jar):
        # Download womtool
        subprocess.run(['wget', 'https://github.com/broadinstitute/cromwell/releases/download/85/' + womtool_jar])
    
    # Validate WDL file
    validate_process = subprocess.run(['java', '-jar', womtool_jar, 'validate', wdl_file_path], capture_output=True, text=True)
    validate_output = validate_process.stdout
    validate_errors = validate_process.stderr

    print(validate_output)
    print(validate_errors)

def read_task_order(task_order_file):
    task_order = []
    with open(task_order_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                task_name = row[0].strip()
                task_order.append(task_name)
    return task_order
