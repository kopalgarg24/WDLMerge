#!/usr/bin/env python3
import os
import WDL
import subprocess
def reconstruct_wdl(tasks, workflows):
    wdl_code = ""

    # Reconstruct tasks
    for task in tasks:
        task_name = task['name']
        task_code = f"task {task_name} {{\n"
        if task['inputs']:
            task_code += "    input {\n"
            for input_var in task['inputs']:
                task_code += f"        {input_var}\n"
            task_code += "    }\n"
        task_code += f"    command {{\n        {task['command']}\n    }}\n"
        if task['outputs']:
            task_code += "    output {\n"
            for output_var in task['outputs']:
                task_code += f"        {output_var}\n"
            task_code += "    }\n"
        task_code += "}\n\n"
        if task['runtime']:
            task_code += "    runtime {\n"
            for key, value in task['runtime'].items():
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
        for element in combined_workflow_body:
            if isinstance(element, WDL.Tree.Call):
                input_mappings = []
                for input_name, input_expr in element.inputs.items():
                    input_mappings.append(f"{input_name} = {input_expr}")

                wdl_code += f"    call {element.callee_id[0]} {{\n"
                if input_mappings:
                    wdl_code += "        input:\n"
                    for input_mapping in input_mappings:
                        wdl_code += f"            {input_mapping}\n"
                wdl_code += "    }\n"

        wdl_code += "}\n"

    return wdl_code


def upgrade_wdl(wdl_file_path):
    womtool_jar = 'womtool-85.jar'

    # Check if womtool JAR file exists
    if not os.path.exists(womtool_jar):
        # Download womtool
        subprocess.run(['wget', 'https://github.com/broadinstitute/cromwell/releases/download/85/' + womtool_jar])
    
    # Validate WDL file
    subprocess.run(['java', '-jar', womtool_jar, 'validate', wdl_file_path])

    # Upgrade WDL file
    subprocess.run(['java', '-jar', womtool_jar, 'upgrade', wdl_file_path, '-r', '1.0'])

    print("WDL file upgraded successfully!")



def validate_wdl(wdl_file_path):
    womtool_jar = 'womtool-85.jar'

    # Check if womtool JAR file exists
    if not os.path.exists(womtool_jar):
        # Download womtool
        subprocess.run(['wget', 'https://github.com/broadinstitute/cromwell/releases/download/85/' + womtool_jar])
    
    # Validate WDL file
    subprocess.run(['java', '-jar', womtool_jar, 'validate', wdl_file_path])