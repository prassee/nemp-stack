import asyncio
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def publish_data_activity(data: str) -> str:
    # Simulate publishing data (e.g., to MinIO or another service in the stack)
    print(f"Publishing data: {data}")
    return f"Data '{data}' published successfully"


@workflow.defn
class DataPublishWorkflow:
    @workflow.run
    async def run(self, data: str) -> str:
        return await workflow.execute_activity(
            publish_data_activity, data, start_to_close_timeout=timedelta(seconds=10)
        )


async def main():
    # Connect to Temporal server (assuming it's running via docker-compose)
    client = await Client.connect("localhost:7233")

    # Start scheduled workflow (runs every 2 minutes)
    await client.start_workflow(
        DataPublishWorkflow.run,
        "scheduled data payload",
        id="data-publish-cron",
        task_queue="data-publish-queue",
        cron_schedule="*/2 * * * *",  # Every 2 minutes
    )

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
    asyncio.run(main())
