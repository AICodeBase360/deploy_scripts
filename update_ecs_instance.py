import boto3
import click
import json


def get_current_task_definition(client, cluster, service):
    response = client.describe_services(cluster=cluster, services=[service])
    current_task_arn = response["services"][0]["taskDefinition"]

    print("Current task definition ARN:", current_task_arn)
    return client.describe_task_definition(taskDefinition=current_task_arn)


PROD_TASK_ROLE = "production_ecs_task_execution_role"
DEV_TASK_ROLE = "dev_ecs_task_execution_role"


@click.command()
@click.option("--cluster", help="Name of the ECS cluster", required=True)
@click.option("--service", help="Name of the ECS service", required=True)
@click.option("--image", help="Docker image URL for the updated application", required=True)
@click.option("--username-secret-arn", help="Username ARN for the database credentials secret", required=True)
@click.option("--password-secret-arn", help="Password ARN for the database credentials secret", required=True)
@click.option("--target-env", help="Environment (e.g., 'production', 'dev')", required=True)
@click.option("--env-vars", help="JSON string of additional environment variables", required=True)
def deploy(cluster, service, image, username_secret_arn, password_secret_arn, target_env, env_vars):
    client = boto3.client("ecs")

    # Obtener la definición de tarea actual
    print("Fetching current task definition...")
    response = get_current_task_definition(client, cluster, service)
    container_definition = response["taskDefinition"]["containerDefinitions"][0].copy()

    # Actualizar la imagen del contenedor
    container_definition["image"] = image

    # Actualizar variables de entorno
    new_env_vars = json.loads(env_vars)
    container_definition["environment"] = new_env_vars

    # Agregar secretos para las credenciales de la base de datos
    container_definition["secrets"] = [
        {"name": "DB_USERNAME", "valueFrom": username_secret_arn},
        {"name": "DB_PASSWORD", "valueFrom": password_secret_arn}
    ]

    print(f"Updated container image to: {image}")

    # Registrar una nueva definición de tarea
    print("Registering new task definition...")

    # Determinar el rol de ejecución basado en el entorno (producción o desarrollo)
    task_execution_role = PROD_TASK_ROLE if target_env == "production" else DEV_TASK_ROLE

    response = client.register_task_definition(
        family=response["taskDefinition"]["family"],
        volumes=response["taskDefinition"]["volumes"],
        containerDefinitions=[container_definition],
        cpu=response["taskDefinition"]["cpu"],
        memory=response["taskDefinition"]["memory"],
        networkMode=response["taskDefinition"]["networkMode"],
        requiresCompatibilities=response["taskDefinition"]["requiresCompatibilities"],
        executionRoleArn=task_execution_role,
        taskRoleArn=response["taskDefinition"]["taskRoleArn"]
    )

    new_task_arn = response["taskDefinition"]["taskDefinitionArn"]
    print(f"New task definition ARN: {new_task_arn}")

    # Actualizar el servicio con la nueva definición de tarea
    print("Updating ECS service with the new task definition...")
    client.update_service(
        cluster=cluster, service=service, taskDefinition=new_task_arn
    )
    print("Service updated successfully!")


if __name__ == "__main__":
    deploy()
