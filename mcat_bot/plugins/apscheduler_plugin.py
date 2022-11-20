from wechaty import WechatyPlugin
from typing import List
from quart import Quart
from tabulate import tabulate
from apscheduler.job import Job


def get_jobs_table_format(jobs: List[Job]) -> str:
    series = []
    headers = ['id', 'description', 'args', 'kwargs']
    for job in jobs:
        series.append([
            job.id,
            str(job),
            job.args,
            job.kwargs
        ])
        
    return tabulate(series, headers=headers, tablefmt='grid')

def generate_job_table(jobs: List[Job]) -> str:
    header = "<thead>"
    header += f"<td>id</td>"
    header += f"<td>description</td>"
    header += f"<td>args</td>"
    header += f"<td>kwargs</td></thead>"

    body = "<tbody>"
    for job in jobs:
        row = f"<tr>"
        row += f"<td>{job.id}</td>"
        row += f"<td>{job}</td>"
        row += f"<td>{job.args}</td>"
        row += f"<td>{job.kwargs}</td></tr>"
        body += row
    body += "</tbody>"
    return "<table>" + header + body + "</table>"


class ApSchedulerPlugin(WechatyPlugin):
    async def blueprint(self, app: Quart) -> None:
        
        @app.route("/scheduler")
        def view_all_jobs():
            all_jobs = self.scheduler.get_jobs()
            content = get_jobs_table_format(all_jobs)
            self.logger.info("\n" + content)
            # content = content.replace("\n", "<br>")
            
            content = generate_job_table(all_jobs)
            return content
    
            