from common.common import job_saving_folder_path
import os
import pickle
from django import setup
from common.jobposting import JobPosting as PickledJobPosting

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()
from display_jobs.models import JobPosting


def main():
    the_dir = os.path.join(job_saving_folder_path, 'linked_in')
    rv = list()
    posts = JobPosting.objects.all().delete()
    print(1)
    for file in os.listdir(the_dir):
        if not os.path.isfile(os.path.join(the_dir, file)):
            continue
        job = pickle.load(open(os.path.join(the_dir, file), 'rb'))
        rv.append(job)

    for job in rv:
        assert isinstance(job, PickledJobPosting)
        post = JobPosting(
            job_id=job.job_id,
            retrieval_date=job.retrieval_date,
            posted_date=job.posted_date,
            title = job.title,
            applicants=job.applicants,
            workplace_type=job.workplace_type,
            company_type=job.company_type,
            full_time_or_other=job.full_time_or_other,
            description=job.description,
            location=job.location,
            site_scraped_from=job.site_name,
            entry_level=job.entry_level,
            language_of_description=job.language_posted

        )
        post.save()


if __name__ == "__main__":
    main()
