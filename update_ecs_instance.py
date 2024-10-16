import boto3
import click
import json


def get_current_task_definition(client, cluster, service):
    response = client.describe_services(cluster=cluster, services=[service])
    current_task_arn = response["services"][0]["taskDefinition"]

    print("≠ current_task_arn ≠")
    print(current_task_arn.rsplit(':', 1)[0])

    return client.describe_task_definition(taskDefinition=f"{current_task_arn.rsplit(':', 1)[0]}")


PROD_TASK_ROLE = "production_ecs_task_execution_role"
DEV_TASK_ROLE = "dev_ecs_task_execution_role"


@click.command()
@click.option("--cluster", help="Name of the ECS cluster", required=True)
@click.option("--service", help="Name of the ECS service", required=True)
@click.option("--image", help="Docker image URL for the updated application", required=True)
@click.option("--region", help="AWS region where the ECS tasks are located", required=False, default="us-east-1")
@click.option("--target-env", help="the target environment to update the task instance", required=False)
def deploy(cluster, service, image, region, target_env):
    client = boto3.client("ecs")

    # Fetch the current task definition
    print("Fetching current task definition...")
    response = get_current_task_definition(client, cluster, service)
    container_definition = response["taskDefinition"]["containerDefinitions"][0].copy(
    )
    print(response)
    print(response["taskDefinition"]["containerDefinitions"])

    # Update the container definition with the new image
    container_definition["image"] = image

    print(f"Updated image to: {image}")

    # Register a new task definition
    print("Registering new task definition...")

    task_execution_role = PROD_TASK_ROLE if target_env == "production" else DEV_TASK_ROLE

    if (region == "eu-west-2"):
        task_execution_role = f"{region}_{task_execution_role}"

    print("ECS TASK ROLE", task_execution_role)

    response = client.register_task_definition(
        family=response["taskDefinition"]["family"],
        volumes=response["taskDefinition"]["volumes"],
        containerDefinitions=[container_definition],
        cpu=response["taskDefinition"]["cpu"],
        memory=response["taskDefinition"]["memory"],
        networkMode="awsvpc",
        requiresCompatibilities=["FARGATE"],
        executionRoleArn=task_execution_role,
        taskRoleArn=task_execution_role,
    )
    new_task_arn = response["taskDefinition"]["taskDefinitionArn"]
    print(f"New task definition ARN: {new_task_arn}")

    # Update the service with the new task definition
    print("Updating ECS service with new task definition...")
    client.update_service(
        cluster=cluster, service=service, taskDefinition=new_task_arn,
    )
    print("Service updated!")


if __name__ == "__main__":
    deploy()