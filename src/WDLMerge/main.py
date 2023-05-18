#!/usr/bin/env python3

import argparse
import sys
import WDL
import os
import subprocess
import csv
#import asyncio
#import nest_asyncio

# Allow nested event loops in Jupyter notebook
#nest_asyncio.apply()

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
        if task_info['parameter_meta']:
            task_code += "    parameter_meta {\n"
            for meta_var, meta_val in task_info['parameter_meta'].items():
                task_code += f"        {meta_var}: {meta_val}\n"
            task_code += "    }\n"
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

        added_calls = []
        for element in combined_workflow_body:
            if isinstance(element, WDL.Tree.Call):
                call_id = element.callee_id

                if element.inputs:
                    input_mappings = []
                    
                    for input_name, input_expr in element.inputs.items():
                        if isinstance(input_expr, WDL.Expr.Get):
                            # Traverse to the actual value of the Get object
                            get_expr = input_expr.expr
                            input_value = get_expr.name
                        else:
                            
                            input_value = input_expr

                        input_mappings.append(f"{input_name} = {input_value}")
                    
                    wdl_code += f"    call {call_id[0]} as {vars(element)['name']} {{\n"
                    if input_mappings:
                        wdl_code += "        input:\n"
                        for input_mapping in input_mappings:
                            wdl_code += f"            {input_mapping}\n"
                    wdl_code += "    }\n"
                    added_calls.append(call_id)
            else:
                #import pdb; pdb.set_trace()
                wdl_code+=f"    {str(element) }"
                wdl_code += "  \n"


        wdl_code += "}\n"

    return wdl_code



def upgrade_wdl(wdl_file_path):
    womtool_jar = 'womtool-85.jar'

    # Check if womtool JAR file exists
    if not os.path.exists(womtool_jar):
        # Download womtool
        subprocess.run(['wget', 'https://github.com/broadinstitute/cromwell/releases/download/85/' + womtool_jar])
    # Upgrade WDL file
    command = 'java -jar ' + womtool_jar + ' upgrade ' + wdl_file_path
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    new_wdl=result.stdout
    if new_wdl == '':
        print('Already up to date.')
    else:
        print("Updated WDL: ", wdl_file_path)
        with open(wdl_file_path, 'w') as file:
            file.write(new_wdl)


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
    print("Validation Result for ", wdl_file_path,":")
    print(validate_output)
    print(validate_errors)


def merge_wdls(WDLs, order=None):
    wdl_files = set(WDLs)  # Convert WDLs to a set
    task_order = order

    task_attributes = {}
    workflow_attributes = []

    for wdl_file in wdl_files:

        document = WDL.load(wdl_file)
        workflows = document.workflow
        tasks = document.tasks

        for task in tasks:
            if task.name in task_attributes:
                print(f"Skipping task with duplicate name: {task.name}")
                continue

            task_info = {
                'inputs': task.inputs or {},
                'command': str(task.command),
                'outputs': task.outputs or {},
                'parameter_meta': task.parameter_meta or {},
                'runtime': task.runtime or {},
            }
            task_attributes[task.name] = task_info

        if workflows:
            workflow_info = {
                'name': workflows.name,
                'inputs': workflows.inputs or {},
                'outputs': workflows.outputs or {},
                'body': workflows.body or [],
            }
            workflow_attributes.append(workflow_info)

    # Generate the WDL statements for calling tasks in the specified order
    if task_order:
        call_statements = []
        for task_name in task_order:
            if task_name in task_attributes:
                task_info = task_attributes[task_name]
                call_inputs = []
                if isinstance(task_info['inputs'], list):  # Check if inputs is a list
                    # Use placeholder names for input names
                    call_inputs = [
                        WDL.Env.Binding(f"input_{i}", WDL.Value.String(f"input_{i}"))
                        for i, _ in enumerate(task_info['inputs'])
                    ]
                else:
                    call_inputs = [
                        WDL.Env.Binding(input_name, WDL.Value.String(input_name))
                        for input_name in task_info['inputs']
                    ]
                call_statements.append(WDL.Call(pos=None, alias=None, callee_id=task_name, inputs=call_inputs))

        # Modify the workflow body to include the call statements in the specified order
        added_calls = set()  # Create a set to store added calls
        for workflow in workflow_attributes:
            workflow['body'] = call_statements
            added_calls.add(tuple(call_statements))  # Convert call_statements to a tuple and add to added_calls set

    reconstructed_wdl = reconstruct_wdl(task_attributes, workflow_attributes)

    #print(reconstructed_wdl)

    return reconstructed_wdl
