import argparse
import sys
import WDL
from utils import *
import argparse
import sys
import WDL

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wdl', nargs='+', help='WDL files', required=True)
    parser.add_argument('-o', '--order', help='Task order within the workflow')
    args = parser.parse_args()

    wdl_files = args.wdl
    task_order = args.order.split(',') if args.order else None

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
        for workflow in workflow_attributes:
            workflow['body'] = call_statements
    reconstructed_wdl = reconstruct_wdl(task_attributes, workflow_attributes)

    print(reconstructed_wdl)

if __name__ == "__main__":
    main()
