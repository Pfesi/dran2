import click
#https://click.palletsprojects.com/en/8.1.x/quickstart/


@click.command()
def initdb():
    click.echo('Initialized the database')

@click.command()
def dropdb():
    click.echo('Dropped the database')

@click.command()
def run():
    print('Running')

@click.group()
def cli():
    pass

cli.add_command(run)
# cli.add_command(initdb)
# cli.add_command(dropdb)
# cli.add_command(run)



if __name__ == '__main__':
    cli()