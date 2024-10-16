### User Manual

#### **how to execute scripts:**

1. **Credentials:**
   - **Access:** to execute this script you need configure GitHub token to access this files and download in your repo.

2. **Dependencies:**
   - **Install:** You need install the dependencies in your workflow.
   ```bash
   python -m pip install --upgrade pip
   pip install boto3 click
   ```

3. **Download files in your workflow and usage:**
   - **update_ecs_instance.py:** In your workflow you should put this curl.
   ```
     curl -H "Authorization: token ${{ secrets.MY_GITHUB_TOKEN }}" -L -o get_parameters.py "https://raw.githubusercontent.com/AICodeBase360/deploy_scripts/main/update_ecs_instance.py"
   ```
   - **update_ecs_instance.py:** Invoke the script like that.
   ```
    - name: Execute deploy script
      run: |
        CLUSTER_NAME="${GITHUB_ENVIRONMENT}_ecs_cluster"
        SERVICE_NAME="ops_${GITHUB_ENVIRONMENT}_service"
        IMAGE_URL="docker image url"
        AWS_OPS_DB_USERNAME_ARN='${{ secrets.AWS_OPS_DB_USERNAME_ARN }}'
        AWS_OPS_DB_PASSWORD_ARN='${{ secrets.AWS_OPS_DB_PASSWORD_ARN }}'
        ENV_VARS_JSON=$(cat <<-END
          [
            {"name":"DB_HOST","value":"${{ steps.fetch-params.outputs.DB_HOST }}"},
            {"name":"DB_PORT","value":"5432"},
            {"name":"DB_NAME","value":"${{ steps.fetch-params.outputs.DB_NAME }}"}
          ]
        END
        )

        echo "CLUSTER_NAME: $CLUSTER_NAME"
        echo "SERVICE_NAME: $SERVICE_NAME"
        echo "IMAGE_URL: $IMAGE_URL"
        echo "ENV_VARS_JSON: $ENV_VARS_JSON"

        python update_ecs_inntance.py \
        --cluster "$CLUSTER_NAME" \
        --service "$SERVICE_NAME" \
        --image "$IMAGE_URL" \
        --username-secret-arn "$AWS_OPS_DB_USERNAME_ARN" \
        --password-secret-arn "$AWS_OPS_DB_PASSWORD_ARN" \
        --env-vars "$ENV_VARS_JSON"
   ```
