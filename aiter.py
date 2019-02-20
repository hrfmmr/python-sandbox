import asyncio
import time

global start

start = time.time()
job_duration = 1
n_jobs = 3
n_workers = 5


async def job(worker_id, n_jobs):
    print(f'start job worker_id:{worker_id}')
    for i in range(1, n_jobs + 1):
        await asyncio.sleep(job_duration)
        yield f'worker_id:{worker_id}', f'job:{i}'


async def run_worker(worker_id, n_jobs):
    print(f'start worker_id:{worker_id}')
    async for ret in job(worker_id, n_jobs):
        print(f'Done job of {ret} in {int(time.time() - start)}sec')


async def run(n_workers, n_jobs):
    coros = [run_worker(i, n_jobs)
             for i in range(1, n_workers + 1)]
    await asyncio.wait(coros)


def main():
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(run(n_workers, n_jobs))
    finally:
        event_loop.close()
    end = time.time()
    assert int(end - start) == n_jobs * job_duration


if __name__ == '__main__':
    main()
