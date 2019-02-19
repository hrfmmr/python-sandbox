from multiprocessing import Process

import click

from daemonize import start_daemon


@click.group()
def cli():
    pass


@cli.command()
@click.argument('i', type=click.INT)
def start(i):
    start_daemon(i)


@cli.command()
@click.argument('n', type=click.INT)
def run_daemons(n):
    for i in range(n):
        worker = Process(target=start_daemon, args=(i,))
        worker.start()


def main():
    cli()


if __name__ == '__main__':
    main()
