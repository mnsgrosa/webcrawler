from airflow.providers.docker.operators.docker import DockerOperator
from airflow.decorators import dag
import datetime

DOCKER_OPERATOR_ARGS = {
    'mount_tmp_dir': False,
    'image': 'my-crawler-image:latest', 
    'docker_url': 'unix://var/run/docker.sock', 
    'network_mode': 'webcrawler_app_network'
}

@dag(
    dag_id = 'scraper_dag',
    start_date = datetime.datetime(2025, 8, 12),
    catchup = True,
    schedule = '@daily',
    is_paused_upon_creation = False,
    dagrun_timeout = datetime.timedelta(minutes = 10),
)
def scraper_dag():
    DockerOperator(
        task_id='run_playstation_crawler',
        command='python -m scripts.run_playstation_crawler',
        **DOCKER_OPERATOR_ARGS
    )

    DockerOperator(
        task_id = 'run_xbox_crawler',
        command = 'python -m scripts.run_xbox_crawler',
        **DOCKER_OPERATOR_ARGS
    )

    # DockerOperator(
    #     task_id = 'run_steam_crawler',
    #     command = 'python -m scripts.run_steam_crawler',
    #     **DOCKER_OPERATOR_ARGS
    # )

scraper_dag()