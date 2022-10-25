import pickle
import os
from common.jobposting import JobPosting
from langdetect import detect
from copy import deepcopy

def get_saved_jobs(jobs_dir="../jobs/linked_in/"):
    rv = []
    for item in os.listdir(jobs_dir):
        job = pickle.load(open(os.path.join(jobs_dir, item), 'rb'))
        rv.append(job)
    return rv


def requires_phd(jobdescription) -> bool:
    if 'PHD' in jobdescription and 'EQUIVALENT EXPERIENCE' not in jobdescription:
        return True
    return False


def keep_languages(jobs: list, languages_to_keep: iter, verbose=True) -> dict:
    """
    Warning! List mutability

    :param jobs: List mutated
    :param languages_to_keep:
    :return: a dict with the jobs that were removed from jobs
    """
    removed_jobs = dict()
    for n, job in enumerate(jobs):
        assert isinstance(job, JobPosting)
        lang = job.language_posted
        if lang not in removed_jobs.keys() and lang not in languages_to_keep:
            removed_jobs[lang] = list()
        if lang not in languages_to_keep:
            removed_jobs[lang].append(job)

    for lang, _jobs in removed_jobs.items():
        for job in _jobs:
            jobs.remove(job)

    total = 0
    if verbose:
        for lang, _removed_jobs in removed_jobs.items():
            total += len(_removed_jobs)
            print(f"{len(_removed_jobs)} '{lang}' entries.")
    print(f"Total removed due to languages: {total}")

    return removed_jobs


def main():
    removed_jobs = list()
    jobs_description_contain = {
        'AUTOMATION': [],
        'PYTHON': [],
    }
    max_applicatns = 5
    jobs = get_saved_jobs()

    jobs.sort()

    jobs = [j for j in jobs if j.company_name != "Canonical"]

    # Keep only wanted languages on 'jobs' list.
    # WARNING: list mutability
    wanted_languages = 'en,es'.split(",")
    lang_removed_jobs = keep_languages(jobs, wanted_languages)

    #remove graduates
    prevlen = len(jobs)
    for black_word in "GRADUATE,AT LEAST A MSC,UNIVERSITY DEGREE,DEGREE".split(','):
        graduate_jobs = [j for j in jobs if not ('EQUIVALENT EXPERIENCE' not in j.description.upper() and black_word not in j.description.upper())]
        jobs = [j for j in jobs if 'EQUIVALENT EXPERIENCE' not in j.description.upper() and black_word not in j.description.upper()]
    print(f"Dropped {len(jobs) - prevlen} jobs due to graduateness")

    remote_only = [job for job in jobs if job.workplace_type in ("Hy5brid","Remote")]

    python_contains = [job for job in remote_only if 'Python'.upper() in job.description.upper()]
    autom_cotains = [job for job in remote_only if 'automation'.upper() in job.description.upper() and job not in python_contains]

    entry_level_python = [job for job in python_contains if job.entry_level == 'Entry level']
    antientry_level_python = [job for job in python_contains if job.entry_level != 'Entry level']

    entry_level_autom = [job for job in autom_cotains if job.entry_level == 'Entry level']
    antientry_level_autom = [job for job in autom_cotains if job.entry_level != 'Entry level']

    print(2)

if __name__ == "__main__":
    main()