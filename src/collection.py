import os
import csv
import yaml
import datetime
import logging
import sys
import time
import getpass
import pandas 
import requests

import toloka.client as toloka
import toloka.client.project.template_builder as tb
from cli_parser import CliParser


######## Parsing CLI, Loading Config #########

arg_parser = CliParser("Barcode Photo Collection")
cli_args = arg_parser()
with open(cli_args.cfg) as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)


############ Setting Constants ###########
PROJECT_NAME = "collection"
    
# reading Auth token from an Environment Variavle or STDIN
# to prevent it's leakage from config or bash history
print(os.environ)
PASSWORD = os.environ.get("TOLOKA_TOKEN", None)
if not PASSWORD:
    PASSWORD = getpass.getpass('Enter your OAuth token: ')

# False - if problems with tasks in toloka-kit still occure
USE_KIT_FOR_TASKS = config["use_kit_for_tasks"]

# PRODUCTION or SANDBOX, SANDBOX is default
ENVIRONMENT = config["environment"]

# N_TASKS = config["projects"][PROJECT_NAME]["n_tasks"]
log_level = config["projects"][PROJECT_NAME].get("log_level","DEBUG")
logging.basicConfig(
    format='[%(levelname)s] %(name)s: %(message)s',
    level=getattr(logging, log_level),
    stream=sys.stdout,
)
OVERLAP = config["projects"][PROJECT_NAME]["overlap"]


################## Subroutines ################

def make_interface():
    image_loader = tb.FileFieldV1(
        data=tb.OutputData("image"),
        label="Barcode photo",
        validation=tb.RequiredConditionV1(),
    )
    # How performers will see the task
    interface = toloka.project.TemplateBuilderViewSpec(
        view=tb.ListViewV1([image_loader]),
        settings={
            'showSubmit': True,
            'showFinish': True,
            'showTimer': True,
            'showReward': True,
            'showTitle': True,
            'showRoute': True,
            'showComplain': True,
            'showMessage': True,
            'showSubmitExit': True,
            'showFullscreen': True,
            'showInstructions': True,
        },
    )
    return interface


def make_project(client):
    interface = make_interface()
    instruction_path = config["projects"][PROJECT_NAME]["instruction_path"]
    with open(instruction_path) as fp:
        instruction = fp.read()
    input_specification = {
        "id": toloka.project.IntegerSpec(required=True, hidden=False)
    }
    output_specification = {"image": toloka.project.FileSpec()}
    project = toloka.Project(
        public_name="Barcode Photo Search",
        public_description="Take a photo of a barcode with its number",
        task_spec=toloka.project.task_spec.TaskSpec(
            input_spec=input_specification,
            output_spec=output_specification,
            view_spec=interface,
        ),
        public_instructions = instruction
    )
    project = client.create_project(project)
    return project.id


def make_pool(project_id: int):
    pool = toloka.Pool(
        project_id=project_id,
        private_name=f"Barcode Photo Search",
        may_contain_adult_content=False,
        will_expire=(
            datetime.datetime.utcnow()
            +
            datetime.timedelta(days=365)
        ),
        reward_per_assignment=0.01, # USD
        auto_accept_solutions=False,
        auto_accept_period_day=14,
        assignment_max_duration_seconds=60*10,
        defaults=toloka.Pool.Defaults(
            default_overlap_for_new_task_suites=1
        )
    )
    pool.set_mixer_config(real_tasks_count=1)
    pool = toloka_client.create_pool(pool)
    return pool.id


def add_tasks(pool_id):
    task_indices = []
    with open(
        config["projects"][PROJECT_NAME]["tasks_path"],
        newline=''
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            task_indices.append(row["INPUT:id"])
    if USE_KIT_FOR_TASKS:
        tasks = [
            toloka.Task(input_values={"id": id}, pool_id=pool_id)
            for id in task_indices
        ]
        toloka_client.create_tasks(tasks, allow_defaults=False)
    else:
        if ENVIRONMENT == "PRODUCTION":
            url = "https://toloka.dev/api/v1/tasks?skip_invalid_items=true"
        else:
            url = "https://sandbox.toloka.dev/api/v1/tasks?skip_invalid_items=true"
        headers = {
          'Authorization': f"OAuth {PASSWORD}",
          'Content-Type': 'application/json'
        }
        tasks = [
            {
                "input_values": {"id": id},
                "pool_id": pool_id,
                "overlap": 1,
            }
            for id in task_indices
        ]
        response = requests.post(url, headers=headers, json=tasks)
        print(response.text)
    print(f'Populated pool with {len(task_indices)} tasks')


if __name__ == "__main__":
    toloka_client = toloka.TolokaClient(PASSWORD, ENVIRONMENT)
    print(toloka_client.get_requester())
    project_id = make_project(toloka_client)
    pool_id = make_pool(project_id)
    add_tasks(pool_id)
