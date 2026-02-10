import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def publish_data_activity(data: str) -> str:
    # Simulate publishing data (e.g., to MinIO or another service)
    print(f"Publishing data: {data}")
    return f"Data '{data}' published successfully"


@workflow.defn
class DataPublishWorkflow:
    @workflow.run
    async def run(self, data: str) -> str:
        return await workflow.execute_activity(
            publish_data_activity, data, start_to_close_timeout=10
        )


async def main():
    # Connect to Temporal server (assuming it's running via docker-compose)
    client = await Client.connect("localhost:7233")

    # Start worker
    worker = Worker(
        client,
        task_queue="data-publish-queue",
        workflows=[DataPublishWorkflow],
        activities=[publish_data_activity],
    )
    await worker.run()


if __name__ == "__main__":
    # Run worker in background and execute a sample workflow
    asyncio.run(
        asyncio.gather(
            main(),
            # Example: Start a workflow (in a real app, trigger this separately)
            # client.execute_workflow(DataPublishWorkflow.run, "sample data", id="publish-1", task_queue="data-publish-queue")
        )
    )
